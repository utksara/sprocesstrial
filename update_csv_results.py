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
                
    silicon_etch_rate = ""
    oxide_etch_rate = ""
    etch_time = ""
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
                if rate_match:
                    oxide_etch_rate = float(rate_match.group(1))
                if time_match:
                    etch_time = float(time_match.group(1))
            elif mat.lower() == "silicon":
                silicon_etch_depth += depth
                silicon_etch_type = etype
                if rate_match:
                    silicon_etch_rate = float(rate_match.group(1))
                if time_match:
                    etch_time = float(time_match.group(1))

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
        "Bottom_CD_(um)": bot_cd,
        "Silicon_Etch_Rate_(um/s)": silicon_etch_rate or (oxide_etch_rate if "task2" in filepath else ""),
        "Silicon_Etch_Rate_(um/min)": silicon_etch_rate or (oxide_etch_rate if "task2" not in filepath else ""),
        "Etch_Time_(s)": etch_time
    }

TASK1_HEADERS = [
    "id", "Pressure_(mTorr)", "RF_Power_(W)", "Bias_Voltage_(V)", "SF6_Flow_(sccm)", 
    "Silicon_Etch_Rate_(um/min)", "cmd_file", "tdr_file", "log_file", "changes_observed",
    "Trench_Depth_(um)", "Top_CD_(um)", "Mid_CD_(um)", "Bottom_CD_(um)",
    "Substrate Geometry", "Oxide_thickness_deposited_(um)", "Mask opening Geometry",
    "Etch type", "Requested_depth_(um)", "Material etched", "Photoresist_thickness_(um)",
    "Deposited vs Etched Thickness", "Etch_depth_calculated_(um)", "Nodes", "Volumes",
    "Smallest Region", "Smallest_Volume_(um2_or_um3)"
]

TASK2_HEADERS = [
    "id", "Pressure_(mTorr)", "RF_Power_(W)", "Bias_Voltage_(V)", "SF6_Flow_(sccm)", "C4F8_Flow_(sccm)",
    "SF6_Flux_(10e15_cm-2_s-1)", "C4F8_Flux_(10e15_cm-2_s-1)", "Ion_Flux_(10e15_cm-2_s-1)",
    "Silicon_Etch_Rate_(um/s)", "Polymer_Dep_Rate_(um/s)", "Etch_Time_(s)", "Dep_Time_(s)", "Num_Cycles",
    "cmd_file", "tdr_file", "log_file", "description",
    "Substrate Geometry", "Oxide_thickness_deposited_(um)", "Mask opening Geometry",
    "Etch type", "Requested_depth_(um)", "Material etched", "Photoresist_thickness_(um)",
    "Deposited vs Etched Thickness", "Etch_depth_calculated_(um)", "Nodes", "Volumes",
    "Smallest Region", "Smallest_Volume_(um2_or_um3)",
    "Trench_Depth_(um)", "Top_CD_(um)", "Mid_CD_(um)", "Bottom_CD_(um)"
]

DEFAULT_HEADERS = [
    "id", "Pressure_(mTorr)", "RF_Power_(W)", "Bias_Voltage_(V)", "SF6_Flow_(sccm)", "C4F8_Flow_(sccm)",
    "SF6_Flux_(10e15_cm-2_s-1)", "C4F8_Flux_(10e15_cm-2_s-1)", "Ion_Flux_(10e15_cm-2_s-1)",
    "Silicon_Etch_Rate_(um/s)", "Silicon_Etch_Rate_(um/min)", "Polymer_Dep_Rate_(um/s)", 
    "Etch_Time_(s)", "Dep_Time_(s)", "Num_Cycles",
    "cmd_file", "tdr_file", "log_file", "description", "changes_observed",
    "Substrate Geometry", "Oxide_thickness_deposited_(um)", "Mask opening Geometry",
    "Etch type", "Requested_depth_(um)", "Material etched", "Photoresist_thickness_(um)",
    "Deposited vs Etched Thickness", "Etch_depth_calculated_(um)", "Nodes", "Volumes",
    "Smallest Region", "Smallest_Volume_(um2_or_um3)",
    "Trench_Depth_(um)", "Top_CD_(um)", "Mid_CD_(um)", "Bottom_CD_(um)"
]

def find_corresponding_cmd(log_path):
    log_basename = os.path.basename(log_path)
    cmd_basename = log_basename.replace(".log", ".cmd")
    workspace_root = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(workspace_root):
        if cmd_basename in files:
            return os.path.join(root, cmd_basename)
    return None

def parse_cmd(filepath):
    if not filepath or not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        content = f.read()
    variables = {}
    for match in re.finditer(r'set\s+(\w+)\s+(\S+)', content):
        name = match.group(1)
        val = match.group(2).strip()
        try:
            if '.' in val:
                val = float(val)
            else:
                val = int(val)
        except ValueError:
            pass
        variables[name] = val
        
    description = ""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith("#"):
            desc_candidate = line.lstrip("#").strip()
            if desc_candidate and not any(k in desc_candidate for k in ["===", "scenario", "math", "domain", "output", "Measurements"]):
                description = desc_candidate
                break
    if description:
        variables["description"] = description
    return variables

def find_tdr_file(log_path, cmd_basename):
    parent_dir = os.path.dirname(os.path.dirname(log_path))
    tdr_dir = os.path.join(parent_dir, "tdrs")
    if os.path.exists(tdr_dir):
        for f in os.listdir(tdr_dir):
            if f.startswith(cmd_basename) and f.endswith(".tdr"):
                return os.path.join(tdr_dir, f)
    return ""

# task :  modify log path such that if it is directory instad of file, all log files in the directory are parsed
def update_csv(csv_path, log_path):
    if os.path.isdir(log_path):
        log_files = []
        for root, dirs, files in os.walk(log_path):
            for file in files:
                if file.endswith(".log"):
                    log_files.append(os.path.join(root, file))
        if not log_files:
            print(f"No log files found in directory: {log_path}")
            return
        
        log_files.sort()
        for lf in log_files:
            print(f"Processing log file: {lf}")
            _update_single_csv(csv_path, lf)
    else:
        _update_single_csv(csv_path, log_path)

def _update_single_csv(csv_path, log_path):
    # Ensure parent directory of CSV exists
    csv_dir = os.path.dirname(csv_path)
    if csv_dir and not os.path.exists(csv_dir):
        os.makedirs(csv_dir, exist_ok=True)

    is_empty = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0

    new_fields = [
        "Substrate Geometry", "Oxide_thickness_deposited_(um)", "Mask opening Geometry",
        "Etch type", "Requested_depth_(um)", "Material etched", "Photoresist_thickness_(um)",
        "Deposited vs Etched Thickness", "Etch_depth_calculated_(um)", "Nodes", "Volumes",
        "Smallest Region", "Smallest_Volume_(um2_or_um3)",
        "Trench_Depth_(um)", "Top_CD_(um)", "Mid_CD_(um)", "Bottom_CD_(um)"
    ]

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

    if is_empty:
        # Determine headers based on path or cmd file context
        cmd_path = find_corresponding_cmd(log_path)
        is_task1 = "task1" in csv_path or "task1" in log_path
        is_task2 = "task2" in csv_path or "task2" in log_path
        if not is_task1 and not is_task2 and cmd_path:
            with open(cmd_path, 'r') as f:
                cmd_content = f.read()
            if "SiliconEtchRate" in cmd_content and "PolymerDepRate" in cmd_content:
                is_task2 = True
            elif "SiliconEtchRate" in cmd_content:
                is_task1 = True
                
        if is_task1:
            updated_fieldnames = list(TASK1_HEADERS)
        elif is_task2:
            updated_fieldnames = list(TASK2_HEADERS)
        else:
            updated_fieldnames = list(DEFAULT_HEADERS)
            
        remapped_rows = []
    else:
        rows = []
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)
                
        updated_fieldnames = []
        for f in fieldnames:
            new_f = rename_map.get(f, f)
            if new_f not in updated_fieldnames:
                updated_fieldnames.append(new_f)
                
        remapped_rows = []
        for row in rows:
            new_row = {}
            for k, v in row.items():
                new_row[rename_map.get(k, k)] = v
            remapped_rows.append(new_row)
            
        fields_to_add = [f for f in new_fields if f not in updated_fieldnames]
        updated_fieldnames = updated_fieldnames + fields_to_add

    log_basename = os.path.basename(log_path)
    found_row = None
    for row in remapped_rows:
        row_log = row.get("log_file", "") or row.get("log_path", "")
        if row_log and os.path.basename(row_log) == log_basename:
            found_row = row
            break

    if not found_row:
        new_row = {}
        existing_ids = []
        for r in remapped_rows:
            try:
                existing_ids.append(int(r.get("id", 0)))
            except:
                pass
        new_row["id"] = max(existing_ids) + 1 if existing_ids else 1
        new_row["log_file"] = log_path
        
        cmd_path = find_corresponding_cmd(log_path)
        if cmd_path:
            new_row["cmd_file"] = os.path.relpath(cmd_path, os.getcwd())
            cmd_vars = parse_cmd(cmd_path)
            
            var_to_header = {
                "Pressure_mTorr": "Pressure_(mTorr)",
                "RFPower_W": "RF_Power_(W)",
                "ICPPower_W": "RF_Power_(W)",
                "Bias_V": "Bias_Voltage_(V)",
                "SF6_sccm": "SF6_Flow_(sccm)",
                "C4F8_sccm": "C4F8_Flow_(sccm)",
                "PolymerDepRate": "Polymer_Dep_Rate_(um/s)",
                "EtchTime": "Etch_Time_(s)",
                "DepTime": "Dep_Time_(s)",
                "NumCycles": "Num_Cycles",
                "description": "description"
            }
            for var_name, header_name in var_to_header.items():
                if var_name in cmd_vars and header_name in updated_fieldnames:
                    new_row[header_name] = cmd_vars[var_name]
                    
            if "SiliconEtchRate" in cmd_vars:
                rate = cmd_vars["SiliconEtchRate"]
                if "Silicon_Etch_Rate_(um/s)" in updated_fieldnames:
                    new_row["Silicon_Etch_Rate_(um/s)"] = rate
                elif "Silicon_Etch_Rate_(um/min)" in updated_fieldnames:
                    new_row["Silicon_Etch_Rate_(um/min)"] = rate
                else:
                    if "task2" in csv_path or "Flux" in cmd_path or rate > 0.05:
                        new_row["Silicon_Etch_Rate_(um/s)"] = rate
                    else:
                        new_row["Silicon_Etch_Rate_(um/min)"] = rate
                        
            def convert_flux(val):
                try:
                    f_val = float(val)
                    return int(f_val / 1.0e15)
                except:
                    return val
                    
            for flux_var, header in [("SF6_Flux", "SF6_Flux_(10e15_cm-2_s-1)"), 
                                     ("C4F8_Flux", "C4F8_Flux_(10e15_cm-2_s-1)"), 
                                     ("IonFlux", "Ion_Flux_(10e15_cm-2_s-1)")]:
                if flux_var in cmd_vars and header in updated_fieldnames:
                    new_row[header] = convert_flux(cmd_vars[flux_var])
            
            cmd_basename_no_ext = os.path.splitext(os.path.basename(cmd_path))[0]
            tdr_file_path = find_tdr_file(log_path, cmd_basename_no_ext)
            if tdr_file_path:
                new_row["tdr_file"] = os.path.relpath(tdr_file_path, os.getcwd())
            else:
                new_row["tdr_file"] = ""
        else:
            new_row["cmd_file"] = ""
            new_row["tdr_file"] = ""
            
        remapped_rows.append(new_row)

    final_rows = []
    for row in remapped_rows:
        row_log = row.get("log_file", "") or row.get("log_path", "")
        if row_log and os.path.basename(row_log) == log_basename:
            parsed_data = parse_log(log_path)
            if parsed_data:
                for field in new_fields:
                    row[field] = parsed_data.get(field, "")
                # Also populate rate/time if they are in parsed_data and not set in row yet
                for field in ["Silicon_Etch_Rate_(um/s)", "Silicon_Etch_Rate_(um/min)", "Etch_Time_(s)"]:
                    if field in updated_fieldnames and (row.get(field) is None or row.get(field) == ""):
                        row[field] = parsed_data.get(field, "")
            else:
                for field in new_fields:
                    row[field] = "N/A"
        else:
            for field in updated_fieldnames:
                if field not in row:
                    row[field] = ""
        final_rows.append(row)
        
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=updated_fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)
        
    print(f"Successfully updated CSV: {csv_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        update_csv(sys.argv[1], sys.argv[2])
    else:
        # Example/default usage:
        # update_csv("task1_results/simulation_results.csv", 'log_20260624-144602/logs/OxideMaskedHighAspectRatioEtch_run_1.log')
        # update_csv("etchingWithPlasma/results.csv", 'log_20260625-162840/logs/ion_enhanced_etch.log')
        update_csv("etchingWithPlasma/results.csv", 'log_20260625-114230/logs')
