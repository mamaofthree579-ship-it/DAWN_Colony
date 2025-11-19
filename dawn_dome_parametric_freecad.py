import FreeCAD as App
import Part
import math

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
