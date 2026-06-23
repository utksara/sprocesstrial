import os
import csv
import re

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
    
    return {
        "Substrate Geometry": substrate_geometry,
        "Oxide thickness deposited": oxide_thickness,
        "Mask opening Geometry": mask_geometry,
        "Etch type": silicon_etch_type,
        "Requested depth": silicon_etch_depth,
        "Material etched": "Silicon",
        "Photoresist thickness": pr_thickness,
        "Deposited vs Etched Thickness": deposited_vs_etched,
        "Etch depth calculated": round(calculated_silicon_depth, 6),
        "Nodes": nodes,
        "Volumes": volumes,
        "Smallest Region": smallest_region,
        "Smallest Volume": smallest_volume
    }

def update_csv(csv_path):
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        return
        
    rows = []
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
            
    # New fields to add
    new_fields = [
        "Substrate Geometry", "Oxide thickness deposited", "Mask opening Geometry",
        "Etch type", "Requested depth", "Material etched", "Photoresist thickness",
        "Deposited vs Etched Thickness", "Etch depth calculated", "Nodes", "Volumes",
        "Smallest Region", "Smallest Volume"
    ]
    
    # Find all new fields that aren't already in fieldnames
    fields_to_add = [f for f in new_fields if f not in fieldnames]
    updated_fieldnames = fieldnames + fields_to_add
    
    updated_rows = []
    for row in rows:
        log_path = row["log_file"]
        # In case the path starts with task1_results/ or task2_results/
        parsed_data = parse_log(log_path)
        if parsed_data:
            for field in fields_to_add:
                row[field] = parsed_data[field]
        else:
            for field in fields_to_add:
                row[field] = "N/A"
        updated_rows.append(row)
        
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=updated_fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
        
    print(f"Successfully updated CSV: {csv_path}")

if __name__ == "__main__":
    update_csv("task1_results/simulation_results.csv")
    update_csv("task2_results/simulation_results.csv")
