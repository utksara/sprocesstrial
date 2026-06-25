# ------------------------------------------------------------
# coordinate_etch.cmd (Y-2026 sprocess-compatible)
# ------------------------------------------------------------

math dimension=2

# ---------- domain ----------
line x location=0.0 spacing=0.03 tag=Left
line x location=3.6 spacing=0.03 tag=Right

line y location=0.0 spacing=0.03 tag=Bottom
line y location=3.4 spacing=0.03 tag=Top

region Silicon xlo=Left xhi=Right ylo=Bottom yhi=Top

init

# ---------- deposition stack ----------
deposit material=Tantalum    type=isotropic thickness=0.05
deposit material=Aluminum    type=isotropic thickness=0.75
deposit material=Tantalum    type=isotropic thickness=0.05
deposit material=PhotoResist type=isotropic thickness=1.8

# ---------- coordinate profile approximation ----------
# (converted into mask-like stepped etch windows)

mask name=coord left=0.0 right=0.6
photo mask=coord thickness=1.8

etch material=PhotoResist type=anisotropic thickness=1.8
strip PhotoResist

mask name=coord2 left=1.2 right=2.0
photo mask=coord2 thickness=1.8

etch material=PhotoResist type=anisotropic thickness=1.8
strip PhotoResist

mask name=coord3 left=2.6 right=3.2
photo mask=coord3 thickness=1.8

etch material=PhotoResist type=anisotropic thickness=1.8
strip PhotoResist

# ---------- main silicon etch using SF6-like behavior ----------
etch material=Silicon type=anisotropic rate=0.35 time=8

# ---------- output ----------
struct tdr=coordinate_etch