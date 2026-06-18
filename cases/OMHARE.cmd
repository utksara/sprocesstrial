#scenario2_har.cmd

math dimension=3 #means 3d

set Pressure_mTorr 10
set Bias_V         250
set RFPower_W      500
set SF6_sccm       80

line x location=0 spacing=0.2 tag=Left
line x location=2 spacing=0.2 tag=Right

line y location=0 spacing=0.2 tag=Bottom
line y location=4 spacing=0.2 tag=Top

line z location=0 spacing=0.2 tag=Back
line z location=2 spacing=0.2 tag=Front

region Silicon xlo=Left xhi=Right ylo=Bottom yhi=Top zlo=Back zhi=Front

init
deposit material=Oxide type=isotropic thickness=0.25

mask name=layer Left=0.5 Right=0.5 Back=0.75 Front=0.25

photo mask=layer thickness=0.4

etch material=Oxide type=anisotropic thickness=0.35

strip PhotoResist

etch material=Silicon type=anisotropic rate=0.6 time=5

struct tdr=omhare_image