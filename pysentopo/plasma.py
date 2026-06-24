from .sentaurus import SentaurusSim

class Plasma(SentaurusSim):
    
    def __init__(self, pressure, dcpot, acpot, dcthickness, gasmass, ionmass, momentumxsect, numparticles):
        self.template = f" \
        # ---------------------------------------------------------------------\
        # Plasma simulation\
        # ---------------------------------------------------------------------\
        \
        plasma file=spt_plasmaex1_dis pressure={pressure} dcpot={dcpot} acpot={acpot} dcthickness={dcthickness}\n\
        + gasmass={gasmass} ionmass={ionmass} momentumxsect={momentumxsect} numparticles={numparticles} \
        "
        self.write_template()
    
if __name__ == "__main__":
    test_values = 50
    dcpot = 50
    acpot = 55
    dcthickness = 4 
    gasmass = 55
    ionmass = 50
    momentumxsect = 8.E-20
    numparticles = 1e5