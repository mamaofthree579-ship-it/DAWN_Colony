import sys, os, platform

def load_freecad():
    system = platform.system()

    candidate_paths = []

    if system == "Windows":
        candidate_paths += [
            r"C:\Program Files\FreeCAD 0.21\bin",
            r"C:\Program Files\FreeCAD 0.20\bin",
            r"C:\Program Files\FreeCAD\bin",
        ]

    elif system == "Darwin":  # macOS
        base = "/Applications/FreeCAD.app/Contents/Resources/lib"
        if os.path.isdir(base):
            # try all Python minor versions inside the bundle
            for v in os.listdir(base):
                p = os.path.join(base, v, "site-packages")
                if os.path.isdir(p):
                    candidate_paths.append(p)

    elif system == "Linux":
        candidate_paths += [
            "/usr/lib/freecad/lib",
            "/usr/share/freecad/Mod",
            "/usr/lib/freecad-python3/lib",
        ]

    for p in candidate_paths:
        if os.path.isdir(p):
            sys.path.append(p)
            try:
                import FreeCAD, FreeCADGui
                print(f"✔ Loaded FreeCAD from: {p}")
                return FreeCAD
            except Exception as e:
                print(f"Attempted: {p} but failed: {e}")

    raise ImportError("❌ Could not locate FreeCAD installation.")

# Load FreeCAD
FreeCAD = load_freecad()

# ---------------------------------------------------------
# PARAMETERS
# ---------------------------------------------------------

R = 3.0          # meters
shell = 0.06     # m thickness
rib_spacing = 0.5
rib_height = 0.08
rib_width_top = 0.06
rib_width_base = 0.13

theta_start = math.radians(60)
theta_end   = math.radians(120)

doc = App.newDocument("Dawn_Dome")

# ---------------------------------------------------------
# DOME SHELL
# ---------------------------------------------------------

sphere_outer = Part.makeSphere(R)
sphere_inner = Part.makeSphere(R - shell)

# cut hemispherical region
cut_box = Part.makeBox(2*R,2*R,R, App.Vector(-R,-R,R/2))

dome_outer = sphere_outer.common(cut_box)
dome_inner = sphere_inner.common(cut_box)

dome_shell = dome_outer.cut(dome_inner)
shell_obj = doc.addObject("Part::Feature", "DomeShell")
shell_obj.Shape = dome_shell

# ---------------------------------------------------------
# RIB GENERATION
# ---------------------------------------------------------

circumference = 2 * math.pi * R
n_ribs = int(circumference / rib_spacing)

for i in range(n_ribs):
    phi = i * 2*math.pi / n_ribs

    for theta in [theta_start + j*math.radians(10) for j in range(int((theta_end-theta_start)/math.radians(10)))]:
        
        # point on surface
        x = R*math.sin(theta)*math.cos(phi)
        y = R*math.sin(theta)*math.sin(phi)
        z = R*math.cos(theta)

        # normal vector
        nx = x/R; ny = y/R; nz = z/R
        normal = App.Vector(nx,ny,nz)

        # rib profile (trapezoid)
        poly = Part.makePolygon([
            App.Vector(0,0,0),
            App.Vector(rib_width_top, 0, 0),
            App.Vector(rib_width_top, rib_height, 0),
            App.Vector(0, rib_width_base, 0),
            App.Vector(0,0,0)
        ])
        face = Part.Face(poly)
        rib = face.extrude(normal.multiply(0.5))  # half-length extrusion

        rib_obj = doc.addObject("Part::Feature", f"Rib_{i}_{int(theta*1000)}")
        rib_obj.Shape = rib
        rib_obj.Placement.Base = App.Vector(x,y,z)

# ---------------------------------------------------------
# EXPORT
# ---------------------------------------------------------

step_path = "/tmp/dawn_dome.step"
iges_path = "/tmp/dawn_dome.iges"

doc.saveAs("/tmp/dawn_dome.FCStd")
Part.export([shell_obj], step_path)
Part.export([shell_obj], iges_path)

print("Exported:")
print(step_path)
print(iges_path)
