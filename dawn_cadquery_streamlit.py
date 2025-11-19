import cadquery as cq
import streamlit as st
import io
import base64
import math
import numpy as np

st.set_page_config(layout="wide")
st.title("Dawn Colony — CadQuery Parametric Generator")

# ---------- Utilities ----------
def export_stl_bytes(solid):
    # returns STL (ASCII) bytes
    sb = io.StringIO()
    solid.val().exportStl(sb)
    return sb.getvalue().encode("utf-8")

def export_step_bytes(solid):
    # Attempt to export STEP binary bytes; fallback to message if not supported
    try:
        b = solid.val().exportStepString()
        if isinstance(b, str):
            b = b.encode("utf-8")
        return b
    except Exception as e:
        return None

def download_button_str(bytes_obj, filename, label):
    b64 = base64.b64encode(bytes_obj).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)

# ---------- Part generators ----------
def gen_airlock(inner_diameter=2.4, length=3.0, flange_thickness=0.06, ring_count=6):
    # Cylindrical airlock chamber with mating flanges & gasket groove
    R = inner_diameter / 2.0
    chamber = cq.Workplane("XY").circle(R + 0.05).extrude(length)  # slightly larger outer shell
    inner = cq.Workplane("XY").circle(R).extrude(length + 0.02).translate((0,0,-0.01))
    shell = chamber.cut(inner)
    # flanges
    flange = (cq.Workplane("XY", origin=(0,0,length/2))
              .circle(R+0.3).circle(R+0.05).extrude(flange_thickness))
    for i in range(ring_count):
        shell = shell.union(flange.translate((0,0, (i - ring_count//2) * (flange_thickness*1.5))))
    # gasket groove (simple)
    groove = (cq.Workplane("XY", origin=(0, 0, length/2))
             .circle(R+0.02).circle(R-0.02).extrude(0.02))
    shell = shell.cut(groove)
    return shell

def gen_habitat_dome(R=3.0, wall=0.08, entrance_cut=1.2, rib_spacing=0.5):
    # Spherical dome shell with internal ribs
    outer = cq.Workplane("XY").sphere(R)
    inner = cq.Workplane("XY").sphere(R - wall)
    dome = outer.cut(inner)
    # cut bottom to make dome (cap)
    dome = dome.cut(cq.Workplane("XY").rect(2*R, 2*R).extrude(R).translate((0,0,-R)))
    # entrance cut
    dome = dome.cut(cq.Workplane("XY").box(entrance_cut, entrance_cut, 2*R).translate((R-entrance_cut/2,0,0)))
    # ribs (simple longitudinal ribs)
    circumference = 2*math.pi*R
    n = max(6, int(circumference / rib_spacing))
    ribs = cq.Workplane("XY")
    for i in range(n):
        ang = i * 360.0/n
        rib = (cq.Workplane("XY").rect(0.02*R, 2*R).extrude(0.06)
               .rotate((0,0,0),(0,0,1), ang)
               .translate((0,0, -R+1.0)))
        ribs = ribs.union(rib)
    dome = dome.union(ribs)
    return dome

def gen_myco_bioreactor(radius=1.0, height=1.6, chamber_count=6, wall_thickness=0.06):
    # Cylindrical reactor with internal radial baffles and nutrient channels
    outer = cq.Workplane("XY").circle(radius + wall_thickness).extrude(height)
    inner = cq.Workplane("XY").circle(radius - 0.02).extrude(height)
    shell = outer.cut(inner)
    # radial baffles
    baffles = cq.Workplane("XY")
    for i in range(chamber_count):
        ang = i*360.0/chamber_count
        baff = (cq.Workplane("XY").rect(2*radius, 0.02).extrude(height*0.9)
                .rotate((0,0,0),(0,0,1), ang))
        baffles = baffles.union(baff)
    shell = shell.union(baffles)
    # porous top cap (patterned)
    top = (cq.Workplane("XY", origin=(0,0,height))
           .circle(radius).workplane(offset=0.02)
           .rarray(0.05, 0.05, int(radius/0.05), int(radius/0.05))
           .pushPoints([(x,y) for x in np.linspace(-radius+0.05,radius-0.05,5)
                        for y in np.linspace(-radius+0.05,radius-0.05,5)])
           .circle(0.02).extrude(0.02))
    shell = shell.union(top)
    return shell

def gen_structured_water_ring(outer_R=6.0, inner_R=4.0, thickness=0.2, pattern_fins=24):
    # Toroidal ring with finned internal structuring for structured water lattice
    ring = cq.Workplane("XY").circle(outer_R).circle(inner_R).extrude(thickness)
    fins = cq.Workplane("XY")
    for i in range(pattern_fins):
        ang = i*360.0/pattern_fins
        fin = (cq.Workplane("XY")
               .box((outer_R-inner_R)/4, 0.05, thickness*0.9)
               .rotate((0,0,0),(0,0,1), ang)
               .translate(((outer_R+inner_R)/2, 0, 0)))
        fins = fins.union(fin)
    return ring.union(fins)

def gen_atmospheric_tower(base_R=0.6, height=8.0, disc_count=12):
    # Tall tower with stacked resonance discs
    body = cq.Workplane("XY").circle(base_R).extrude(height)
    discs = cq.Workplane("XY")
    for i in range(disc_count):
        z = i*(height/disc_count)
        disc = cq.Workplane("XY", origin=(0,0,z)).circle(base_R*1.2 - i*0.02).extrude(0.02)
        discs = discs.union(disc)
    return body.union(discs)

def gen_resonance_gate(outer_R=2.0, ring_count=5, ring_spacing=0.25):
    # Nested rings with tuning nodes
    base = cq.Workplane("XY")
    gate = cq.Workplane("XY")
    for i in range(ring_count):
        r = outer_R - i*ring_spacing
        ring = cq.Workplane("XY").torus(r, 0.05)
        # small tuning nodes
        for j in range(8):
            ang = j*360/8
            node = cq.Workplane("XY").sphere(0.03).translate((r*math.cos(math.radians(ang)), r*math.sin(math.radians(ang)), 0))
            ring = ring.union(node)
        gate = gate.union(ring)
    return gate

def gen_terraform_drone(w=0.8, l=1.2, h=0.25, leg_height=0.2):
    # Simple chassis with hex-frame and mast for seeder
    chassis = cq.Workplane("XY").box(l, w, h)
    hex_pattern = cq.Workplane("XY").polygon(6, 0.6).extrude(0.02).translate((0,0,h/2 + 0.01))
    chassis = chassis.cut(hex_pattern)
    mast = cq.Workplane("XY").circle(0.03).extrude(0.6).translate((l/2 - 0.05, 0, h/2))
    legs = cq.Workplane("XY").box(0.1, 0.02, leg_height).translate((-l/2 + 0.05, -w/2, -leg_height/2))
    legs = legs.union(cq.Workplane("XY").box(0.1, 0.02, leg_height).translate((-l/2 + 0.05, w/2, -leg_height/2)))
    return chassis.union(mast).union(legs)

# ---------- UI ----------
st.sidebar.header("Select model")
model = st.sidebar.selectbox("Model", [
    "Airlock",
    "Habitat Dome",
    "Myco Bioreactor",
    "Structured Water Ring",
    "Atmospheric Tower",
    "Resonance Gate",
    "Terraform Drone",
    "Full Block (combined)"
])

# parameter panels
if model == "Airlock":
    d = st.sidebar.slider("Inner diameter (m)", 1.0, 4.0, 2.4, 0.1)
    L = st.sidebar.slider("Length (m)", 1.0, 6.0, 3.0, 0.1)
    part = gen_airlock(d, L)

elif model == "Habitat Dome":
    R = st.sidebar.slider("Radius (m)", 1.0, 8.0, 3.0, 0.1)
    wall = st.sidebar.slider("Wall thickness (m)", 0.03, 0.2, 0.08, 0.01)
    part = gen_habitat_dome(R, wall)

elif model == "Myco Bioreactor":
    r = st.sidebar.slider("Radius (m)", 0.5, 3.0, 1.0, 0.1)
    h = st.sidebar.slider("Height (m)", 0.6, 3.0, 1.6, 0.1)
    part = gen_myco_bioreactor(r, h)

elif model == "Structured Water Ring":
    oR = st.sidebar.slider("Outer R (m)", 2.0, 10.0, 6.0, 0.1)
    iR = st.sidebar.slider("Inner R (m)", 1.0, oR-0.5, 4.0, 0.1)
    part = gen_structured_water_ring(oR, iR)

elif model == "Atmospheric Tower":
    base = st.sidebar.slider("Base R (m)", 0.2, 2.0, 0.6, 0.05)
    height = st.sidebar.slider("Height (m)", 2.0, 20.0, 8.0, 0.5)
    part = gen_atmospheric_tower(base, height)

elif model == "Resonance Gate":
    oR = st.sidebar.slider("Outer R (m)", 0.5, 4.0, 2.0, 0.1)
    rings = st.sidebar.slider("Ring count", 1, 12, 5)
    part = gen_resonance_gate(oR, rings)

elif model == "Terraform Drone":
    l = st.sidebar.slider("Length (m)", 0.4, 3.0, 1.2, 0.1)
    w = st.sidebar.slider("Width (m)", 0.2, 2.0, 0.8, 0.1)
    part = gen_terraform_drone(w, l)

elif model == "Full Block (combined)":
    # Compose a small scene of modules
    dome = gen_habitat_dome(3.0, 0.08)
    air = gen_airlock(2.4, 3.0).translate((4.0, 0, 0))
    biore = gen_myco_bioreactor(1.0, 1.6).translate((-4.0, 0, 0))
    ring = gen_structured_water_ring(6.0, 4.0).translate((0, 6.5, 0))
    tower = gen_atmospheric_tower(0.5, 6.0).translate((0, -6.5, 0))
    gate = gen_resonance_gate(2.0).translate((0,0,3.0))
    part = dome.union(air).union(biore).union(ring).union(tower).union(gate)

# ---------- render preview (simple) ----------
st.write("Model:", model)
try:
    # generate small mesh preview by exporting STL string and showing its size
    st.write("Generating STL preview...")
    stl_bytes = export_stl_bytes(part)
    st.write(f"STL size: {len(stl_bytes)/1024:.1f} KB")
    # download buttons
    download_button_str(stl_bytes, f"{model.replace(' ','_')}.stl", "Download STL")
    step_bytes = export_step_bytes(part)
    if step_bytes:
        download_button_str(step_bytes, f"{model.replace(' ','_')}.step", "Download STEP")
    else:
        st.write("STEP export not available in this environment.")
except Exception as e:
    st.error(f"Preview/export failed: {e}")
# Attempt to export STEP binary bytes; fallback to message if not supported
try:
    b = solid.val().exportStepString()
    
st.write("---")
st.markdown("Adjust parameters in the sidebar and re-run export. These parts are parametric templates — refine them for manufacturing.")
