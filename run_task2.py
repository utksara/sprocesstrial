import os
import json
import re
import glob
import shutil
import subprocess

def load_combinations():
    with open("task2_combinations.json", "r") as f:
        return json.load(f)

def calculate_rates(combo):
    sf6_sccm = combo["SF6_sccm"]
    rf_power = combo["RFPower_W"]
    bias_v = combo["Bias_V"]
    pressure = combo["Pressure_mTorr"]
    c4f8_sccm = combo["C4F8_sccm"]
    
    # SF6 Neutral Flux and Ion Flux approximation
    sf6_flux = sf6_sccm * 1.0e16 * (pressure / 10.0)
    ion_flux = rf_power * 4.0e13
    ion_energy = bias_v
    
    # Silicon Etch Rate Model: chemical + ion-enhanced
    c1 = 3.125e-19
    c2 = 9.129e-19
    silicon_etch_rate = c1 * sf6_flux + c2 * ion_flux * (ion_energy ** 0.5)
    
    # Polymer Deposition Rate Model: driven by C4F8 neutrals
    polymer_dep_rate = 0.015 * (c4f8_sccm / 100.0) * (pressure / 15.0)
    
    return round(silicon_etch_rate, 4), round(polymer_dep_rate, 4)

def generate_cmd_files(combinations):
    template_path = "boschProcess/OxideMaskedHighAspectRatioEtch_withFlux.cmd"
    with open(template_path, "r") as f:
        template = f.read()

    for combo in combinations:
        run_id = combo["id"]
        silicon_etch_rate, polymer_dep_rate = calculate_rates(combo)
        
        content = template
        
        # Replace reactor settings
        content = re.sub(r"set Pressure_mTorr\s+\d+", f"set Pressure_mTorr {combo['Pressure_mTorr']}", content)
        content = re.sub(r"set ICPPower_W\s+\d+", f"set ICPPower_W {combo['RFPower_W']}", content)
        content = re.sub(r"set Bias_V\s+\d+", f"set Bias_V {combo['Bias_V']}", content)
        
        # Replace fluxes
        sf6_flux = combo['SF6_sccm'] * 1.0e16 * (combo['Pressure_mTorr'] / 10.0)
        c4f8_flux = combo['C4F8_sccm'] * 1.5e15 * (combo['Pressure_mTorr'] / 10.0)
        ion_flux = combo['RFPower_W'] * 4.0e13
        ion_energy = combo['Bias_V']
        
        content = re.sub(r"set SF6_Flux\s+\S+", f"set SF6_Flux       {sf6_flux:.1e}", content)
        content = re.sub(r"set C4F8_Flux\s+\S+", f"set C4F8_Flux      {c4f8_flux:.1e}", content)
        content = re.sub(r"set IonFlux\s+\S+", f"set IonFlux        {ion_flux:.1e}", content)
        content = re.sub(r"set IonEnergy_eV\s+\d+", f"set IonEnergy_eV   {ion_energy}", content)
        
        # Replace calculated rate settings
        content = re.sub(r"set PolymerDepRate\s+[\d\.]+", f"set PolymerDepRate {polymer_dep_rate}", content)
        content = re.sub(r"set SiliconEtchRate\s+[\d\.]+", f"set SiliconEtchRate {silicon_etch_rate}", content)
        
        # Convert timing and cycles settings
        content = re.sub(r"set DepTime\s+[\d\.]+", f"set DepTime {combo['DepTime']}", content)
        content = re.sub(r"set EtchTime\s+[\d\.]+", f"set EtchTime {combo['EtchTime']}", content)
        content = re.sub(r"set NumCycles\s+\d+", f"set NumCycles {combo['NumCycles']}", content)
        
        # Convert to 2D
        content = content.replace("math dimension=3", "math dimension=2")
        content = re.sub(r"line z location=.* spacing=.* tag=.*\n", "", content)
        content = re.sub(r"\\\s+zlo=Front\s+zhi=Back", "", content)
        content = re.sub(r"\\\s+front=0.45\s+back=0.55", "", content)
        content = content.replace("select z=0.5\n", "")
        content = content.replace(" z=0.5", "")
        
        # Replace mesh spacing to 0.1 for fast execution
        content = re.sub(r"spacing=\S+", "spacing=0.1", content)
        
        # Replace struct tdr name
        content = re.sub(
            r"struct tdr=\S+", 
            f"struct tdr=OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}", 
            content
        )
        
        target_path = f"boschProcess/OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.cmd"
        with open(target_path, "w") as f:
            f.write(content)
        print(f"Generated: {target_path} (calculated SiliconEtchRate={silicon_etch_rate}, PolymerDepRate={polymer_dep_rate})")

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

# 2. Run all generated OxideMaskedHighAspectRatioEtch_withFlux_run_*.cmd files
"""
    for combo in combinations:
        run_id = combo["id"]
        # Use a larger timeout for the 20-cycle runs
        timeout_sec = 240 if combo["NumCycles"] >= 20 else 120
        sh_content += f'echo "Running OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.cmd..."\n'
        sh_content += f'timeout {timeout_sec}s sprocess OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.cmd\n'
        sh_content += f'if [ -f "OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.log" ]; then\n'
        sh_content += f'    mv "OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.log" logs/\n'
        sh_content += f'fi\n'
        sh_content += f'if ls OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}*.tdr 1> /dev/null 2>&1; then\n'
        sh_content += f'    mv OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}*.tdr tdrs/\n'
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
    log_folders = sorted(glob.glob("log_*"))
    if not log_folders:
        print("No log folders found!")
        return
    latest_log_dir = log_folders[-1]
    print(f"Collecting results from: {latest_log_dir}")
    
    results_dir = "task2_results"
    os.makedirs(results_dir, exist_ok=True)
    
    csv_path = os.path.join(results_dir, "simulation_results.csv")
    
    with open(csv_path, "w") as csv_file:
        # Renamed headers with units
        headers = [
            "id", "Pressure_(mTorr)", "RF_Power_(W)", "Bias_Voltage_(V)",
            "SF6_Flow_(sccm)", "C4F8_Flow_(sccm)", 
            "SF6_Flux_(10e15_cm-2_s-1)", "C4F8_Flux_(10e15_cm-2_s-1)", "Ion_Flux_(10e15_cm-2_s-1)",
            "Silicon_Etch_Rate_(um/s)", "Polymer_Dep_Rate_(um/s)", 
            "Etch_Time_(s)", "Dep_Time_(s)", "Num_Cycles",
            "cmd_file", "tdr_file", "log_file", "description"
        ]
        csv_file.write(",".join(headers) + "\n")
        
        for combo in combinations:
            run_id = combo["id"]
            silicon_etch_rate, polymer_dep_rate = calculate_rates(combo)
            
            # Calculate fluxes in 10e15 units (e.g. 8.0e17 is 800 * 10e15)
            sf6_flux_10e15 = int((combo['SF6_sccm'] * 1.0e16 * (combo['Pressure_mTorr'] / 10.0)) / 1.0e15)
            c4f8_flux_10e15 = int((combo['C4F8_sccm'] * 1.5e15 * (combo['Pressure_mTorr'] / 10.0)) / 1.0e15)
            ion_flux_10e15 = int((combo['RFPower_W'] * 4.0e13) / 1.0e15)
            
            # Paths
            cmd_src = f"boschProcess/OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.cmd"
            log_src = os.path.join(latest_log_dir, "logs", f"OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.log")
            tdr_src_pattern = os.path.join(latest_log_dir, "tdrs", f"OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}*.tdr")
            
            # Destination paths (relative to workspace root for easier CSV references)
            cmd_dest_rel = f"{results_dir}/OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.cmd"
            log_dest_rel = f"{results_dir}/OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.log"
            tdr_dest_rel = ""
            
            # Copy cmd file
            if os.path.exists(cmd_src):
                shutil.copy2(cmd_src, os.path.join(results_dir, f"OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.cmd"))
            
            # Copy log file
            if os.path.exists(log_src):
                shutil.copy2(log_src, os.path.join(results_dir, f"OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.log"))
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
            
            row_values = [
                str(run_id),
                str(combo['Pressure_mTorr']),
                str(combo['RFPower_W']),
                str(combo['Bias_V']),
                str(combo['SF6_sccm']),
                str(combo['C4F8_sccm']),
                str(sf6_flux_10e15),
                str(c4f8_flux_10e15),
                str(ion_flux_10e15),
                str(silicon_etch_rate),
                str(polymer_dep_rate),
                str(combo['EtchTime']),
                str(combo['DepTime']),
                str(combo['NumCycles']),
                cmd_dest_rel,
                tdr_dest_rel,
                log_dest_rel,
                combo['description']
            ]
            csv_file.write(",".join(row_values) + "\n")
            
    print(f"Results successfully saved to CSV: {csv_path}")

def clean_up_bosch_process(combinations):
    for combo in combinations:
        run_id = combo["id"]
        cmd_path = f"boschProcess/OxideMaskedHighAspectRatioEtch_withFlux_run_{run_id}.cmd"
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
