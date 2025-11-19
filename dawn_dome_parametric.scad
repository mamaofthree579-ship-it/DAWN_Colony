// Dawn Colony — Parametric Dome + Rib Generator (OpenSCAD)
// Usage: load in OpenSCAD, adjust parameters, render/export STL for toolpath generation.
// Note: This is a conceptual parametric generator for prototyping and CAM preparation.

// Parameters (units: mm)
R = 3000;             // dome radius in mm (3000 mm = 3.0 m)
shell_thickness = 60; // mm
rib_spacing = 500;    // mm (arc length spacing)
rib_height = 80;      // mm
rib_top_width = 60;   // mm
rib_base_width = 130; // mm
rib_tendon_dia = 16;  // mm
nozzle_bead = 30;     // mm bead width for projection visualization

// Derived
module dome_shell(){
    difference(){
        // outer hemisphere shell (cut by cube)
        intersection(){
            translate([0,0,0]) sphere(r=R);
            translate([0,0,R/2]) cube([2*R,2*R,R], center=true);
        }
        // inner hollow
        intersection(){
            translate([0,0,0]) sphere(r=R-shell_thickness);
            translate([0,0,R/2]) cube([2*R,2*R,R], center=true);
        }
    }
}

// place ribs around longitude/latitude using spherical mapping (approximation)
module rib_at(theta_deg, phi_deg){
    // Convert degrees to radians
    theta = theta_deg*PI/180;
    phi = phi_deg*PI/180;
    // sample point on sphere surface (outer)
    x = (R)*sin(theta)*cos(phi);
    y = (R)*sin(theta)*sin(phi);
    z = (R)*cos(theta);
    // create rib as long box then orient it to approx normal; trimmed by difference with dome_shell
    rib_length = 2 * R;
    translate([x,y,z])
        rotate(a = acos(z/R)*180/PI, v = [-y, x, 0])
            translate([-rib_length/2, -rib_top_width/2, 0])
                linear_extrude(height = rib_height)
                    polygon(points=[[0,0],[rib_length,0],[rib_length,rib_top_width],[0,rib_base_width]]);
}

module assemble_dome_with_ribs(){
    // dome shell (half dome)
    dome_shell();
    // approximate number of ribs around equator
    num_ribs = floor((2*PI*R) / rib_spacing);
    for(i=[0:num_ribs-1]) {
        phi = i * 360/num_ribs;
        // place ribs at several latitudes between 60° and 120° to produce a rib curtain
        for(theta=[60:10:120]) {
            rib_at(theta, phi);
        }
    }
}

// render
assemble_dome_with_ribs();
