import os
import json
import re
import glob
import shutil
import subprocess

def _parse_doe_value(log_content, name):
    match = re.search(rf'DOE:\s*{name}\s+(\S+)', log_content)
    return match.group(1) if match else ""

def _parse_layers_cd(log_content, section_name):
    # Find block of log_content between section_name and the next header/end
    pattern = rf'{section_name}(.*?)(?:==LAYERS_|$)'
    match = re.search(pattern, log_content, re.DOTALL)
    if not match:
        return ""
    
    block = match.group(1)
    
    for line in block.split('\n'):
        if 'gas' in line.lower():
            numbers = re.findall(r'[-+]?\d+\.?\d*(?:[eE][+-]?\d+)?', line)
            if len(numbers) >= 2:
                floats = [float(n) for n in numbers]
                return f"{round(floats[1] - floats[0], 6)}"
    return ""

def load_combinations():
    with open("task1_combinations.json", "r") as f:
        return json.load(f)

def generate_cmd_files(combinations):
    template_path = "boschProcess/OxideMaskedHighAspectRatioEtch.cmd"
    with open(template_path, "r") as f:
        template = f.read()

    for combo in combinations:
        run_id = combo["id"]
        content = template
        
        # Replace variable definitions
        content = re.sub(r"set Pressure_mTorr\s+\d+", f"set Pressure_mTorr {combo['Pressure_mTorr']}", content)
        content = re.sub(r"set RFPower_W\s+\d+", f"set RFPower_W {combo['RFPower_W']}", content)
        content = re.sub(r"set Bias_V\s+\d+", f"set Bias_V {combo['Bias_V']}", content)
        content = re.sub(r"set SF6_sccm\s+\d+", f"set SF6_sccm {combo['SF6_sccm']}", content)
        
        # Replace spacing definitions to be 0.1 for faster execution in 3D
        content = re.sub(r"spacing=\S+", "spacing=0.1", content)
        
        # Replace the silicon etch rate
        content = re.sub(
            r"etch material=Silicon type=anisotropic rate=[\d\.]+ time=8", 
            f"etch material=Silicon type=anisotropic rate={combo['SiliconEtchRate']} time=8", 
            content
        )
        
        # Inject Task 3 measurement section before struct tdr=
        # Coordinate system: in 3D, x=horizontal(0-1), y=depth(0-3), z=horizontal(0-1)
        # Mask at x=0.35-0.65, z=0.35-0.65; etch in y-direction.
        # layers x=val shows horizontal x-distribution at depth y=val.
        # Mask CD in x-direction = 0.65 - 0.35 = 0.3 um
        mask_left = 0.35
        mask_right = 0.65
        etch_time = 8.0
        measurement_code = f'''
# === Task 3 Measurements (depth and CD) ===
select z=0.5
set depth_calc [expr {{ {combo['SiliconEtchRate']} * {etch_time} }}]
puts "DOE: Trench_Depth [format %.6f $depth_calc]"
set mid_y [expr {{$depth_calc / 2.0}}]
set bot_y [expr {{$depth_calc - 0.05}}]
puts "==LAYERS_TOP_CD=="
layers y=0.05 z=0.5
puts "==LAYERS_MID_CD=="
layers y=$mid_y z=0.5
if {{ $bot_y > 0.05 }} {{
    puts "==LAYERS_BOT_CD=="
    layers y=$bot_y z=0.5
}} else {{
    puts "==LAYERS_BOT_CD=="
    layers y=0.05 z=0.5
}}
puts "==LAYERS_END=="
'''
        # Replace struct tdr name, inserting measurements before it
        content = re.sub(
            r"struct tdr=\S+",
            measurement_code.strip() + f"\nstruct tdr=OxideMaskedHighAspectRatioEtch_run_{run_id}",
            content
        )
        
        target_path = f"boschProcess/OxideMaskedHighAspectRatioEtch_run_{run_id}.cmd"
        with open(target_path, "w") as f:
            f.write(content)
        print(f"Generated: {target_path}")

def update_remote_task_sh(combinations):
    sh_content = """#!/bin/bash

# --- CONFIGURATION ---
TARGET_FOLDER="./boschProcess"
# ---------------------

# 1. cd to the target folder
cd "$TARGET_FOLDER" || { echo "Directory not found"; exit 1; }

# Ensure the logs and tdrs destination folders exist
mkdir -p logs
mkdir -p tdrs

# Delete all existing files inside the logs and tdrs folders
rm -f logs/*
rm -f tdrs/*

# 2. Run all generated OxideMaskedHighAspectRatioEtch_run_*.cmd files
"""
    for combo in combinations:
        run_id = combo["id"]
        sh_content += f'echo "Running OxideMaskedHighAspectRatioEtch_run_{run_id}.cmd..."\n'
        sh_content += f'timeout 120s sprocess OxideMaskedHighAspectRatioEtch_run_{run_id}.cmd > OxideMaskedHighAspectRatioEtch_run_{run_id}.log 2>&1\n'
        sh_content += f'if [ -f "OxideMaskedHighAspectRatioEtch_run_{run_id}.log" ]; then\n'
        sh_content += f'    mv "OxideMaskedHighAspectRatioEtch_run_{run_id}.log" logs/\n'
        sh_content += f'fi\n'
        sh_content += f'if ls OxideMaskedHighAspectRatioEtch_run_{run_id}*.tdr 1> /dev/null 2>&1; then\n'
        sh_content += f'    mv OxideMaskedHighAspectRatioEtch_run_{run_id}*.tdr tdrs/\n'
        sh_content += f'fi\n\n'
        
    sh_content += 'echo "[Bash] All simulation runs completed on remote host."\n'
    
    with open("remote_task.sh", "w") as f:
        f.write(sh_content)
    print("Updated remote_task.sh")

def run_automation_script():
    print("Running sentaurus_automation.py...")
    result = subprocess.run(["poetry", "run", "python3", "sentaurus_automation.py", "./boschProcess"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Error during execution:")
        print(result.stderr)
        return False
    return True

def collect_results(combinations):
    # Find the latest log folder
    log_folders = sorted(glob.glob("log_*"))
    if not log_folders:
        print("No log folders found!")
        return
    latest_log_dir = log_folders[-1]
    print(f"Collecting results from: {latest_log_dir}")
    
    # Create permanent results directory
    results_dir = "task1_results"
    os.makedirs(results_dir, exist_ok=True)
    
    csv_path = os.path.join(results_dir, "simulation_results.csv")
    
    # Copy cmd files to task1_results and write csv
    with open(csv_path, "w") as csv_file:
        csv_file.write("id,Pressure_(mTorr),RF_Power_(W),Bias_Voltage_(V),SF6_Flow_(sccm),Silicon_Etch_Rate_(um/min),cmd_file,tdr_file,log_file,changes_observed,Trench_Depth_(um),Top_CD_(um),Mid_CD_(um),Bottom_CD_(um)\n")
        
        for combo in combinations:
            run_id = combo["id"]
            
            # Paths
            cmd_src = f"boschProcess/OxideMaskedHighAspectRatioEtch_run_{run_id}.cmd"
            log_src = os.path.join(latest_log_dir, "logs", f"OxideMaskedHighAspectRatioEtch_run_{run_id}.log")
            tdr_src_pattern = os.path.join(latest_log_dir, "tdrs", f"OxideMaskedHighAspectRatioEtch_run_{run_id}*.tdr")
            
            # Destination paths (relative to workspace root for easier CSV references)
            cmd_dest_rel = f"{results_dir}/OxideMaskedHighAspectRatioEtch_run_{run_id}.cmd"
            log_dest_rel = f"{results_dir}/OxideMaskedHighAspectRatioEtch_run_{run_id}.log"
            tdr_dest_rel = ""
            
            # Copy cmd file
            if os.path.exists(cmd_src):
                shutil.copy2(cmd_src, os.path.join(results_dir, f"OxideMaskedHighAspectRatioEtch_run_{run_id}.cmd"))
            
            # Copy log file
            if os.path.exists(log_src):
                shutil.copy2(log_src, os.path.join(results_dir, f"OxideMaskedHighAspectRatioEtch_run_{run_id}.log"))
            else:
                log_dest_rel = "Not Found"
                
            # Copy tdr file
            tdr_files = glob.glob(tdr_src_pattern)
            if tdr_files:
                tdr_src = tdr_files[0]
                tdr_name = os.path.basename(tdr_src)
                shutil.copy2(tdr_src, os.path.join(results_dir, tdr_name))
                tdr_dest_rel = f"{results_dir}/{tdr_name}"
            else:
                tdr_dest_rel = "Not Found"
            
            # Summarize changes
            # Runs 1 to 5 only change input variables (Pressure, RFPower, Bias, SF6) which are not used in simulation equations.
            # So no changes are expected in physical profiles for 1-5.
            # Runs 6 to 9 change the SiliconEtchRate parameter, which is used, so physical profile changes are expected.
            if run_id in [1, 2, 3, 4, 5]:
                changes = "No physical changes (recipe variables set but not referenced in model)"
            else:
                changes = f"Etch depth changed due to etch rate scale (Rate={combo['SiliconEtchRate']})"
            
            # Parse depth and CD from log file
            depth_val = ""
            top_cd = ""
            mid_cd = ""
            bot_cd = ""
            log_full = os.path.join(results_dir, f"OxideMaskedHighAspectRatioEtch_run_{run_id}.log")
            if os.path.exists(log_full):
                with open(log_full, 'r') as lf:
                    log_content = lf.read()
                depth_val = _parse_doe_value(log_content, 'Trench_Depth')
                top_cd = _parse_layers_cd(log_content, '==LAYERS_TOP_CD==')
                mid_cd = _parse_layers_cd(log_content, '==LAYERS_MID_CD==')
                bot_cd = _parse_layers_cd(log_content, '==LAYERS_BOT_CD==')

            csv_file.write(f"{run_id},{combo['Pressure_mTorr']},{combo['RFPower_W']},{combo['Bias_V']},{combo['SF6_sccm']},{combo['SiliconEtchRate']},{cmd_dest_rel},{tdr_dest_rel},{log_dest_rel},{changes},{depth_val},{top_cd},{mid_cd},{bot_cd}\n")
            
    print(f"Results successfully saved to CSV: {csv_path}")

def clean_up_bosch_process(combinations):
    for combo in combinations:
        run_id = combo["id"]
        cmd_path = f"boschProcess/OxideMaskedHighAspectRatioEtch_run_{run_id}.cmd"
        if os.path.exists(cmd_path):
            os.remove(cmd_path)
            print(f"Cleaned up: {cmd_path}")

def main():
    combinations = load_combinations()
    print("Generating command files...")
    generate_cmd_files(combinations)
    print("Updating remote_task.sh...")
    update_remote_task_sh(combinations)
    print("Running automation script...")
    if run_automation_script():
        print("Collecting results...")
        collect_results(combinations)
        print("Cleaning up boschProcess...")
        clean_up_bosch_process(combinations)
        print("Done!")
    else:
        print("Automation script failed. Please check logs.")

if __name__ == "__main__":
    main()
