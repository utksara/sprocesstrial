# scenario4_mems.cmd

set Pressure_mTorr 30
set RFPower_W 600
set Bias_V 150

set SF6_sccm 120
set O2_sccm  10

# Geometry creation

# First cavity etch
etch material=Silicon type=anisotropic rate=0.3 time=5

# Oxide refill
deposit material=Oxide type=isotropic thickness=0.5

# Second lithography
etch material=Oxide type=anisotropic thickness=0.4

# Deep cavity
etch material=Silicon type=anisotropic rate=0.5 time=10

struct tdr=scenario4_mems