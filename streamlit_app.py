import streamlit as st
from build123d import *
import numpy as np

st.title("Blueprint + Parametric CAD Generator (Headless Mode)")

height = st.number_input("Height", value=20.0)
radius = st.number_input("Radius", value=10.0)

with BuildPart() as model:
    Cylinder(radius=radius, height=height)

# Export STEP
step_data = model.part.export_step_string()

# Generate 2D SVG projection (top view)
svg_top = model.part.project_to_viewport("top").svg()

# Visualization
st.subheader("Top View (SVG Projection)")
st.image(svg_top)

# Download STEP
st.download_button(
    label="Download STEP File",
    data=step_data,
    file_name="parametric_model.step",
    mime="application/octet-stream",
)
