import math
import os
import csv
import streamlit as st

uploaded = st.file_uploader("Upload your CSV")

if uploaded:
    import pandas as pd
    df = pd.read_csv(uploaded)
    st.write(df.head())

import sys, os, platform

def load_freecad():
    candidate_paths = []
    system = platform.system()

    if system == "Windows":
        candidate_paths += [
            r"C:\Program Files\FreeCAD 0.21\bin",
            r"C:\Program Files\FreeCAD 0.20\bin",
            r"C:\Program Files\FreeCAD\bin",
        ]

    elif system == "Darwin":
        base = "/Applications/FreeCAD.app/Contents/Resources/lib"
        if os.path.isdir(base):
            for v in os.listdir(base):
                p = os.path.join(base, v, "site-packages")
                if os.path.isdir(p):
                    candidate_paths.append(p)

    elif system == "Linux":
        candidate_paths += [
            "/usr/lib/freecad/lib",
            "/usr/share/freecad/Mod",
        ]

    for p in candidate_paths:
        if os.path.isdir(p):
            sys.path.append(p)
            try:
                import FreeCAD
                return FreeCAD
            except:
                pass

    raise RuntimeError("Could not load FreeCAD")

FreeCAD = load_freecad()
import Part

# ---------------------------------------------------------
# PARAMETERS
# ---------------------------------------------------------

R = 3.0                       # dome radius (meters)
bead_width = 0.03             # 30 mm bead
overlap = 0.15
spacing = bead_width * (1 - overlap)

theta_max = math.radians(70)
dphi = math.radians(0.5)

F_mm_min = 1800  # 30 mm/s

CALIBRATION_CSV = "auger_calibration.csv"
OUTPUT_GCODE = "dawn_dome_spiral.gcode"

# ---------------------------------------------------------
# ENSURE CALIBRATION TABLE EXISTS
# ---------------------------------------------------------

DEFAULT_TABLE = [
    {"RPM": 10, "Q_m3_per_min": 0.00020},
    {"RPM": 20, "Q_m3_per_min": 0.00036},
    {"RPM": 30, "Q_m3_per_min": 0.00050},
    {"RPM": 40, "Q_m3_per_min": 0.00064},
    {"RPM": 50, "Q_m3_per_min": 0.00078},
]

def ensure_calibration_csv():
    if not os.path.exists(CALIBRATION_CSV):
        print("⚠️ No calibration CSV found. Generating default table...")
        with open(CALIBRATION_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["RPM", "Q_m3_per_min"])
            writer.writeheader()
            for row in DEFAULT_TABLE:
                writer.writerow(row)
        print(f"✔ Default calibration saved to {CALIBRATION_CSV}")
    else:
        print(f"✔ Found calibration file: {CALIBRATION_CSV}")

ensure_calibration_csv()

# ---------------------------------------------------------
# LOAD TABLE
# ---------------------------------------------------------

def load_calibration():
    table = []
    with open(CALIBRATION_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            table.append({
                "rpm": float(row["RPM"]),
                "Q": float(row["Q_m3_per_min"])
            })
    print(f"✔ Loaded {len(table)} calibration points.")
    return table

cal_table = load_calibration()

# ---------------------------------------------------------
# MAP FLOW → RPM
# ---------------------------------------------------------

def rpm_for_flow(Q):
    if Q <= cal_table[0]["Q"]:
        return cal_table[0]["rpm"]
    if Q >= cal_table[-1]["Q"]:
        return cal_table[-1]["rpm"]

    for i in range(len(cal_table) - 1):
        q1 = cal_table[i]["Q"]
        q2 = cal_table[i+1]["Q"]
        if q1 <= Q <= q2:
            r1 = cal_table[i]["rpm"]
            r2 = cal_table[i+1]["rpm"]
            t = (Q - q1) / (q2 - q1)
            return r1 + t*(r2 - r1)

    return cal_table[-1]["rpm"]

# ---------------------------------------------------------
# GENERATE SPIRAL POINTS
# ---------------------------------------------------------

print("⟳ Generating dome spiral…")

points = []
phi = 0.0

while True:
    r = spacing * phi / (2*math.pi)
    theta = r / R

    if theta > theta_max:
        break

    x = R*math.sin(theta)*math.cos(phi)
    y = R*math.sin(theta)*math.sin(phi)
    z = R*math.cos(theta)

    points.append((x*1000, y*1000, z*1000))
    phi += dphi

print(f"✔ Generated {len(points)} toolpath points.")

# ---------------------------------------------------------
# WRITE GCODE
# ---------------------------------------------------------

print(f"💾 Writing G-code to {OUTPUT_GCODE}…")

with open(OUTPUT_GCODE, "w") as g:
    g.write("; Dawn Colony – Spiral Dome Toolpath\n")
    g.write("G21 ; mm\nG90 ; absolute\n\n")

    x0,y0,z0 = points[0]
    g.write(f"G1 X{x0:.3f} Y{y0:.3f} Z{z0:.3f} F{F_mm_min}\n")

    for i in range(1, len(points)):
        x1,y1,z1 = points[i]

        dx = (x1 - points[i-1][0])/1000
        dy = (y1 - points[i-1][1])/1000
        dz = (z1 - points[i-1][2])/1000
        L = math.sqrt(dx*dx + dy*dy + dz*dz)

        # approximate volumetric flow per minute
        Q = bead_width * bead_width * L * (F_mm_min/60000)

        rpm = rpm_for_flow(Q)

        g.write(f"M900 R{rpm:.2f}\n")
        g.write(f"G1 X{x1:.3f} Y{y1:.3f} Z{z1:.3f} F{F_mm_min}\n")

print("✔ DONE — Your G-code is ready.")
