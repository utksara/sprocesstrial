import os
import re
import csv
import numpy as np
import matplotlib.pyplot as plt
import subprocess

# Default visualization geometry parameters
DEFAULT_DEPTH = 1.0
DEFAULT_TOP_CD = 0.1
DEFAULT_MID_CD = 0.1
DEFAULT_BOT_CD = 0.1
DEFAULT_OXIDE_THICKNESS = 0.1
DEFAULT_LEFT = 0.1
DEFAULT_RIGHT = 0.9
DEFAULT_FRONT = 0.1
DEFAULT_BACK = 0.9

# task : it seems this function searches for ==LAYERS_TOP_CD== in log files, though these keywords 
# are present in .cmd files, the correspondg log file does not have it, please correct the code for cmd files
#  in task1_results as well as this function of extract_depth_and_width.
def extract_depth_and_width(log_filepath):
    """
    Parses an Sprocess log file to extract calculated trench depth and CD values (Top, Mid, Bottom).
    """
    if not os.path.exists(log_filepath):
        print(f"Log file not found: {log_filepath}")
        return None
        
    with open(log_filepath, 'r') as f:
        content = f.read()
        
    trench_depth = ""
    td_match = re.search(r'DOE:\s*Trench_Depth\s+(\S+)', content)
    if td_match:
        trench_depth = float(td_match.group(1))
        
    def get_cd(section_name):
        """Return the CD (full width) for a given LAYERS_* marker.
        We look at the lines following the marker until the next marker or end.
        We parse the table rows like:
        { Top Bottom Integral Material }
        """
        lines = content.splitlines()
        cd = ""
        for i, line in enumerate(lines):
            if section_name in line:
                section_lines = []
                for j in range(i + 1, len(lines)):
                    nxt = lines[j].strip()
                    if "==LAYERS_" in nxt or "struct" in nxt or "License features" in nxt:
                        break
                    section_lines.append(nxt)
                
                intervals = []
                for sl in section_lines:
                    # Match rows like: { -2.997219093983e-01 -1.999977074710e-01 0.000000000000e+00 Photoresist }
                    m_row = re.match(r'^\{\s*(\S+)\s+(\S+)\s+(\S+)\s+(\w+)\s*\}', sl)
                    if m_row:
                        try:
                            start = float(m_row.group(1))
                            end = float(m_row.group(2))
                            material = m_row.group(4)
                            intervals.append((start, end, material))
                        except ValueError:
                            pass
                
                if not intervals:
                    # Let's check if there is an echoed layers command line so we can fall back to the dummy value if needed
                    for sl in section_lines:
                        m_cmd = re.search(r'layers\s+[xyXY]=([\d.+-eE]+)', sl)
                        if m_cmd:
                            # Backward-compatible dummy value
                            val = float(m_cmd.group(1))
                            if abs(val - 0.05) < 1e-4:
                                cd = 0.10
                            else:
                                cd = ""
                            break
                    break
                
                # Try to find a Gas interval
                gas_intervals = [it for it in intervals if it[2].lower() == "gas"]
                if gas_intervals:
                    cd = round(gas_intervals[0][1] - gas_intervals[0][0], 6)
                    break
                
                # Check for gaps between solid intervals
                intervals.sort(key=lambda x: x[0])
                for k in range(len(intervals) - 1):
                    end_curr = intervals[k][1]
                    start_next = intervals[k+1][0]
                    if start_next > end_curr + 1e-4:
                        cd = round(start_next - end_curr, 6)
                        break
                if cd != "":
                    break
                
                cd = 0.0
                break
        return cd
        
    top_cd = get_cd('==LAYERS_TOP_CD==')
    mid_cd = get_cd('==LAYERS_MID_CD==')
    bot_cd = get_cd('==LAYERS_BOT_CD==')
    
    return {
        "Trench_Depth": trench_depth,
        "Top_CD": top_cd,
        "Mid_CD": mid_cd,
        "Bottom_CD": bot_cd
    }


def visualize_from_csv(csv_path, row_id):
    """
    Reads parameters from a CSV row and calls both 3D and 2D trench visualization functions.
    """
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return
        
    row = None
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get('id') == str(row_id):
                row = r
                break
                
    if not row:
        print(f"Row ID {row_id} not found in {csv_path}")
        return
        
    depth = float(row.get('Trench_Depth_(um)', DEFAULT_DEPTH) or DEFAULT_DEPTH)
    top_cd = float(row.get('Top_CD_(um)', DEFAULT_TOP_CD) or DEFAULT_TOP_CD)
    mid_cd = float(row.get('Mid_CD_(um)', DEFAULT_MID_CD) or DEFAULT_MID_CD)
    bot_cd = float(row.get('Bottom_CD_(um)', DEFAULT_BOT_CD) or DEFAULT_BOT_CD)
    oxide_thick = float(row.get('Oxide_thickness_deposited_(um)', DEFAULT_OXIDE_THICKNESS) or DEFAULT_OXIDE_THICKNESS)
    
    # Parse Mask Geometry
    left, right, front, back = DEFAULT_LEFT, DEFAULT_RIGHT, DEFAULT_FRONT, DEFAULT_BACK
    mask_str = row.get('Mask opening Geometry', '')
    if mask_str:
        m_left = re.search(r'left=\s*([+-]?\d+\.?\d*)', mask_str)
        m_right = re.search(r'right=\s*([+-]?\d+\.?\d*)', mask_str)
        m_front = re.search(r'front=\s*([+-]?\d+\.?\d*)', mask_str)
        m_back = re.search(r'back=\s*([+-]?\d+\.?\d*)', mask_str)
        if m_left: left = float(m_left.group(1))
        if m_right: right = float(m_right.group(1))
        if m_front: front = float(m_front.group(1))
        if m_back: back = float(m_back.group(1))
        
    dir_name = os.path.dirname(csv_path)
    output_3d_png = os.path.join(dir_name, f"trench_run_{row_id}_3d.png")
    output_2d_png = os.path.join(dir_name, f"trench_run_{row_id}_2d.png")
    
    title_3d = f"3D Trench - Row {row_id}\nDepth: {depth} um | Top CD: {top_cd} um | Bot CD: {bot_cd} um"
    title_2d = f"2D Trench Cross-Section - Row {row_id}"
    
    # Generate 3D isometric view
    visualize_trench_isometric(
        depth=depth,
        top_cd=top_cd,
        mid_cd=mid_cd,
        bot_cd=bot_cd,
        oxide_thick=oxide_thick,
        left=left,
        right=right,
        front=front,
        back=back,
        output_png=output_3d_png,
        title=title_3d
    )
    
    # Generate 2D cross section view
    visualize_trench_cross_section(
        depth=depth,
        top_cd=top_cd,
        mid_cd=mid_cd,
        bot_cd=bot_cd,
        oxide_thick=oxide_thick,
        left=left,
        right=right,
        front=front,
        back=back,
        output_png=output_2d_png,
        title=title_2d
    )


def visualize_trench_cross_section(depth, top_cd=None, mid_cd=None, bot_cd=None, oxide_thick=DEFAULT_OXIDE_THICKNESS, left=DEFAULT_LEFT, right=DEFAULT_RIGHT, front=DEFAULT_FRONT, back=DEFAULT_BACK, output_png=None, title=None):
    """
    Generates and saves a 2D cross-section view of the trench:
    - Subplot 1: Side view with depth, top_cd, mid_cd, and bot_cd labeled.
    - Subplot 2: Top view with width (mask opening) and length labeled.
    """
    # Backwards compatibility check
    if isinstance(depth, str):
        return visualize_from_csv(csv_path=depth, row_id=top_cd)
        
    if top_cd is None: top_cd = DEFAULT_TOP_CD
    if mid_cd is None: mid_cd = DEFAULT_MID_CD
    if bot_cd is None: bot_cd = DEFAULT_BOT_CD
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    if title:
        fig.suptitle(title, fontsize=16, fontweight='bold')
    else:
        fig.suptitle("2D Trench Characterization", fontsize=16, fontweight='bold')
        
    center_y = (left + right) / 2.0
    
    # ------------------ Subplot 1: Side View ------------------
    if depth > 0:
        M = np.array([[depth**2, depth], [0.25 * (depth**2), 0.5 * depth]])
        R = np.array([bot_cd - top_cd, mid_cd - top_cd])
        try:
            a, b = np.linalg.solve(M, R)
        except np.linalg.LinAlgError:
            a, b = 0.0, (bot_cd - top_cd) / depth
    else:
        a, b = 0.0, 0.0
        
    def get_width_at_depth(d):
        return max(0.0, a * (d**2) + b * d + top_cd)
        
    d_profile = np.linspace(0, depth, 200)
    w_profile = np.array([get_width_at_depth(d) for d in d_profile])
    left_wall = center_y - w_profile / 2.0
    right_wall = center_y + w_profile / 2.0
    
    # Fill Silicon Substrate background
    ax1.fill_between([0, 1], [-1.2 * depth, -1.2 * depth], [0, 0], color='royalblue', alpha=0.7, label='Silicon Substrate')
    # Fill trench opening with white
    ax1.fill_betweenx(-d_profile, left_wall, right_wall, color='white')
    
    # Fill Oxide Mask
    ax1.fill_between([0, left], [0, 0], [oxide_thick, oxide_thick], color='orange', alpha=0.8, label='Oxide Mask')
    ax1.fill_between([right, 1], [0, 0], [oxide_thick, oxide_thick], color='orange', alpha=0.8)
    
    # Draw outlines
    ax1.plot(left_wall, -d_profile, color='black', lw=1.5)
    ax1.plot(right_wall, -d_profile, color='black', lw=1.5)
    ax1.plot([left_wall[-1], right_wall[-1]], [-depth, -depth], color='black', lw=1.5)
    ax1.plot([0, left], [0, 0], color='black', lw=1.5)
    ax1.plot([right, 1], [0, 0], color='black', lw=1.5)
    ax1.plot([left, left], [0, oxide_thick], color='black', lw=1.5)
    ax1.plot([right, right], [0, oxide_thick], color='black', lw=1.5)
    ax1.plot([0, left], [oxide_thick, oxide_thick], color='black', lw=1.5)
    ax1.plot([right, 1], [oxide_thick, oxide_thick], color='black', lw=1.5)
    
    # Dimension labels (Annotations)
    # 1. Depth arrow
    arrow_x = 0.92
    ax1.annotate('', xy=(arrow_x, -depth), xytext=(arrow_x, 0),
                 arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax1.text(arrow_x + 0.01, -depth / 2, f'depth = {depth:.3f} um', color='red', va='center', fontweight='bold')
    ax1.plot([center_y, arrow_x], [0, 0], 'r--', lw=1, alpha=0.5)
    ax1.plot([right_wall[-1], arrow_x], [-depth, -depth], 'r--', lw=1, alpha=0.5)
    
    # 2. Top CD
    top_y_l = center_y - top_cd / 2.0
    top_y_r = center_y + top_cd / 2.0
    ax1.annotate('', xy=(top_y_l, 0.01), xytext=(top_y_r, 0.01),
                 arrowprops=dict(arrowstyle='<->', color='purple', lw=1.5))
    ax1.text(center_y, 0.02, f'top_cd = {top_cd:.3f} um', color='purple', ha='center', va='bottom', fontweight='bold')
    
    # 3. Mid CD
    mid_y_l = center_y - mid_cd / 2.0
    mid_y_r = center_y + mid_cd / 2.0
    ax1.annotate('', xy=(mid_y_l, -depth / 2), xytext=(mid_y_r, -depth / 2),
                 arrowprops=dict(arrowstyle='<->', color='purple', lw=1.5))
    ax1.text(center_y, -depth / 2 + 0.01, f'mid_cd = {mid_cd:.3f} um', color='purple', ha='center', va='bottom', fontweight='bold')
    
    # 4. Bottom CD
    bot_y_l = center_y - bot_cd / 2.0
    bot_y_r = center_y + bot_cd / 2.0
    ax1.annotate('', xy=(bot_y_l, -depth + 0.01), xytext=(bot_y_r, -depth + 0.01),
                 arrowprops=dict(arrowstyle='<->', color='purple', lw=1.5))
    ax1.text(center_y, -depth + 0.02, f'bot_cd = {bot_cd:.3f} um', color='purple', ha='center', va='bottom', fontweight='bold')
    
    # Labels and Limits
    ax1.set_xlim(0, 1)
    ax1.set_ylim(-1.2 * depth, oxide_thick + 0.05)
    ax1.set_xlabel("Y Position (um)", fontweight='bold')
    ax1.set_ylabel("Depth (um)", fontweight='bold')
    ax1.set_title("Side View (Cross-Section)", fontweight='bold')
    ax1.legend(loc='lower left')
    ax1.grid(True, linestyle=':', alpha=0.6)
    
    # ------------------ Subplot 2: Top View ------------------
    # Fill whole wafer with oxide
    ax2.fill_between([0, 1], [0, 0], [1, 1], color='orange', alpha=0.8, label='Oxide Mask')
    # Fill trench opening with silicon color
    ax2.fill_between([left, right], [front, front], [back, back], color='royalblue', alpha=0.7, label='Silicon Substrate')
    
    # Outline of trench opening
    ax2.plot([left, right, right, left, left], [front, front, back, back, front], color='black', lw=1.5)
    
    # Label diameter/width and length
    width = right - left
    length = back - front
    
    # Width measurement (horizontal)
    ax2.annotate('', xy=(left, (front + back)/2), xytext=(right, (front + back)/2),
                 arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax2.text((left + right)/2, (front + back)/2 + 0.02, f'width = {width:.3f} um', color='red', ha='center', va='bottom', fontweight='bold')
    
    # Length measurement (vertical)
    ax2.annotate('', xy=((left + right)/2, front), xytext=((left + right)/2, back),
                 arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
    ax2.text((left + right)/2 + 0.02, (front + back)/2, f'length = {length:.3f} um', color='green', ha='left', va='center', rotation=90, fontweight='bold')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_xlabel("Y Position (um)", fontweight='bold')
    ax2.set_ylabel("Z Position (um)", fontweight='bold')
    ax2.set_title("Top View (Wafer Surface)", fontweight='bold')
    ax2.legend(loc='lower left')
    ax2.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    if output_png:
        plt.savefig(output_png, dpi=300)
        print(f"Saved 2D cross-section plot to {output_png}")
    else:
        plt.show()
    plt.close()


def visualize_trench_isometric(depth, top_cd=None, mid_cd=None, bot_cd=None, oxide_thick=DEFAULT_OXIDE_THICKNESS, left=DEFAULT_LEFT, right=DEFAULT_RIGHT, front=DEFAULT_FRONT, back=DEFAULT_BACK, output_png=None, title=None):
    """
    Generates and saves a 3D surface plot of the trench based on direct dimensions.
    """
    # Backwards compatibility check
    if isinstance(depth, str):
        # depth acts as csv_path and top_cd as row_id
        return visualize_from_csv(csv_path=depth, row_id=top_cd)
        
    # Provide defaults for numeric values
    if top_cd is None: top_cd = DEFAULT_TOP_CD
    if mid_cd is None: mid_cd = DEFAULT_MID_CD
    if bot_cd is None: bot_cd = DEFAULT_BOT_CD
    
    center_y = (left + right) / 2.0
    center_z = (front + back) / 2.0
    
    grid_res = 100
    x_vals = np.linspace(0.0, 1.0, grid_res)
    y_vals = np.linspace(0.0, 1.0, grid_res)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = np.zeros_like(X)
    color_mask = np.zeros_like(X)
    
    # Interpolation parameters for width W(d) = a*d^2 + b*d + top_cd
    if depth > 0:
        M = np.array([[depth**2, depth], [0.25 * (depth**2), 0.5 * depth]])
        R = np.array([bot_cd - top_cd, mid_cd - top_cd])
        try:
            a, b = np.linalg.solve(M, R)
        except np.linalg.LinAlgError:
            a, b = 0.0, (bot_cd - top_cd) / depth
    else:
        a, b = 0.0, 0.0
        
    def get_width_at_depth(d):
        return max(0.0, a * (d**2) + b * d + top_cd)
        
    for i in range(grid_res):
        for j in range(grid_res):
            px, py = X[i, j], Y[i, j]
            dist_x = abs(px - center_y)
            dist_y = abs(py - center_z)
            max_dist = max(dist_x, dist_y)
            
            is_outside_mask = (dist_x > (right - left)/2) or (dist_y > (back - front)/2)
            if is_outside_mask:
                Z[i, j] = oxide_thick
                color_mask[i, j] = 1 # Oxide
            else:
                trench_z = 0.0
                inside_trench = False
                for d in np.linspace(0, depth, 150):
                    half_w = get_width_at_depth(d) / 2.0
                    if max_dist <= half_w:
                        trench_z = -d
                        inside_trench = True
                    else:
                        break
                if inside_trench:
                    Z[i, j] = trench_z
                    color_mask[i, j] = 2 # Trench
                else:
                    Z[i, j] = 0.0
                    color_mask[i, j] = 0 # Silicon
                    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    colors = np.empty(X.shape, dtype=object)
    for i in range(grid_res):
        for j in range(grid_res):
            if color_mask[i, j] == 1:
                colors[i, j] = 'orange'
            elif color_mask[i, j] == 2:
                colors[i, j] = 'teal'
            else:
                colors[i, j] = 'royalblue'
                
    ax.plot_surface(X, Y, Z, facecolors=colors, shade=True, rstride=1, cstride=1, linewidth=0, antialiased=False)
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='orange', label='Oxide Mask'),
        Patch(facecolor='royalblue', label='Silicon Substrate'),
        Patch(facecolor='teal', label='Etched Trench')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    ax.set_xlabel('Y (um)')
    ax.set_ylabel('Z (um)')
    ax.set_zlabel('X (um)')
    
    if title is None:
        title = f"3D Trench Geometry\nDepth: {depth} um | Top CD: {top_cd} um | Bot CD: {bot_cd} um"
    ax.set_title(title)
    ax.view_init(elev=35, azim=45)
    
    if output_png:
        plt.savefig(output_png, dpi=300)
        print(f"Saved 3D surface plot to {output_png}")
    else:
        plt.show()
    plt.close()


def visualize_trench(*args, **kwargs):
    """
    Alias/wrapper for visualize_trench_isometric to preserve backwards compatibility.
    """
    return visualize_trench_isometric(*args, **kwargs)

def tdr_to_vtk(input_tdr, output_vtk):
    """
    Exports binary TDR to ASCII/DF-ISE format and parses it into VTK Legacy unstructured mesh format.
    """
    ascii_path = input_tdr.replace(".tdr", "_ascii.tdr")
    has_sentaurus = False
    
    try:
        subprocess.run(["tdr2ascii", input_tdr, ascii_path], capture_output=True, check=True)
        has_sentaurus = True
    except:
        script_content = f'math dimension=3\nstruct tdr="{input_tdr}"\nstruct tdr="{ascii_path}" ascii'
        temp_cmd = "temp_convert.cmd"
        with open(temp_cmd, "w") as f:
            f.write(script_content)
        try:
            subprocess.run(["sprocess", temp_cmd], capture_output=True, check=True)
            has_sentaurus = True
        except:
            pass
        if os.path.exists(temp_cmd):
            os.remove(temp_cmd)
            
    target_ascii = ascii_path if has_sentaurus else input_tdr
    if not os.path.exists(target_ascii):
        print(f"ASCII file not found for parsing: {target_ascii}")
        return
        
    with open(target_ascii, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Vertices
    vertices = []
    v_match = re.search(r'Vertices\s*\((.*?)\)', content, re.DOTALL)
    if v_match:
        coords = [float(v) for v in re.findall(r'[-+]?\d+\.?\d*[eE]?[+-]?\d*', v_match.group(1))]
        for idx in range(0, len(coords), 3):
            if idx + 2 < len(coords):
                vertices.append((coords[idx], coords[idx+1], coords[idx+2]))
                
    # Elements
    elements = []
    e_match = re.search(r'Elements\s*\((.*?)\)', content, re.DOTALL)
    if e_match:
        for line in e_match.group(1).strip().split('\n'):
            parts = line.strip().split()
            if len(parts) >= 4:
                try:
                    elem_type = int(parts[0])
                    nodes = [int(p) for p in parts[1:] if p.isdigit()]
                    elements.append((elem_type, nodes))
                except:
                    continue
                    
    if not vertices:
        print("Failed to parse mesh vertices from ASCII.")
        if has_sentaurus and os.path.exists(ascii_path):
            os.remove(ascii_path)
        return
        
    with open(output_vtk, 'w') as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write("Sentaurus Process Mesh\n")
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n\n")
        
        f.write(f"POINTS {len(vertices)} float\n")
        for v in vertices:
            f.write(f"{v[0]} {v[1]} {v[2]}\n")
        f.write("\n")
        
        total_cells = len(elements)
        cell_size = sum(len(nodes) + 1 for _, nodes in elements)
        f.write(f"CELLS {total_cells} {cell_size}\n")
        for _, nodes in elements:
            f.write(f"{len(nodes)} " + " ".join(str(n) for n in nodes) + "\n")
        f.write("\n")
        
        f.write(f"CELL_TYPES {total_cells}\n")
        for etype, _ in elements:
            vtk_type = 5 if etype == 2 else (10 if etype == 5 else 5)
            f.write(f"{vtk_type}\n")
            
    print(f"Converted VTK saved to {output_vtk}")
    if has_sentaurus and os.path.exists(ascii_path):
        os.remove(ascii_path)