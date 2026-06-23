# scenario2_har.cmd

math dimension=3

set Pressure_mTorr 10
set RFPower_W 500
set Bias_V 250
set SF6_sccm 80

line x location=0 spacing=0.1 tag=Left
line x location=1 spacing=0.1 tag=Right

line y location=0 spacing=0.1 tag=Top
line y location=3 spacing=0.1 tag=Bottom

line z location=0 spacing=0.1 tag=Front
line z location=1 spacing=0.1 tag=Back

region Silicon xlo=Left xhi=Right ylo=Top yhi=Bottom zlo=Front zhi=Back

init

deposit material=Oxide type=isotropic thickness=0.2

mask name=trench left=0.35 right=0.65 front=0.35 back=0.65

photo mask=trench thickness=0.6

etch material=Oxide type=anisotropic thickness=0.25

strip PhotoResist

etch material=Silicon type=anisotropic rate=1.75 time=8

struct tdr=OxideMaskedHighAspectRatioEtch_run_9
