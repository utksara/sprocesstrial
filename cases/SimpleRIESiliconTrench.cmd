```tcl
# scenario1_rie.cmd

math dimension=3

set Pressure_mTorr 20
set RFPower_W      200
set Bias_V         100
set SF6_sccm       50

line x location=0 spacing=0.05 tag=Left
line x location=1 spacing=0.05 tag=Right

line y location=0 spacing=0.05 tag=Top
line y location=2 spacing=0.05 tag=Bottom

line z location=0 spacing=0.05 tag=Front
line z location=1 spacing=0.05 tag=Back

region Silicon xlo=Left xhi=Right ylo=Top yhi=Bottom zlo=Front zhi=Back

init

mask name=trench left=0.4 right=0.6 front=0.4 back=0.6

photo mask=trench thickness=0.5

etch material=Silicon type=anisotropic rate=0.20 time=5.0

strip PhotoResist

struct tdr=scenario1_rie
```