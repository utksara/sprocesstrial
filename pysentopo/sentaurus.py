import os
from .sshconnect import main

NOT_SPECIFIED = "NA"

usable_metrics = {
    "Pressure": 10,
    "RF_Power": 500,
    "Bias_Voltage": 250,
    "SF6_Flow": 80,
    "Silicon_Etch_Rate": 0.35,
    "changes_observed": NOT_SPECIFIED,
    "Trench_Depth": 0.0,
    "Top_CD": 0.0,
    "Mid_CD": 0.0,
    "Bottom_CD": 0.0,
    "Substrate Geometry": NOT_SPECIFIED,
    "Oxide_thickness_deposited": 0.20,
    "Mask opening Geometry": NOT_SPECIFIED,
    "Etch type": NOT_SPECIFIED,
    "Requested_depth": 0.0,
    "Material etched": NOT_SPECIFIED,
    "Photoresist_thickness": 0.5,
    "Deposited vs Etched Thickness": NOT_SPECIFIED,
    "Etch_depth_calculated": 0.0,
    "Nodes": 0,
    "Volumes": 0,
    "Smallest Region": NOT_SPECIFIED,
    "Smallest_Volume": 0.0
}


customer_input = {
    "Wafer_Size": 100,
    "Wafer_Type": "Coupon (25mm*25mm)",
    "wafer_coupon_width": 25,
    "wafer_coupon_height": 25,
    "Substrate_Type": "Si Substrate (high resistive Si) with 500um thickness",
    "substrate_thickness": 500,
    "Substrate_Material": NOT_SPECIFIED,
    "Photoresist_Thickness": 25.0,
    "Insulator_Thickness": NOT_SPECIFIED,
    "Feature_Type": "VIAs",
    "Size_of_the_Feature": "200um > 150 > 100 ... > 20um Diameter 300um Depth (VIA)",
    "feature_depth": 300,
    "feature_max_diameter": 200,
    "feature_min_diameter": 20,
    "Metrology_Type": "SEM, AFM",
    "Measurement_KPIs": "CD, Depth, Uniformity, Surface Roughness",
    "Defect_Types": NOT_SPECIFIED,
    "Process_Recipe_Sample": "PALOMA",
    "Etch_Time": NOT_SPECIFIED,
    "Dep_Time": NOT_SPECIFIED,
    "Number_of_Cycles": NOT_SPECIFIED,
    "Gas_Types": NOT_SPECIFIED,
    "Gas_Flow_Rates": NOT_SPECIFIED,
    "Power": NOT_SPECIFIED,
    "Pressure": NOT_SPECIFIED,
    "Temperature": NOT_SPECIFIED,
    "OES_available": False,
    "Langmuir_available": False,
    "Interferometry_available": False,
    "Tool_Maker_and_Name": "Sentech Plasma Etching SI500",
    "Chuck_Type": NOT_SPECIFIED,
    "Reactor_Radius": NOT_SPECIFIED,
    "Reactor_Height": ""
}

class SentaurusSim:
    
    _cmd_folder = "./cmd_folder"
    _cmd_file_name = f"{_cmd_folder}/sentaurus_script.cmd"
    _sh_file_name = "remote_task.sh"
    _file_content = ""
    config = {}
    
    def write_cmd(self):
        dir_name = os.path.dirname(SentaurusSim._cmd_file_name)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(SentaurusSim._cmd_file_name, "w") as f:
            f.write(SentaurusSim._file_content)
    
    def write_template(self):
        SentaurusSim._file_content = SentaurusSim._file_content + self.template
        
    def set_config(config): 
        SentaurusSim.config = config
    
    def execute(self):
        self.write_cmd()
        main(
            SentaurusSim.config["REMOTE_HOST"],
            SentaurusSim.config["REMOTE_USER"],
            SentaurusSim.config["REMOTE_PASS"],
            REMOTE_TARGET_DIR = SentaurusSim.config["REMOTE_TARGET_DIR"],
            LOCAL_FOLDER_TO_COPY = SentaurusSim.config["LOCAL_FOLDER_TO_COPY"],
            BASH_SCRIPT_NAME = SentaurusSim.config["BASH_SCRIPT_NAME"]
            )
        SentaurusSim._file_content = ""
        with open(SentaurusSim._cmd_file_name, "w") as f:
            f.write("")