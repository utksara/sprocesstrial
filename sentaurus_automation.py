import os
import time
import paramiko
from scp import SCPClient # Optional, but we can use Paramiko's built-in SFTP for standard copying


# --- CONFIGURATION ---
REMOTE_HOST = "10.114.1.79"
REMOTE_USER = "utkarsh"
REMOTE_PASS = "user123$"  # Or use pkey for SSH keys
REMOTE_TARGET_DIR = "/home/utkarsh/sentaurus"

LOCAL_FOLDER_TO_COPY = "./boschProcess"
BASH_SCRIPT_NAME = "remote_task.sh"
# ---------------------

def create_local_log_dir():
    """Creates a new folder log_timestamp in the current directory"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_dir_name = f"log_{timestamp}"
    os.makedirs(log_dir_name, exist_ok=True)
    print(f"[Local] Created directory: {log_dir_name}")
    return log_dir_name

def upload_folder_sftp(sftp, local_dir, remote_dir):
    """Recursively uploads a local folder to a remote path via SFTP"""
    try:
        sftp.mkdir(remote_dir)
    except IOError:
        pass # Directory might already exist

    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = os.path.join(remote_dir, item).replace('\\', '/')
        if os.path.isdir(local_path):
            upload_folder_sftp(sftp, local_path, remote_path)
        else:
            sftp.put(local_path, remote_path)
            print(f"[SFTP] Uploaded file: {remote_path}")

def main():
    # 1. Create local timestamp folder
    local_log_dir = create_local_log_dir()

    # 2. Establish SSH Connection (Runs in background)
    print(f"[SSH] Connecting to {REMOTE_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASS)
    
    sftp = ssh.open_sftp()

    try:
        # 3. Copy local folder to remote machine
        remote_folder_path = f"{REMOTE_TARGET_DIR}/{os.path.basename(LOCAL_FOLDER_TO_COPY)}"
        print(f"[SFTP] Copying folder to {remote_folder_path}...")
        upload_folder_sftp(sftp, LOCAL_FOLDER_TO_COPY, remote_folder_path)

        # 4. Copy the bash script to the remote machine
        remote_script_path = f"{REMOTE_TARGET_DIR}/{BASH_SCRIPT_NAME}"
        print(f"[SFTP] Copying script to {remote_script_path}...")
        sftp.put(BASH_SCRIPT_NAME, remote_script_path)
        
        # Make the bash script executable
        ssh.exec_command(f"chmod +x {remote_script_path}")

        # 5. Execute the bash script on the remote side
        print(f"[SSH] Executing script: {remote_script_path} ...")
        
        
        stdin, stdout, stderr = ssh.exec_command(f"cd {REMOTE_TARGET_DIR}")
        # stdin, stdout, stderr = ssh.exec_command(f"cd {REMOTE_TARGET_DIR} && {remote_script_path}")
        
        # Wait for the script to finish and print output
        exit_status = stdout.channel.recv_exit_status() 
        print(stdout.read().decode())
        print(stderr.read().decode())

        if exit_status == 0:
            print("[SSH] Remote script executed successfully.")
            
            # 6. Download the updated logs and tdrs folders back to local log_timestamp directory
            print("[SFTP] Downloading logs and tdrs back to local machine...")
            
            # Helper closure to download remote directories
            def download_remote_dir(remote_dir, local_dir):
                os.makedirs(local_dir, exist_ok=True)
                try:
                    for attr in sftp.listdir_attr(remote_dir):
                        r_path = f"{remote_dir}/{attr.filename}"
                        l_path = os.path.join(local_dir, attr.filename)
                        if 'd' in str(attr.longname).split()[0]: # Check if directory
                            download_remote_dir(r_path, l_path)
                        else:
                            sftp.get(r_path, l_path)
                except IOError:
                    print(f"[Warning] Remote path {remote_dir} not found or empty.")

            download_remote_dir(f"{REMOTE_TARGET_DIR}/boschProcess/logs", os.path.join(local_log_dir, "logs"))
            download_remote_dir(f"{REMOTE_TARGET_DIR}/boschProcess/tdrs", os.path.join(local_log_dir, "tdrs"))
            print("[Success] All files transferred back successfully.")
        else:
            print(f"[Error] Remote script failed with exit code {exit_status}")

    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()