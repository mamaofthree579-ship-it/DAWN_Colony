import sys, os, platform, math

# -----------------------------------------------------
# FREECAD AUTO-LOADER
# -----------------------------------------------------

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
            "/usr/lib/freecad-python3/lib",
        ]

    # Try each candidate path
    for p in candidate_paths:
        if os.path.isdir(p):
            sys.path.append(p)
            try:
                import FreeCAD, FreeCADGui
                print(f"✔ FreeCAD loaded from: {p}")
                return FreeCAD
            except Exception:
                pass

    raise ImportError("❌ Could not load FreeCAD. Please install or add the correct path.")

# Load FreeCAD
FreeCAD = load_freecad()
import Part

# -----------------------------------------------------
# GEOMETRY GENERATORS
# -----------------------------------------------------

def generate_spiral_ring(
    inner_radius=5.0,
    thickness=1.2,
    pitch=0.7,
    height=20.0,
    turns=5,
):
    """
    Creates a spiraling cylindrical colony ring-core structure.
    Tunable for Dawn Colony atmospheric lattice models.
    """
    doc = FreeCAD.newDocument("spiral_ring")

    pts = []
    steps = 300

    for i in range(steps):
        t = i / steps
        angle = 2 * math.pi * turns * t
        r = inner_radius + thickness * math.sin(angle * 0.5)
        z = height * t

        x = r * math.cos(angle)
        y = r * math.sin(angle)

        pts.append(FreeCAD.Vector(x, y, z))

    poly = Part.makePolygon(pts)
    wire = Part.Wire(poly)
    solid = wire.makePipeShell([wire], True, True)

    part = doc.addObject("Part::Feature", "SpiralRing")
    part.Shape = solid

    doc.recompute()
    return doc, part


def export_stl(doc, part, output_path="spiral_ring.stl"):
    shape = part.Shape
    shape.exportStl(output_path)
    print(f"✔ STL exported: {output_path}")
    return output_path
