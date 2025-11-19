Dawn Colony — Parametric SCAD & Auger Calibration (local files)

Files to create locally:
- dawn_dome_parametric.scad  (OpenSCAD script — edit parameters)
- auger_calibration.csv      (CSV table pasted from the earlier block)
- README_Dawn_Printer_Toolchain.txt (this note)

Work flow:
1) Open 'dawn_dome_parametric.scad' in OpenSCAD. Adjust parameters (R, shell_thickness, rib_spacing...). Render and export STL.
2) Import STL into your CAM/CAD slicer. Use spiral toolpath generator or custom script to generate continuous spiral bead paths based on projected sphere surface mapping.
3) Use the auger calibration table as a starting lookup. Run empirical calibration (measure actual volumetric output at multiple RPMs) and compute correction factors.
4) Implement closed-loop extrusion control: controller reads target volumetric flow → looks up auger RPM from table → modulates auger RPM while monitoring inline pressure sensor.
5) For dome prints, use cold-press roller or vibrator to compact beads and improve interlayer bonding. Maintain curing dome conditions for initial hyphal colonization.
