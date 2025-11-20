import streamlit as st
from build123d import *
import numpy as np

st.title("Blueprint + Parametric CAD Generator (build123d)")

height = st.number_input("Height", value=20.0)
radius = st.number_input("Radius", value=10.0)

# Build model
with BuildPart() as model:
    Cylinder(radius=radius, height=height)

# Export
step_data = model.part.export_step_string()

# Display confirmation
st.write("3D Model Generated Successfully.")

# Download
st.download_button(
    label="Download STEP File",
    data=step_data,
    file_name="parametric_model.step",
    mime="application/octet-stream",
)
