# scenario5_tsv.cmd

set Pressure_mTorr 8
set ICPPower_W 1500
set Bias_V 120

set SF6_sccm 150
set C4F8_sccm 120
set Ar_sccm 50

# TSV mask opening

deposit material=Oxide type=isotropic thickness=0.5

# DRIE cycle block

etch material=Silicon type=anisotropic rate=0.8 time=20

deposit material=Oxide type=isotropic thickness=0.1

etch material=Oxide type=anisotropic thickness=0.05

etch material=Silicon type=anisotropic rate=0.5 time=5

struct tdr=scenario5_tsv