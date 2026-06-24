from pysentopo import *


config = {
    "REMOTE_HOST" : "10.114.1.79",
    "REMOTE_USER" : "utkarsh",
    "REMOTE_PASS" : "user123$",  # Or use pkey for SSH keys
    "REMOTE_TARGET_DIR" : "/home/utkarsh/sentaurus",
    "LOCAL_FOLDER_TO_COPY" : "./boschProcess",
    "BASH_SCRIPT_NAME" : "remote_task.sh"
}

test_values = 50
dcpot = 50
acpot = 55
dcthickness = 4 
gasmass = 55
ionmass = 50
momentumxsect = 8.E-20
numparticles = 1e5

Pressure_mTorr = 10
ICPPower_W = 500
Bias_V = 250

SF6_Flux = 8.0e17
IonFlux = 2.0e16
IonEnergy_eV = 120

C4F8_Flux = 1.5e17

PolymerDepRate = 0.01
SiliconEtchRate = 0.5387

DepTime = 2.0
EtchTime = 5.0

NumCycles = 5

region = "Silicon"
x_location_left = 0.0
x_location_right = 1.0
x_spacing = 0.1

y_location_left = 0.0
y_location_right = 5.0
y_spacing = 0.1
    
SentaurusSim.set_config(config)

Plasma(test_values, dcpot, acpot, dcthickness, gasmass, ionmass, momentumxsect, numparticles)