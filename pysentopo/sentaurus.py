import os
from .sshconnect import main

class SentaurusSim:
    _cmd_file_name = "temp_folder/sentaurus_script.cmd"
    _sh_file_name = "temp_folder/remote_task.sh"
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
    
    def execute():
        SentaurusSim.write_cmd()
        main(
            SentaurusSim.config["REMOTE_HOST"],
            SentaurusSim.config["REMOTE_HOST"],
            SentaurusSim.config["REMOTE_USER"],
            SentaurusSim.config["REMOTE_PASS"],
            SentaurusSim.config["REMOTE_TARGET_DIR"],
            SentaurusSim.config["LOCAL_FOLDER_TO_COPY"],
            SentaurusSim.config["BASH_SCRIPT_NAME"] 
            )