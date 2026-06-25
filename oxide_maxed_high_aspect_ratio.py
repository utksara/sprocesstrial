import json
from pysentopo import *

config = {
    "REMOTE_HOST" : "10.114.1.79",
    "REMOTE_USER" : "utkarsh",
    "REMOTE_PASS" : "user123$",
    "REMOTE_TARGET_DIR" : "/home/utkarsh/sentaurus",
    "LOCAL_FOLDER_TO_COPY" : "./cmd_folder",
    "BASH_SCRIPT_NAME" : "remote_task.sh"
}

if __name__ == "__main__":
    # task 1 :vary one paramter from Pressure_(mTorr), RF_Power_(W), Bias_Voltage_(V), SF6_Flow_(sccm), Silicon_Etch_Rate_(um/min) at a time using for loop
    # and for each iteration run the python script in task 2 
    
    with open("task1_combinations.json", "r") as f:
        combinations = json.load(f)
        
    SentaurusSim.set_config(config)
    
    for combo in combinations:
        combo_id = combo["id"]
        
        e = Etching()
        # Initialize math dimension
        e.template = "math dimension=3\n"
        e.write_template()
        
        # Set reactor conditions using mapped combination parameters
        e.set_reactor_conditions(
            Pressure_mTorr=combo["Pressure_mTorr"],
            ICPPower_W=combo["RFPower_W"],
            Bias_V=combo["Bias_V"],
            SF6_Flux=f"{combo['SF6_sccm']/10.0}e17",
            IonFlux=2.0e16,
            IonEnergy_eV=120,
            C4F8_Flux=1.5e17
        )
        
        # Set etching parameters
        e.set_etching_paramters(
            PolymerDepRate=0.01,
            SiliconEtchRate=combo["SiliconEtchRate"],
            DepTime=2.0,
            EtchTime=5.0,
            NumCycles=5
        )
        
        # Set mesh spacing and region bounds
        e.set_mesh(
            x_location_left=0.0,
            x_location_right=1.0,
            region="Silicon",
            y_location_top=0.0,
            y_location_bottom=5.0,
            spacing=0.1
        )
        
        # Deposit oxide and define hard mask via window
        e.set_mask(
            mask_material="Oxide",
            thickness_deposit=0.20,
            mask_name="via",
            mask_left=0.45,
            mask_right=0.55,
            photo_thickness=0.5,
            etch_thickness=0.25,
            strip_material="PhotoResist"
        )
        
        # Create the cyclic Bosch loop
        e.create_etching_cycle()
        
        # Save geometry step
        e.create_geometry(filename=f"OxideMaskedHighAspectRatioEtch_run_{combo_id}")
        
        # Execute the simulation (writes the file and handles remote task setup)
        print(f"Generating and executing {SentaurusSim._cmd_file_name}...")
        try:
            e.execute()
        except Exception as err:
            print(f"Execution failed for run {combo_id}: {err}")