import os
import csv
import re
from pysentopo import extract_depth_and_width

def parse_log(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
        
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 1. Substrate Geometry (X, Y, Z dimensions)
    line_coords = {'X': [], 'Y': [], 'Z': []}
    for line in content.split('\n'):
        m = re.search(r'line ([XYZ]) location=\s*([+-]?\d+\.?\d*[eE]?[+-]?\d*)', line)
        if m:
            line_coords[m.group(1)].append(float(m.group(2)))
            
    geom_parts = []
    for axis in ['X', 'Y', 'Z']:
        if line_coords[axis]:
            coords = sorted(list(set(line_coords[axis])))
            geom_parts.append(f"{axis}: {coords[0]} to {coords[-1]}")
    substrate_geometry = ", ".join(geom_parts)
    
    # 2. Oxide thickness deposited
    oxide_thickness = ""
    for line in content.split('\n'):
        if "deposit" in line.lower() and "oxide" in line.lower():
            m = re.search(r'thickness=\s*([+-]?\d+\.?\d*)', line)
            if m:
                oxide_thickness = float(m.group(1))
                
    # 3. Mask opening Geometry
    mask_geometry = ""
    for line in content.split('\n'):
        if "mask" in line.lower() and "name=" in line.lower():
            params = []
            for key in ["left", "right", "front", "back"]:
                m = re.search(rf'{key}=\s*([+-]?\d+\.?\d*)', line)
                if m:
                    params.append(f"{key}={m.group(1)}")
            mask_geometry = ", ".join(params)
            
    # 4. Photoresist thickness
    pr_thickness = ""
    for line in content.split('\n'):
        if "photo" in line.lower() and "thickness=" in line.lower():
            m = re.search(r'thickness=\s*([+-]?\d+\.?\d*)', line)
            if m:
                pr_thickness = float(m.group(1))
                
    # 5. Etch steps, requested depths
    oxide_etch_depth = 0.0
    silicon_etch_depth = 0.0
    oxide_etch_type = "None"
    silicon_etch_type = "None"
    
    for line in content.split('\n'):
        if "etch" in line.lower() and "material=" in line.lower():
            # Material
            mat_match = re.search(r'material=\s*\{?(\w+)\}?', line)
            mat = mat_match.group(1) if mat_match else "Unknown"
            
            # Type
            type_match = re.search(r'type=\s*"(\w+)"', line)
            etype = type_match.group(1) if type_match else "Unknown"
            
            # Depth calculation
            thick_match = re.search(r'thickness=\s*([+-]?\d+\.?\d*)', line)
            rate_match = re.search(r'rate=\s*\{?([+-]?\d+\.?\d*)\}?', line)
            time_match = re.search(r'time=\s*([+-]?\d+\.?\d*)', line)
            
            depth = 0.0
            if thick_match:
                depth = float(thick_match.group(1))
            elif rate_match and time_match:
                depth = float(rate_match.group(1)) * float(time_match.group(1))
            
            if mat.lower() == "oxide":
                oxide_etch_depth = depth
                oxide_etch_type = etype
            elif mat.lower() == "silicon":
                silicon_etch_depth += depth
                silicon_etch_type = etype

    # 6. Nodes and Volumes after etching
    nodes = ""
    volumes = ""
    nodes_matches = re.findall(r'Nodes:\s*(\d+)', content)
    volumes_matches = re.findall(r'Volumes:\s*(\d+)', content)
    if nodes_matches:
        nodes = int(nodes_matches[-1])
    if volumes_matches:
        volumes = int(volumes_matches[-1])
        
    # 7. Smallest Region After Etch and its volume
    smallest_region = ""
    smallest_volume = ""
    matches = re.findall(r'Smallest region:\s*(\S+)\s+Total volume:\s*([+-]?\d+\.?\d*[eE]?[+-]?\d*)', content)
    if matches:
        smallest_region = matches[-1][0]
        smallest_volume = float(matches[-1][1])
        
    # Calculations
    # Deposited vs Etched thickness comparison
    deposited_vs_etched = f"Dep Oxide: {oxide_thickness} um, Etch Oxide: {oxide_etch_depth} um"
    
    # Calculate over-etch and total silicon etch depth
    over_etch = max(0.0, oxide_etch_depth - (oxide_thickness if oxide_thickness else 0.0))
    calculated_silicon_depth = silicon_etch_depth + over_etch
    
    # Trench Depth and CD values from Task 3
    geom_data = extract_depth_and_width(filepath) or {}
    trench_depth = geom_data.get("Trench_Depth", "")
    top_cd = geom_data.get("Top_CD", "")
    mid_cd = geom_data.get("Mid_CD", "")
    bot_cd = geom_data.get("Bottom_CD", "")
    
    return {
        "Substrate Geometry": substrate_geometry,
        "Oxide_thickness_deposited_(um)": oxide_thickness,
        "Mask opening Geometry": mask_geometry,
        "Etch type": silicon_etch_type,
        "Requested_depth_(um)": silicon_etch_depth,
        "Material etched": "Silicon",
        "Photoresist_thickness_(um)": pr_thickness,
        "Deposited vs Etched Thickness": deposited_vs_etched,
        "Etch_depth_calculated_(um)": round(calculated_silicon_depth, 6),
        "Nodes": nodes,
        "Volumes": volumes,
        "Smallest Region": smallest_region,
        "Smallest_Volume_(um2_or_um3)": smallest_volume,
        "Trench_Depth_(um)": trench_depth,
        "Top_CD_(um)": top_cd,
        "Mid_CD_(um)": mid_cd,
        "Bottom_CD_(um)": bot_cd
    }

# modify the function such that it also takes log_path as an input
def update_csv(csv_path, log_path):
    
    # task : utilize extract_depth_and_width(log_filepath) from pysentopo/visualization.py to fill currently blank values of Trench_Depth_(um)	Top_CD_(um)	Mid_CD_(um)	Bottom_CD_(um
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        return
        
    rows = []
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
            
    # Define rename mapping for older headers (if present)
    rename_map = {
        "Pressure_mTorr": "Pressure_(mTorr)",
        "RFPower_W": "RF_Power_(W)",
        "Bias_V": "Bias_Voltage_(V)",
        "SF6_sccm": "SF6_Flow_(sccm)",
        "C4F8_sccm": "C4F8_Flow_(sccm)",
        "SiliconEtchRate": "Silicon_Etch_Rate_(um/s)" if "task2" in csv_path else "Silicon_Etch_Rate_(um/min)",
        "PolymerDepRate": "Polymer_Dep_Rate_(um/s)",
        "EtchTime": "Etch_Time_(s)",
        "DepTime": "Dep_Time_(s)",
        "NumCycles": "Num_Cycles",
        "Trench_Depth": "Trench_Depth_(um)",
        "Top_CD": "Top_CD_(um)",
        "Mid_CD": "Mid_CD_(um)",
        "Bottom_CD": "Bottom_CD_(um)"
    }
    
    # Apply header renaming to existing fields
    updated_fieldnames = []
    for f in fieldnames:
        new_f = rename_map.get(f, f)
        if new_f not in updated_fieldnames:
            updated_fieldnames.append(new_f)
            
    # Remap keys in existing rows
    remapped_rows = []
    for row in rows:
        new_row = {}
        for k, v in row.items():
            new_row[rename_map.get(k, k)] = v
        remapped_rows.append(new_row)
        
    # New fields to add
    new_fields = [
        "Substrate Geometry", "Oxide_thickness_deposited_(um)", "Mask opening Geometry",
        "Etch type", "Requested_depth_(um)", "Material etched", "Photoresist_thickness_(um)",
        "Deposited vs Etched Thickness", "Etch_depth_calculated_(um)", "Nodes", "Volumes",
        "Smallest Region", "Smallest_Volume_(um2_or_um3)",
        "Trench_Depth_(um)", "Top_CD_(um)", "Mid_CD_(um)", "Bottom_CD_(um)"
    ]
    
    # Find all new fields that aren't already in updated_fieldnames
    fields_to_add = [f for f in new_fields if f not in updated_fieldnames]
    updated_fieldnames = updated_fieldnames + fields_to_add
    
    final_rows = []
    for row in remapped_rows:
        # log_path = row.get("log_file")
        parsed_data = parse_log(log_path)
        if parsed_data:
            for field in new_fields:
                row[field] = parsed_data[field]
        else:
            for field in new_fields:
                row[field] = "N/A"
        final_rows.append(row)
        
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=updated_fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)
        
    print(f"Successfully updated CSV: {csv_path}")

if __name__ == "__main__":
    # update_csv("task1_results/simulation_results.csv", 'log_20260624-144602/logs/OxideMaskedHighAspectRatioEtch_run_1.log')
    update_csv("task2_results/simulation_results.csv", 'log_20260625-131100/logs/ OxideMaskedHighAspectRatioEtch_withFlux_run_2.log')
