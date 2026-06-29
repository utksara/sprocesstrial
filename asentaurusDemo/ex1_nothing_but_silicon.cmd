# =====================================================================
# Sentaurus Process - Calibrated Flux-Based Bosch Approximation
# =====================================================================

math dimension=2

# ---------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------

line x location=0.0 spacing=0.1 tag=Left
line x location=1.0 spacing=0.1 tag=Right

line y location=0.0 spacing=0.1 tag=Top
line y location=5.0 spacing=0.1 tag=Bottom


# ---------------------------------------------------------------------
# Silicon Region
# ---------------------------------------------------------------------

region Silicon \
    xlo=Left xhi=Right \
    ylo=Top yhi=Bottom 

init

struct tdr=ex1