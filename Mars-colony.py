import streamlit as st
import numpy as np
import pandas as pd
import os

# Set layout parameters for the dashboard
st.set_page_config(
    page_title="Dawn Colony Engineering Suite", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("🚀 Dawn Colony — Engineering Control & Parametric CAM Suite")
st.markdown("---")

# ==========================================================
# SIDEBAR CONFIGURATION & CONTROL PARAMETERS
# ==========================================================
st.sidebar.header("📐 Global Architectural Bounds")
R = st.sidebar.slider("Dome Radius (R) in mm", 1000, 5000, 3000, step=100)
shell_thickness = st.sidebar.slider("Shell Thickness (mm)", 20, 200, 60)
nozzle_bead = st.sidebar.slider("Nozzle Bead Width (mm)", 10, 60, 30)
layer_height = st.sidebar.slider("Layer Height (mm)", 5, 30, 15)

st.sidebar.header("🖨️ CAM & Kinematic Inputs")
print_feedrate = st.sidebar.slider("Print Travel Speed (mm/s)", 10, 250, 80)
overlap_pct = st.sidebar.slider("Bead Inter-layer Overlap (%)", 0.0, 0.5, 0.15, step=0.05)
target_rpm = st.sidebar.slider("Extruder Nominal Target Speed (RPM)", 10, 200, 40, step=10)

st.sidebar.header("🌋 Hardware & Processing Bounds")
auger_d = st.sidebar.slider("Auger Outer Diameter (m)", 0.02, 0.15, 0.08, step=0.01)
auger_pitch = st.sidebar.slider("Auger Screw Pitch (m)", 0.01, 0.10, 0.04, step=0.01)
fill_factor = st.sidebar.slider("Extruder Channel Fill Factor", 0.1, 1.0, 0.6, step=0.05)
material_density = st.sidebar.slider("Slurry Bulk Density (kg/m³)", 1000, 2500, 1500, step=50)
vol_efficiency = st.sidebar.slider("Volumetric Efficiency Factor (η)", 0.1, 1.0, 0.7, step=0.05)

# ==========================================================
# INTERFACE NAVIGATION - EXPLICIT CONTAINER UNPACKING
# ==========================================================
tab1, tab2, tab3 = st.tabs([
    "📊 Extruder Physics Engine (Mod 3)", 
    "🌀 System Infrastructure Simulations", 
    "📑 Blueprint Specifications Architecture"
])

# ==========================================================
# TAB 1: MODULE 3 - EXTRUDER PHYSICS ENGINE & CALIBRATION MATRIX
# ==========================================================
with tab1:
    st.header("⚙️ Module 3: Auger Volumetric Transference Matrix Calibration")
    st.markdown("Computes fluid dynamics parameters using explicit geometrical boundaries.")
    
    radius_m = auger_d / 2
    area_m2 = np.pi * (radius_m ** 2)
    pocket_vol_m3 = area_m2 * auger_pitch * fill_factor
    
    st.sidebar.markdown(f"**Pocket Volume Metric:** {pocket_vol_m3:.7f} m³/rev")
    
    rpm_range = np.arange(10, 210, 10)
    csv_rows = []
    
    for current_rpm in rpm_range:
        q_m3 = pocket_vol_m3 * current_rpm * vol_efficiency
        q_l = q_m3 * 1000.0
        mass_kg = q_m3 * material_density
        csv_rows.append({
            "RPM": current_rpm,
            "Q_m3_per_min": round(q_m3, 6),
            "Q_L_per_min": round(q_l, 2),
            "Mass_kg_per_min": round(mass_kg, 2),
            "Note": "theoretical"
        })
        
    df_calibration = pd.DataFrame(csv_rows)
    
    st.subheader("📊 Output Calibration Array Dashboard")
    st.dataframe(df_calibration, use_container_width=True)
    
    csv_buffer = df_calibration.to_csv(index=False)
    st.download_button("💾 Export Calibration Matrix (.CSV)", csv_buffer, "auger_calibration.csv", "text/csv")

# ==========================================================
# TAB 2: SYSTEM INFRASTRUCTURE SIMULATIONS
# ==========================================================
with tab2:
    st.header("📈 Integrated Subsystems Simulation Framework")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🍀 CLSE-03 Life Support Loops")
        algae_m = st.slider("Active Photobioreactor Loop Extensions (meters)", 500, 5000, 2500)
        crew_demand = 48 * 0.9
        algae_yield = algae_m * 0.015
        agri_yield = 12.5 * 0.98
        net_o2 = (algae_yield + agri_yield) - crew_demand
        
        st.metric("Total O₂ Loop Generation", f"{algae_yield+agri_yield:.2f} kg/day")
        st.metric("Net Habitat Loop Balance", f"{net_o2:+.2f} kg/day", delta_color="normal")
        
    with col2:
        st.subheader("🔥 GPEA-06 Lithospheric Thermal Flux")
        bore_depth = st.slider("Geothermal Drill Shaft Depth (meters)", 80, 230, 150)
        crust_gradient = 0.62
        bottom_t = -45.0 + (crust_gradient * bore_depth)
        ext_kw = min(35.0, (bottom_t / 48.0) * 1.28 * 8)
        
        st.metric("Target Bore Base Temperature", f"{bottom_t:.1f} °C")
        st.metric("Active Array Heat Harvesting Capacity", f"{ext_kw:.2f} kW")
        
    with col3:
        st.subheader("📡 PCS-07 Telemetry Atmospheric Attenuation")
        dust_tau = st.slider("Martian Dust Opacity Factor (Tau Bounds)", 0.5, 5.0, 1.2)
        optical_cap = max(0.1, 40.0 * np.exp(-0.4 * dust_tau))
        
        st.metric("Achievable Interplanetary Laser Throughput", f"{optical_cap:.2f} Gbps")
        st.progress(optical_cap / 40.0, text=f"Bandwidth Integrity Percentage: {int((optical_cap/40)*100)}%")

# ==========================================================
# TAB 3: BLUEPRINT SPECIFICATIONS ARCHITECTURE
# ==========================================================
with tab3:
    st.header("🗎 Infrastructure System Specification Matrix Documents")
    
    # Selection mapping to specific text files
    module_files = {
        "MHS-01 Main Habitat Superstructure Architecture": "mhs01.txt",
        "APW-02 Atmospheric Processing & Hydrological Hub": "apw02.txt",
        "CLSE-03 Closed-Loop Biological Life Support": "clse03.txt",
        "SAB-04 Subterranean Agricultural Biosystems Complex": "sab04.txt",
        "AGX-05 Concentric Torus Mycotecture Production Center": "agx05.txt",
        "GPEA-06 Geothermal Planetary Exchanger Grid Array": "gpea06.txt",
        "PCS-07 Planetary Interplanetary Telemetry Backbone": "pcs07.txt"
    }
    
    selected_module = st.selectbox(
        "Select Technical Blueprint Component Spec Sheet", 
        list(module_files.keys())
    )
    
    # Dynamically locate and resolve target blueprint path
    target_filename = module_files[selected_module]
    target_path = os.path.join("blueprints", target_filename)
    
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            blueprint_content = f.read()
        st.text(blueprint_content)
    else:
        st.error(f"Asset File Missing: Please ensure target specification text is saved at '{target_path}'")

# ==========================================================
# FOOTER SYSTEM INTEGRATION
# ==========================================================
st.markdown("---")
st.markdown("🌐 **Dawn Colony CAM Suite** | Engineering Core Infrastructure Repository System")

st.sidebar.markdown("---")
st.sidebar.info("Modular file-loading protocol successfully initiated.")
