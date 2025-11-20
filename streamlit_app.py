import streamlit as st
from build123d import *
import numpy as np

st.title("Headless CAD Blueprint Generator")

height = st.number_input("Height", 10.0)
radius = st.number_input("Radius", 5.0)

with BuildPart() as model:
    Cylinder(radius=radius, height=height)

# Export STEP file
step_bytes = model.part.export_step_string()

# Generate SVG projection
svg_top = model.part.project_to_viewport("top").svg()
svg_front = model.part.project_to_viewport("front").svg()
svg_iso = model.part.project_to_viewport("iso").svg()

st.subheader("Blueprint Views")

st.markdown("### Top View")
st.image(svg_top)

st.markdown("### Front View")
st.image(svg_front)

st.markdown("### Isometric View")
st.image(svg_iso)

st.download_button(
    "Download STEP",
    data=step_bytes,
    file_name="model.step",
    mime="model/step"
)
