import math
import csv

# ---------------------------------------------------------
# USER PARAMETERS
# ---------------------------------------------------------

# Dome geometry (meters)
R = 3.0               # dome radius
theta_max = math.radians(70)  # spherical cap angle

# Toolpath parameters
bead_width = 0.03     # m   (30 mm)
overlap = 0.15        # 15% overlap
spacing = bead_width * (1 - overlap)

dphi = math.radians(0.5)   # angular resolution of spiral

# Feedrate
F_mm_min = 1800  # 1800 mm/min = 30 mm/s typical for thick material

# Auger calibration table path
CSV = "auger_calibration.csv"

# Output G-code path
OUTPUT_GCODE = "dawn_dome_spiral.gcode"

# ---------------------------------------------------------
# LOAD AUGER CALIBRATION TABLE
# ---------------------------------------------------------

def load_calibration(path):
    table = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            table.append({
                "rpm": float(row["RPM"]),
                "Q_m3_min": float(row["Q_m3_per_min"])
            })
    return table

cal_table = load_calibration(CALIBRATION_CSV)

# ---------------------------------------------------------
# MAP REQUIRED FLOW -> RPM USING LINEAR INTERPOLATION
# ---------------------------------------------------------

def rpm_for_flow(Q):
    # Q is desired volumetric flow m³/min
    # clamp if outside table
    if Q <= cal_table[0]["Q_m3_min"]:
        return cal_table[0]["rpm"]
    if Q >= cal_table[-1]["Q_m3_min"]:
        return cal_table[-1]["rpm"]

    # linear interpolation
    for i in range(len(cal_table)-1):
        q1 = cal_table[i]["Q_m3_min"]
        q2 = cal_table[i+1]["Q_m3_min"]
        if q1 <= Q <= q2:
            r1 = cal_table[i]["rpm"]
            r2 = cal_table[i+1]["rpm"]
            t = (Q - q1) / (q2 - q1)
            return r1 + t*(r2 - r1)

    return cal_table[-1]["rpm"]

# ---------------------------------------------------------
# GENERATE SPIRAL
# ---------------------------------------------------------

points = []

phi = 0.0
while True:
    r = spacing * phi / (2*math.pi)      # Archimedean spiral in plane
    theta = r / R                        # project to spherical
    if theta > theta_max:
        break

    # spherical to Cartesian
    x = R*math.sin(theta)*math.cos(phi)
    y = R*math.sin(theta)*math.sin(phi)
    z = R*math.cos(theta)

    # convert meters → mm
    points.append((x*1000, y*1000, z*1000))
    phi += dphi

# ---------------------------------------------------------
# GENERATE G-CODE WITH AUGER RPM CONTROL
# ---------------------------------------------------------

with open(OUTPUT_GCODE, "w") as g:
    g.write("; Dawn Colony — Spiral Dome Toolpath\n")
    g.write("G21 ; mm units\n")
    g.write("G90 ; absolute coordinates\n")

    # Move to first point
    x0, y0, z0 = points[0]
    g.write(f"G1 X{x0:.3f} Y{y0:.3f} Z{z0:.3f} F{F_mm_min}\n")

    # Iterate toolpath
    for i in range(1, len(points)):
        x1, y1, z1 = points[i]
        # segment length (mm → m)
        dx = (x1 - points[i-1][0])/1000
        dy = (y1 - points[i-1][1])/1000
        dz = (z1 - points[i-1][2])/1000
        L = math.sqrt(dx*dx + dy*dy + dz*dz)

        # volumetric flow needed
        Q = bead_width * bead_width * L * (F_mm_min/60000)  # m³/min approx

        rpm = rpm_for_flow(Q)

        # Write RPM command (custom M-code)
        g.write(f"M900 R{rpm:.2f} ; set auger rpm\n")
        g.write(f"G1 X{x1:.3f} Y{y1:.3f} Z{z1:.3f} F{F_mm_min}\n")

    g.write("; DONE\n")

print("Generated:", OUTPUT_GCODE)
