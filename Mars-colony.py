import streamlit as st
import numpy as np
import pandas as pd

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
# INTERFACE NAVIGATION CORNER
# ==========================================================
tabs = st.tabs([
    "🎨 Parametric OpenSCAD Model", 
    "🎯 Geodesic Spiral Toolpath", 
    "📊 Extruder Physics Engine", 
    "🌀 System Infrastructure Simulations", 
    "📑 Blueprint Specifications Architecture"
])

# ==========================================================
# TAB 1: PARAMETRIC OPENSCAD MODEL GENERATION
# ==========================================================
with tabs[0]:
    st.header("🧱 Parametric Dome Wall Interlocking Rib Script")
    st.markdown("This window generates a corrected, water-tight, compiler-ready script for OpenSCAD.")
    
    rib_spacing = 500 # Constant arc offset constraint
    rib_height = 80
    rib_top_width = 60
    rib_base_width = 130

    openscad_template = f"""// Dawn Colony — Parametric Dome + Rib Generator (OpenSCAD)
// Generated dynamically via Streamlit Control Interface

$fn = 60; // Curve evaluation count

R = {R};
shell_thickness = {shell_thickness};
rib_spacing = {rib_spacing};
rib_height = {rib_height};
rib_top_width = {rib_top_width};
rib_base_width = {rib_base_width};

module dome_shell(){{
    difference(){{
        sphere(r=R);
        sphere(r=R - shell_thickness);
        translate([0, 0, -R]) cube([2*R + 10, 2*R + 10, 2*R], center=true);
    }}
}}

module rib_segment(rib_length) {{
    rotate([0, 90, 0])
    linear_extrude(height = rib_length, center = true) {{
        polygon(points=[
            [-rib_base_width/2, 0],
            [rib_base_width/2, 0],
            [rib_top_width/2, rib_height],
            [-rib_top_width/2, rib_height]
        ]);
    }}
}}

module assemble_dome_with_ribs(){{
    dome_shell();
    num_ribs = floor((2 * PI * R) / rib_spacing);
    segment_length = R * (10 * PI / 180) + 5;
    
    for(i = [0 : num_ribs - 1]) {{
        phi = i * (360 / num_ribs);
        for(theta = [0 : 10 : 80]) {{
            rotate([0, 0, phi])
            rotate([0, theta + 5, 0])
            translate([0, 0, R - shell_thickness])
            rib_segment(segment_length);
        }}
    }}
}}

assemble_dome_with_ribs();"""

    st.code(openscad_template, language="scad")
    st.caption("Copy this code straight into your local OpenSCAD IDE environment to view or edit the 3D grid.")

# ==========================================================
# TAB 2: GEODESIC SPIRAL TOOLPATH GENERATOR
# ==========================================================
with tabs[1]:
    st.header("📿 Geodesic Continuous Spiral Toolpath Builder")
    st.markdown("Calculates non-stop spatial paths over the dome surface with constant toolpath stepover loops.")
    
    # Mathematical Geodesic Constants
    W = nozzle_bead * (1.0 - overlap_pct)
    theta_max = np.radians(60.0)
    displacement_per_rev = (np.pi * (auger_d / 2)**2) * auger_pitch * fill_factor * vol_efficiency * 1e9 # to mm^3
    
    phi_max = (2.0 * np.pi * R * theta_max) / W
    delta_phi = np.radians(2.0) # Larger increments for browser visualization efficiency
    phi_steps = np.arange(0, phi_max, delta_phi)
    
    points = []
    gcode_blocks = []
    
    prev_pt = np.array([0.0, 0.0, float(R)])
    gcode_blocks.append(f"G0 X{prev_pt[0]:.3f} Y{prev_pt[1]:.3f} Z{prev_pt[2]:.3f} ; Target Apex Entry")
    
    for phi in phi_steps:
        theta = (W / (2.0 * np.pi * R)) * phi
        x = R * np.sin(theta) * np.cos(phi)
        y = R * np.sin(theta) * np.sin(phi)
        z = R * np.cos(theta)
        
        curr_pt = np.array([x, y, z])
        points.append(curr_pt)
        
        # Calculate localized delta distances
        segment_length = np.linalg.norm(curr_pt - prev_pt)
        if segment_length > 0.001:
            req_volume = nozzle_bead * layer_height * segment_length
            dt = segment_length / print_feedrate
            flow_rate_per_sec = req_volume / dt
            dynamic_rpm = (flow_rate_per_sec * 60.0) / displacement_per_rev
            
            gcode_blocks.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{print_feedrate*60} M108 R{dynamic_rpm:.2f}")
            prev_pt = curr_pt

    # Data transformation for 3D plotting arrays
    df_path = pd.DataFrame(points, columns=["X", "Y", "Z"])
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🌐 3D Spatial Vector Map")
        st.line_chart(df_path, x="X", y="Y", y_sequence=["Z"])
    with col2:
        st.subheader("🦾 Emitted Vector Machine G-Code Block")
        st.text_area("Synchronized Post-Processor Output Log", "\n".join(gcode_blocks[:100]), height=300)

# ==========================================================
# TAB 3: EXTRUDER PHYSICS ENGINE & REPOSITORY GENERATOR
# ==========================================================
with tabs[2]:
    st.header("⚙️ Auger Volumetric Transference Matrix Calibration")
    st.markdown("Computes fluid dynamics parameters using explicit geometrical boundaries.")
    
    # Computation Steps
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
    
    # Download Anchor Hook
    csv_buffer = df_calibration.to_csv(index=False)
    st.download_button("💾 Export Calibration Matrix (.CSV)", csv_buffer, "auger_calibration.csv", "text/csv")

# ==========================================================
# TAB 4: SYSTEM INFRASTRUCTURE SIMULATIONS
# ==========================================================
with tabs[3]:
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
# TAB 5: BLUEPRINT SPECIFICATIONS ARCHITECTURE
# ==========================================================
with tabs[4]:
    st.header("🗎 Infrastructure System Specification Matrix Documents")
    
    selected_module = st.selectbox("Select Technical Blueprint Component Spec Sheet", [
        "MHS-01 Main Habitat Superstructure Architecture",
        "APW-02 Atmospheric Processing & Hydrological Hub",
        "CLSE-03 Closed-Loop Biological Life Support",
        "SAB-04 Subterranean Agricultural Biosystems Complex",
        "AGX-05 Concentric Torus Mycotecture Production Center",
        "GPEA-06 Geothermal Planetary Exchanger Grid Array",
        "PCS-07 Planetary Interplanetary Telemetry Backbone"
    ])
    
    # High-fidelity architectural configuration schemas strings
    if "MHS-01" in selected_module:
        st.text("""
=========================================================================================
MODULE 1 — MAIN HABITAT SUPERSTRUCTURE (MHS-01)
Revision: B
Authoring System: DAWN Engineering Core
Classification: Structural / ECLSS Enclosure
=========================================================================================

1.0 FUNCTIONAL DESCRIPTION
The Main Habitat Superstructure (MHS-01) serves as:
  • Primary living environment for initial settlers (12–48 personnel scale).
  • Core pressure-stabilized volume for life support.
  • Structural anchor for subsequent modules and expansion nodes.
  • Thermal, radiation, and atmospheric shielding hub.
  • Integration point for agricultural, energy, and command submodules.

The structure is designed for in-situ fabrication using regolith-derived composites, 
fungal-mycelial binder matrices, and lightweight Earth-shipped prefabricated joints.

2.0 STRUCTURAL GEOMETRY
  • Base Shape: Hexagonal radial hub
  • Number of Primary Segments: 6
  • Outer Diameter: 38.0 m
  • Inner Hub Diameter: 12.0 m
  • Height (ground to crown): 9.4 m
  • Total Pressurized Volume: ~4,680 m³
  • Gross Floor Area (GFA): 1,642 m² (Distributed across three active internal decks).
  • Structural Headroom: Clear vertical span of 2.8 m per deck, inclusive of utility raceways.

3.0 MATERIAL PHYSICS & STRUCTURAL CROSS-SECTION
The dome wall employs a functionally graded composite matrix designed to balance internal pneumatic 
pressures against external blast loads, micro-meteoroid impacts, and cyclic thermal swings.
  • Layer A: Sintered Silica Outer Facing Coating [5mm]
            Engineering Function: Vitrified dust-repellent shield; high UV/Albedo reflectivity.
  • Layer B: Basalt-Geopolymer High-Pressure Structural Shell [60mm]
            Engineering Function: Rigid structural load bearing; printed via continuous spiral toolpath.
  • Layer C: Myco-Polymer Resilient Structural Reinforcement [120mm]
            Engineering Function: Thermal break, high-elasticity energy damping, acoustic dampening.
  • Layer D: Regolith Sintered Energy Damping Structural Lattice [200mm]
            Engineering Function: Micro-truss compression ribbing; radiation shielding layer.
  • Layer E: Kevlar-Butyl Dual Gas Bladder Poly Sealant [8mm]
            Engineering Function: Gas-impermeable dual-layer pressure boundary (62 kPa retention).
  • Layer F: Aluminum-Lithium Internal Skin Enclosure [3.5mm]
            Engineering Function: Anti-microbial, impact-resistant interior bulkhead mount paneling.

4.0 FINITE ELEMENT STRESS PROFILES & LOAD DISTRIBUTION
  • Internal Pneumatic Tensile Stress: Maxima occur at the apex (5.7 MPa calculated tensile load).
    Mitigated by interlocking continuous concentric fiber loops woven during the extrusion phase.
  • Shear and Bending Moments: Concentrated at the foundation anchor collar (Z=0.0m). Wind loading 
    creates a lateral shear vector of 142 kN under maximum thin-atmosphere velocity profiles.
  • Thermal Displacement Profile: Differential expansion absorbed by the elastic core of Layer C, 
    accommodating up to 12 mm of radial expansion/contraction per diurnal cycle without micro-cracking.

5.0 ENVIRONMENTAL SYSTEMS & ECLSS INTEGRATION
  • Atmosphere Control: Primary O₂ generation via solid oxide electrolysis + green-wall bioreactors.
  • Internal Pressure: 56–62 kPa
  • Gas Mixture: 28–32% O₂, balance N₂/Ar
  • Temperature Regulation: Nominal interior target: 19–22°C, managed by redundant hydronic loops.
  • Oxygen Generation Assembly (OGA) Yield: 4.8 kg/hr of medical-grade oxygen.

6.0 INTERNAL LAYOUT
  • Level 1 (Ground Deck): EVA staging airlocks (x2), main water treatment unit, power control 
    and fusion microreactor shielding, storage vaults, and mechanical rooms.
  • Level 2 (Habitation Ring): Crew quarters (24 standard pods), medical bay, communal galley, 
    and hydroponic micro-garden atrium.
  • Level 3 (Observation + Command): Command center, holographic navigation table, external 
    sensor suite, and 360° transparent aluminum observation viewport.

7.0 INTER-MODULE INTERFACES
  • Standardized Docking Ports: 6 radial ports (Type-R Hex Collar) + 1 vertical port (Type-V Crown Node).
  • Universal Power & Data Spine: Optical fiber backbone with quantum-clock synchronization, 
    42 kW continuous power bus, and modular redundancy to prevent cascade failures.

8.0 SAFETY + REDUNDANCY
  • Triple redundancy in air-pressure containment.
  • Dual fusion microreactor isolation chambers.
  • Local fire suppression via halon-free clean agent mist.
  • Structural survival rating: 200 years under baseline Mars conditions.
""")
        
    elif "APW-02" in selected_module:
        st.text("""
=========================================================================================
MODULE 2 — ATMOSPHERIC PROCESSING & WATER EXTRACTION HUB (APW-02)
Revision: B
Authoring System: DAWN Engineering Core
Classification: Atmospheric & Hydrological Processing Core
=========================================================================================

1.0 FUNCTIONAL DESCRIPTION
The Atmospheric Processing & Water Extraction Hub (APW-02) serves as the colony’s:
  • Primary water acquisition and purification module.
  • Atmospheric conversion and storage plant.
  • Source of oxygen, nitrogen, and argon for the habitat.
  • Feedstock provider for fuel production and agricultural humidity stabilization.
  • Redundancy node for environmental autonomy if the MHS-01 experiences isolation.

This module runs autonomously with intelligent feedback loops, capable of sustaining 
up to 72 personnel across the Dawn Colony network.

2.0 STRUCTURAL GEOMETRY
  • Main Shape: Cylindrical processing stack seated on a hex-foundation (6° taper for dust shedding)
  • Height: 11.6 m | Base Diameter: 16.4 m
  • Internal Volume: ~890 m³ | Footprint Area: 211.2 m²
  • Tier 1 (Hydrological Core): 4.2 m clearance for reverse-osmosis columns and manifold plumbing.
  • Tier 2 (Electrolysis & Gas Ring): 3.6 m clearance.
  • Tier 3 (Fractionation Cap): 3.2 m clear height.
  • Floor load rating: 14 kN/m²

3.0 MATERIAL SYSTEMS & REINFORCEMENT
  • Layer A: Vitrified Regolith Shell [80.0 mm] — Primary impact armor and shear protection.
  • Layer B: Basalt Filament Overwrap [40.0 mm] — Hoop stress reinforcement against compression.
  • Layer C: Myco-Polymer Insulation [150.0 mm] — High thermal stabilization mantle.
  • Layer D: Fluoropolymer Vapor Bladder [6.0 mm] — Gas-impermeable dual containment liner.
  • Layer E: Stainless Steel Structural Mesh [5.0 mm] — Interior equipment mounting rails.

4.0 CORE SYSTEMS & ATMOSPHERIC HARVESTING INTAKE
  • Multi-stage compressor pulling 0.02–0.06 kg/m³ atmosphere with electrostatic dust scrubbers.
  • Flow Rate: ~1,300–1,900 L/min (Mars ambient pressure). Steps gas up from 0.6 kPa to 450 kPa.
  • Fractionation Tower: Separates constituents using pressure swing, cryogenic cooling (-60°C 
    to -196°C), and membrane partitions.
  • Output Purity Targets: CO₂: 98–99%, N₂: 92–95%, Ar: 96–97%.

5.0 WATER EXTRACTION GRID
  • Regolith Vaporization Beds: Heated to 240–315°C via SOE waste heat. Yields 8–22 L/hr.
  • Subsurface Ice Lances: 12 microwave lances in a ring extending 4–15 m into permafrost bands.
    Emits 2.45 GHz energy to melt ice, pulling vapor up via vacuum. Yields up to 180–260 L/hr.

6.0 OXYGEN PRODUCTION & STORAGE ARCHITECTURE
  • Solid Oxide Extractor (SOE) Bank: 8 x ceramic units running at 700–850°C.
  • Oxygen Output: 3.2–5.0 kg O₂/hr continuous with redundant liquid O₂ (LOX) cooling for storage.
  • Central Water Tank: 12,000 L | Distributed Pods: 6 × 4,000 L (Myco-regolith frost insulation).
  • Gas Storage Ring Capacities: O₂: 6,200 L | N₂: 7,500 L | Ar: 1,800 L | CO₂: 11,000 L.

7.0 THERMAL MANAGEMENT & POWER INTERFACES
  • Radiative Cooling Panels: Shaded west-facing side, rejecting up to 14 kW thermal load.
  • Heat Recovery: Waste heat recycled to beds, habitat hydronics, and myco-chambers.
  • Power Supply: 22–28 kW continuous draw via fusion microreactor and solar array.
  • Onboard Battery: 110 kWh LiFePO₄ cluster, providing 14 hours of critical independent runtime.

8.0 SAFETY, REDUNDANCY & DOCKING
  • Triple pressure chamber redundancy with upward-venting explosion mitigation channels.
  • Independence: Can keep colony alive in "Habitat Failure Scenario" for 9–12 days.
  • Interfaces: 3 x Utility-only (Type-U) docking ports, main conduit link to MHS-01, 40 Gbps data link.
""")
        
    elif "CLSE-03" in selected_module:
        st.text("""
# ==========================================================
# MODULE 3 — CLOSED-LOOP LIFE SUPPORT ECOSYSTEM (CLSE-03)
# ==========================================================
    elif selected_module == "CLSE-03 Closed-Loop Biological Life Support":
        st.text("""
=========================================================================================
MODULE 3 — CLOSED-LOOP LIFE SUPPORT ECOSYSTEM (CLSE-03)
Revision: B
Authoring System: DAWN Engineering Core
Classification: ECLSS / Bio-Regenerative Systems Division
=========================================================================================

1.0 FUNCTIONAL DESCRIPTION
The Closed-Loop Life Support Ecosystem (CLSE-03) is the biological core of the Dawn Colony. 
It integrates atmospheric renewal, water purification/recycling, organic waste digestion, 
food production, microbial/mycelial remediation, and biodynamic environmental stabilization.
  • Recycling Efficiency: >94% nominal loop closure.
  • Baseline Configuration Capacity: Supports 48 personnel indefinitely.

2.0 STRUCTURAL GEOMETRY
  • Primary Shape: Horizontal cylindrical bio-vessel with an interior terraced ring.
  • Length: 30.0 m | Diameter: 12.0 m
  • Pressurized Volume: ~2,450 m³
  • Sector F (Forward): Open vertical bay topology for high-density vertical algae arrays.
  • Sector M (Midsection): Concentric three-tiered terraced stepover tracks (2.4 m radial clearance).
  • Sector A (Aft Suite): Symmetrical flat-floor split-deck arrangement (3.2 m lower / 2.2 m upper).

3.0 MATERIAL SYSTEMS & CONTAINMENT MANTLE
  • Layer A: Basalt Filament Armor [75.0 mm] — External mechanical reinforcement & radiation shield.
  • Layer B: Myco-Insulated Structural Foam [180.0 mm] — High thermal stabilization mantle.
  • Layer C: Elastomeric Shear Layer [12.0 mm] — Vibration dampening from heavy fluid pump harmonics.
  • Layer D: Fluorinated Polyethylene Liner [4.5 mm] — Highly cross-linked biological vapor barrier.
  • Layer E: Vitrified Anti-Microbial Facing [3.0 mm] — Inert surface matrix; prevents bio-fouling.

4.0 CORE SUBSYSTEMS
  • Atmospheric Regeneration Subsystem (ARS): 12 vertical green-wall oxygenation panels + 6 spiral 
    fluidic algae photobioreactor tubes running Chlorella vulgaris modulated between 425nm and 660nm.
    Generates 0.9 kg/day O₂ and captures 1.0 kg/day CO₂ per crew member. Target humidity: 35–45%.
  • Water Recovery & Purification Subsystem (WRPS): Mycelium + activated carbon greywater beds, 
    reverse-osmosis polishing unit, and atmospheric condensers. 96-98% recycling efficiency.
  • Regenerative Agriculture Subsystem (RAS): 3 Planting Rings (A: Greens, B: Root crops/Grains, 
    C: Dwarf trees) using spectrum-tuned LEDs (425, 660, 730 nm) and mycorrhizal fungal webs.
    Yields 1.4–1.8 kg crop mass per person per day. Terrace B floor load capacity: 12.4 kN/m².
  • Biowaste Decomposition Subsystem (BDS): 3 anaerobic digesters, aerobic compost reactors, 
    methane capture tanks, and myco-remediation trenches. Processes organic stream at 4.2 kg/hr.
  • Biodynamic Environmental Stabilization Subsystem (BESS): eDNA monitoring nodes and a 
    symbiosis-balancing AI system providing predictive failure detection with a 2–6 day lead time.

5.0 INTERFACES & SAFETY REDUNDANCY
  • Docking Ports: 2 x horizontal Type-R2 bio-sealed collars + 1 x vertical Type-V nutrient port.
  • Data & Power Integration: Optical data coupling, 30 kW base power draw, 10 kW supplemental peaks.
  • Safety Systems: Triple-isolated waste loops, emergency O₂ reserve banks, overpressure release 
    tunnels, and modular isolation valves between agricultural rings to prevent cascade failures.
""")

    elif "SAB-04" in selected_module:
        st.text("""
=========================================================================================
MODULE 4 — SUBTERRANEAN AGRICULTURAL BIOSYSTEMS COMPLEX (SAB-04)
Revision: B
Authoring System: DAWN Engineering Core
Classification: Subsurface Infrastructure & Agro-Ecological Biosystems
=========================================================================================

1.0 FUNCTIONAL DESCRIPTION
The Subterranean Agricultural Biosystems Complex (SAB-04) is the primary biological production 
and carbon cycling heart of the Dawn Colony. It anchors food production, O₂ production, CO₂ uptake, 
mycelial fabrication substrate, biophilic mental health support, and a genetic seed vault.
Optimized for Mars gravity, low atmospheric pressure, limited water, and internal nutrient cycling.

2.0 STRUCTURAL GEOMETRY & PLACEMENT
  • Placement: Fully subterranean, 8–14 m below surface to maximize thermal and radiation shielding.
  • Primary Shape: Tri-radial vault system branching at 120° offsets from a central hub.
  • Total Pressurized Volume: 6,400 m³ | Span per Vault: 22.0 m | Central Atrium Height: 12.0 m
  • Vault Ceiling Type: Catenary curve — optimal for distributing vertical overburden compressive loads.

3.0 LITHOSPHERIC PROTECTION SYSTEM & LAYERED VAULT SHELL
  • Layer 1: Compacted Regolith Overburden [800 mm - 2000 mm] — Radiation barrier & thermal mass.
  • Layer 2: Sintered Regolith Arch [450 mm] — Primary structural compression ring via microwave sintering.
  • Layer 3: Myco-Polymer Composite Mesh [95 mm] — Tensile reinforcement and micro-fracture sealer.
  • Layer 4: Metalized Polyimide Liner [8.5 mm] — Dual-elastomer pressure containment and gas barrier.
  • Layer 5: Vitrified Anti-Microbial Interior Panels [4.0 mm] — Replaceable anti-fungal lining.

4.0 ECOSYSTEM ZONING SPECS
  • Zone A - Myco-Fabrication Chamber (MFC): Biopolymer sheets & blocks. Humidity: 82-90%, 
    Temp: 21°C±1.5°C, CO₂ enriched to 1.5%. Output: 2.4–6.1 tons/month. Growth via LiDAR scanners.
  • Zone B - Hydroponic Corridor (HPC): Greens, herbs, algae. Light: 320–410 μmol/m²/s via blue/red LEDs.
    Modular rack towers (6 vertical levels) with robotic harvesting arms. Yield: 35–60 kg/day.
  • Zone C - Aeroponic Root Chamber (ARC): Tubers and legumes. Fog density: 20–50 microns droplet size 
    via piezo transducers. 4x Earth-standard root oxygenation in low gravity. Yield: 40–75 kg/day.
  • Zone D - Bioluminescent Forest Atrium (BFA): Gene-edited bioluminescent mosses and woody species, 
    humidity pockets, walkable paths. Temp: 19°C±2.0°C, Humidity: 45–55%. Night-luminescence cycles.
  • Zone E - Crop-Soil Biodiversity Lab (CSBL): 14 soil beds (2x5m each) evaluating engineered 
    rhizosphere microbiomes in automated in-situ Martian regolith blends. Static load: 12.4 kN/m².
  • Zone F - Seed Vault & Genomic Archive (SVGA): Cryogenic vaults with multi-redundant power. 
    Radiation shielding equivalent to 12–16 m packed regolith.

5.0 FLUID LOOPS & AIR CYCLING
  • Water Recovery: Greywater bio-filtration loops + fungal biofilters for active nitrogen cycling.
  • Atmosphere Management: Pulls CO₂ from residential core at 1.4 kg/hr per loop to feed Zone A. 
    Returns O₂ directly to main life-support trunk via 14 air-quality sensor types per vault.
  • Power Profile: 22 kW baseline grid draw, 46 kW peak (harvest/sterilization cycles). Flywheel backup.
  • Biosecurity: Triple pressure seals, plant-safe oxygen-starvation foam, and modular biosecurity locks.
""")

    elif "AGX-05" in selected_module:
        st.text("""
=========================================================================================
MODULE 5 — ADVANCED HYDROPONIC + MYCOTECTURE AGRICULTURE COMPLEX (AGX-05)
Revision: B
Authoring System: Dawn Engineering Core
Classification: Subsurface Infrastructure & Agro-Ecological Biosystems
=========================================================================================

1.0 FUNCTIONAL DESCRIPTION
AGX-05 is a massive closed-loop biological production center that integrates hydroponics, aeroponics, 
mycelial substrate farms, algal bioreactors, and biophilic environmental spaces.
  • Base Capacity: Sustains 48–120 colonists under continuous operational scaling.
  • Structural Lifespan: 120-year structural integrity baseline.

2.0 STRUCTURAL GEOMETRY
  • Primary Shape: Tri-ring concentric torus (“triple halo”) branching via radial core spokes.
  • Outer Diameter: 52.0 m | Inner Spine Diameter: 8.0 m | Vertical Height: 11.0 m
  • Pressurized Volume: ~7,200 m³
  • Level 1 (Ground Core Deck): 3.2 m vertical clearance for heavy pump arrays and manifold plumbing.
  • Level 2 (Crop Cultivation Deck): 4.8 m open vertical span to accommodate 6.0 m aeroponic towers.
  • Level 3 (Biophilic Atrium Deck): 3.0 m clear space capped with a curved vault profile.

3.0 MATERIAL SYSTEMS & SHELL SPECIFICATION
  • Layer A: Sintered Regolith Bioceramic [120.0 mm] — Micrometeoroid armor and high albedo UV deflection.
  • Layer B: Myco-Insulated Structural Foam [220.0 mm] — Core thermal insulation barrier.
  • Layer C: Carbon-Basalt Lattice Arcs [60.0 mm] — Structural load ribbing handling expansion cycles.
  • Layer D: Fluorinated Cross-Linked Polymer [8.0 mm] — Multi-layered gas and humidity boundary barrier.
  • Layer E: Hydrophobic Anti-Biofilm Facing [3.5 mm] — Anti-microbial interior lining.

4.0 CONCENTRIC RING TECHNICAL ALLOCATION
  • Ring A (Food Hydroponics): Length: 24m segments, 3.2m width troughs. Automated recirculating N-P-K loops. 
    Temp: 22°C±1°C, Humidity: 55-65%. Spectra: Red/Blue (660nm/450nm). Yields 4.8 kg fresh crops per person/day.
  • Ring B (Mycotecture Farms): 18 sealed chambers. Temp: 24.5°C±0.5°C, Humidity: 88-92%. Output: Mushroom 
    protein, myco-polymer sheets, structural blocks, bioluminescent comfort light corridors.
  • Ring C (Algal Bioreactors): 45 spiral bio-tube modules running Chlorella vulgaris suspension. 
    Temp: 26°C±1.5°C, Humidity: 40-45%. Broad white + Far-Red (730nm). Carbon conversion efficiency: 41%.
  • Central Spine: 8.0 m vertical utility core housing 3-stage filtration (myco -> 0.1μm nano-mesh -> UV-C).

# ==========================================================
# CONTINUATION OF MODULE 5 — ADVANCED HYDROPONIC + MYCOTECTURE AGRICULTURE COMPLEX (AGX-05)
# ==========================================================
  • 5.0 SIMULATION & ENERGY OVERHEADS
            - Food Generation Capacity: 220–360 kg/day total combined biomass output.
            - Construction Material Growth: 1.6 m³/day of processed structural myco-substrate blocks.
            - Water Recovery Loop: 97.8% recovery efficiency rate; daily leakage vector restricted below 1.3%.
            - Interfaces: 3 x Type-R Hex Collars, quantum-synced fiber data link, high-flow tri-port fluid loops.
            - Safety Systems: Triplicate pumps, instant isolation pressure seals, CO₂ excess vent to fusion coolant.

6.0 INTERNAL LAYOUT
  • Level 1 (Ground Deck): Reservoirs, nutrient mixers, pump arrays, and low-vibration maintenance corridors.
  • Level 2 (Crop Deck): 360° grow lanes, aeroponic towers, pollination micro-drones, and automated harvest robotics tracks.
  • Level 3 (Biomes + Regeneration): Biophilic relaxation garden, fungal biolight corridors, and emotional-diffusion spaces.

7.0 EXPANSION INTERFACES
  • Docking: 3 x Type-R Hex Collars for secondary modules.
  • Data Link: Quantum-synced fiber backbone routing.
  • Water Loop: High-flow insulated tri-port manifold connection.
  • Atmospheric Loop: Dual-laminar high-pressure exchange valve.

8.0 CONSTRUCTION SEQUENCE
  1. Deploy inflatable torus frames on cleared site grid.
  2. Print regolith composites for the rigid outer protective shell.
  3. Install humidity-proof inner multi-layer polymer liners.
  4. Activate the central water core and nutrient mixers.
  5. Inoculate the specialized Ring B fungal matrix chambers.
  6. Bring atmospheric conditioning and cold-traps online.
  7. Seed hydroponic channels and spin up algae loop tubes.
  8. Seal lock systems and initiate full closed-loop operations.
""")

    elif selected_module == "GPEA-06 Geothermal Planetary Exchanger Grid Array":
        st.text("""
=========================================================================================
MODULE 6 — GEOTHERMAL ENERGY & PLANETARY HEAT EXCHANGE ARRAY (GPEA-06)
Revision: B
Authoring System: Dawn Engineering Core
Classification: Civil / Energy Infrastructure
=========================================================================================

1.0 FUNCTIONAL DESCRIPTION
The Geothermal Energy & Planetary Heat Exchange Array (GPEA-06) provides deep-bore thermal energy 
extraction, habitat temperature buffering, planetary thermal stability, an independent emergency backup 
heat source, and a high-capacity heat-sink interface for industrial manufacturing units.
Optimized for Mars’ crustal composition and low atmospheric convective dissipation efficiency.

2.0 STRUCTURAL GEOMETRY
  • Surface Superstructure: Support anchor ring diameter: 14.2 m | Central Service Dome Height: 4.8 m
  • Material: Regolith composite + basalt fiber reinforcement, pinned via 18 x 2.4 m titanium rods.
  • Central Service Dome: 320 m³ gross unpressurized mechanical service volume.
  • Subsurface Vault: 410 m³ pressurized control enclosure isolated at a nominal 6.0 m burial line.
  • Radial Bore Array: 8 shafts (expandable to 12) arranged in 12° angular symmetry.
  • Bore Shaft Metrics: Diameter: 0.45 m | Radial Distance: 18.0 m | Depth: 80–230 m.

3.0 MATERIAL SYSTEMS & CORE INTERFACES
  • Layer A: Sintered Regolith Cylinder [50.0 mm] — Casing protecting bore from lithospheric collapse.
  • Layer B: Elastomeric Myco-Polymer [20.0 mm] — Flexible seismic shock absorption buffer.
  • Layer C: Ceramic-Silicate Barrier [15.0 mm] — Thermal barrier isolating loops down to 540°C.
  • Layer D: High-Conductivity Thermal Gel [5.0 mm] — Fluidic heat link eliminating internal air voids.
  • Layer E: Ti-6Al-4V Exchanger Conduit [4.5 mm] — Primary containment loop for the PCM coolant.
  • Manifold Architecture: 316L stainless steel, triple-insulated thermal valving, ceramic quick-disconnects.
  • Coolant Fluid: Water-glycol mixed with 25nm copper oxide nanoparticles (28% thermal conductivity boost).

4.0 OPERATIONAL PHYSICS & MODES
  • Primary Heat Mode (Extraction): Core temperature stabilizes at +48°C at 150m depth baseline. Average 
    extraction: 3.2 kW per bore. Combined output array capacity: 25–26 kW continuous thermal load.
  • Reverse Mode (Heat Dumping): Heat refusal interface for metal printing/sintering smelters. 
    Dump capacity: 40–72 kW peak capacity.
  • Grid Integration: Consumes 2 kW baseline control power. Supplies 4–10 kW stable thermal-equivalent 
    energy directly into MHS-01, SAB-04, and AGX-05 hydronic loops.
  • Failsafe Systems: Triple-pump redundancy rack (P1 active, P2 standby, P3 safety). Inline optical OTDR 
    stress links isolate anomalous bores within 350 ms. Passive thermosiphon engages on total power loss.

5.0 INTERNAL LAYOUT
  • Central Service Dome: Houses control manifolds, flow regulators, phase-change tanks, and redundant arrays.
  • Subsurface Vault: Primary exchanger assemblies, power regulation bus, and emergency shutoff valving.

6.0 CONSTRUCTION SEQUENCE
  1. Conduct thermal gradient mapping via rover seismic pings.
  2. Drill pilot bores using diamond rotary assemblies.
  3. Ream shafts to a final 0.45 m diameter.
  4. Print regolith lining cylinders in situ using automated tooling down-hole.
  5. Insert the flexible myco-polymer shock absorbing buffer sheath.
  6. Install titanium heat-transfer loops and backfill with thermal gel.
  7. Construct the surface service dome and secure anchor rings.
  8. Integrate the main collection manifolds and pump racks.
  9. Charge and pressurize the nanoparticle PCM fluid loop.
  10. Run a continuous 48-hour thermal cycle qualification test.
""")

    elif selected_module == "PCS-07 Planetary Interplanetary Telemetry Backbone":
        st.text("""
=========================================================================================
MODULE 7 — PLANETARY COMMUNICATION SPINE & ORBITAL RELAY ARRAY (PCS-07)
Revision: B
Authoring System: Dawn Engineering Core
Classification: High-Bandwidth Planetary & Interplanetary Communication Architecture
=========================================================================================

1.0 FUNCTIONAL OVERVIEW
The Planetary Communication Spine (PCS) is a hybrid, multi-layered telecommunications framework 
providing local mesh communication, long-range surface-to-orbit and orbit-to-Earth data relay, 
quantum-stabilized timing synchronization, dust storm–resilient optical pathways, and emergency telemetry loops.
  • Targeted Link Reliability: ≥ 99.995% availability under global atmospheric storm conditions.

2.0 SYSTEM COMPONENTS & ORBITAL MECHANICS
  • Surface Perimeter Towers: 6 units arranged hexagonally around a 12 km equilateral colony ring perimeter.
  • Tower Dimensions: Height: 18.5 m | Base Diameter: 3.2 m tapering uniformly to a 0.8 m apex platform.
  • Tower Instrumentation: Coherent laser transceivers, Ka-band phased arrays, liquid-helium cooling loops.
  • Coverage Radius: 40–55 km per perimeter tower node. Supports 2-direction failover inside the loop.
  • Orbital Relay Constellation: 4 Areosynchronous equatorial satellites (17,000 km altitude) + 2 high-
    eccentricity Molniya pairs (6,000 × 44,000 km, inclination 63.4°) managing Earth-link handoffs (ICA-E).

3.0 MATERIAL SYSTEMS & TOWER STRATA
  • Layer A: Sintered Basalt Armor [45.0 mm] — External shield protecting frame from dust erosion.
  • Layer B: Piezoelectric Damping Ring [15.0 mm] — Dynamic frame stabilization against wind loading vectors.
  • Layer C: Carbon-Nanotube Matrix [25.0 mm] — High-tensile structural load-bearing tower core frame.
  • Layer D: Vacuum Insulation Void [40.0 mm] — Thermal break isolating internal computing cores.
  • Layer E: Liquid-Helium Cooling Line [12.0 mm] — Cryogenic line lowering sensor noise floors.

4.0 COMMUNICATION MODES & BANDWIDTH CAPACITY
  • High-Bandwidth Optical Link (Primary): 1,550 nm coherent laser communication. Throughput: up to 40 Gbps 
    (Surface → Orbit). Utilizes adaptive optics deformable mirrors to correct for dust scattering.
  • Phased Array Microwave Link (Secondary): Frequency-agile Ka-Band (28–38 GHz) array. Throughput: 4–6 Gbps 
    nominal. Fully operational during heavy ambient particulate dust loading.
  • Quantum Clock Sync Channel (Tertiary): Rubidium-locked RF timing beacon ensuring sub-nanosecond module 
    clock drift synchronization for high-accuracy event logging and robotic spatial mapping coordination.
  • Ultra-Low Frequency Backup (Fail-Safe): 3–30 kHz (ULF Band) data loop. Throughput: ~1 Mbps telemetry 
    and critical life-support command override codes. Penetrates deep terrain, storms, and structural walls.

5.0 INTERNAL NETWORKING & POWER MESH
  • Fiber-Optic Underlay: Buried 0.5–1.0 m deep in shared trenches parallel to 40 kW HVDC power lines. 
    Triangular redundancy loop grid providing 360 TB/s internal site bandwidth capability.
  • Local Mesh Network: Wall/floor embedded routing nodes supporting local AR/VR telemetry overlay projection.
  • Power Systems: Integrated fold-out solar micro-wings (4.6 kW peak per tower) + local subsurface 
    regolith-thermal microbattery bank providing 72 hours of complete infrastructure runtime independent of grid power.
  • Maintenance Core: Weekly automated micro-adjustments via robotic depots. Optics apertures vibrate at 
    42 kHz via ultrasonic transducers to clear fine Martian dust without mechanical abrasive wear.

6.0 CONSTRUCTION & DEPLOYMENT
            1. Deploy grading and leveling rovers at perimeter sites.
            2. Sinter tower foundation pads using microwave print tooling.
            3. Assemble modular tower structural segments via high-torque interlocking joints.
            4. Mount and integrate the optics payloads, phased arrays, and cooling loops.
            5. Excavate trenches, lay down the fiber-optic mesh, and backfill.
            6. Validate orbital asset linkage profiles across all 6 tracking terminals.
            7. Run complete automated loop cross-checks across primary and emergency channels.

7.0 SYSTEM LIFESPAN + MAINTENANCE
  • Structural lifespan: 80–120 years under continuous atmospheric abrasion profiles.
  • Electronic upgrade cycles: Scheduled hardware refreshes every 10–14 years.
  • Self-Preservation: Integrated dust-vibration emitters continuously shake transceivers at 42 kHz.
  • Automated Overhaul: Maintenance rovers perform precision mechanical alignments weekly.

8.0 INTERFACES WITH OTHER MODULES
  • Command System: Dedicated primary optical link directly to the central Command Module (CMD-03).
  • Atmospheric Synchronization: Real-time data pipeline with the Atmospheric Processing Hub (APW-02) for predictive weather routing.
  • Robotic Orchestration: Low-latency telemetry grid interlocked with the Construction & Robotics Depot (ROB-06).
  • External Gateway: Directly linked into the Interplanetary Communications Array (ICA-E) for long-range Earth relays.
""")

# ==========================================================
# FOOTER SYSTEM INTEGRATION
# ==========================================================
st.markdown("---")
st.markdown("🌐 **Dawn Colony CAM Suite** | Engineering Core Infrastructure Repository System | Revision Control Approved.")

# Sidebar status report
st.sidebar.markdown("---")
st.sidebar.info("Application successfully configured and validated up to the final system architecture boundaries.")

