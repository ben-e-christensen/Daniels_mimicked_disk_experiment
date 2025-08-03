import random
import math

# ====== CONFIGURATION ======
inches = 8;

mm = inches * 25.4;

R=mm/2;
canvas_radius = R - 22             # Radius of boundary circle
min_radius = 3.5                  # Minimum ellipse radius
max_radius = 5.5                  # Maximum ellipse radius
padding = 0.2                   # Minimum space between ellipses
max_attempts = 20000            # How many placements to try

output_path = "/home/ben/Desktop/openSCAD/circle_pack.scad"
# ============================

inches = 8;

mm = inches * 25.4;

R=mm/2;

# Store placed ellipses as (x, y, rx, ry)
ellipses = []
attempts = 0

# Check if an ellipse is inside the circular boundary
def is_inside_boundary(x, y, rx, ry):
    dist = math.hypot(x, y)
    corner_dist = math.hypot(rx, ry)
    return dist + corner_dist <= canvas_radius

# Check for overlap with previously placed ellipses
def is_overlapping(x, y, rx, ry, placed):
    for (px, py, prx, pry) in placed:
        dist = math.hypot(x - px, y - py)
        # Conservative: treat ellipses as circles with max axis radius
        if dist < (max(rx, ry) + max(prx, pry) + padding):
            return True
    return False

# Main loop: try placing ellipses
while attempts < max_attempts:
    rx = random.uniform(min_radius, max_radius)
    ry = random.uniform(min_radius, max_radius)

    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, canvas_radius - max(rx, ry) - padding)
    x = r * math.cos(angle)
    y = r * math.sin(angle)

    if is_inside_boundary(x, y, rx, ry) and not is_overlapping(x, y, rx, ry, ellipses):
        ellipses.append((x, y, rx, ry))
    attempts += 1

print(f"Placed {len(ellipses)} ellipses after {attempts} attempts.")

# Write OpenSCAD code
with open(output_path, "w") as f:
    f.write("// Auto-generated packed ellipses inside a circle\n")
    f.write("module circle_pack(){\n")
    f.write("for (e = [\n")
    for (x, y, rx, ry) in ellipses:
        f.write(f"  [{x:.2f}, {y:.2f}, {rx:.2f}, {ry:.2f}],\n")
    f.write("]) {\n")
    f.write("  translate([e[0], e[1]]) scale([e[2], e[3]]) circle(r=1, $fn=100);\n")
    f.write("}\n};\n")
