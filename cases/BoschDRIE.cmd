```tcl
# scenario3_bosch.cmd

math dimension=3

set Pressure_mTorr 15
set ICPPower_W     1000
set Bias_V         80

set SF6_sccm       120
set C4F8_sccm      90

line x location=0 spacing=0.02 tag=Left
line x location=1 spacing=0.02 tag=Right

line y location=0 spacing=0.02 tag=Top
line y location=5 spacing=0.02 tag=Bottom

line z location=0 spacing=0.02 tag=Front
line z location=1 spacing=0.02 tag=Back

region Silicon xlo=Left xhi=Right ylo=Top yhi=Bottom zlo=Front zhi=Back

init

deposit material=Oxide type=isotropic thickness=0.2

mask name=via left=0.45 right=0.55 front=0.45 back=0.55

photo mask=via thickness=0.5

etch material=Oxide type=anisotropic thickness=0.25

strip PhotoResist

# Bosch cycle 1
deposit material=Polymer type=isotropic thickness=0.03
etch material=Silicon type=anisotropic rate=0.6 time=1

# Bosch cycle 2
deposit material=Polymer type=isotropic thickness=0.03
etch material=Silicon type=anisotropic rate=0.6 time=1

# Bosch cycle 3
deposit material=Polymer type=isotropic thickness=0.03
etch material=Silicon type=anisotropic rate=0.6 time=1

struct tdr=scenario3_bosch
```
