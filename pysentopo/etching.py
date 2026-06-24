from .sentaurus import SentaurusSim


class Etching(SentaurusSim):
    def __init__(self):
        self.template = ""
        
    def set_reactor_conditions(self, Pressure_mTorr=10, ICPPower_W=500, Bias_V=250, SF6_Flux=8.0e17, IonFlux=2.0e16, IonEnergy_eV=120, C4F8_Flux=1.5e17):
        self.template = f"""
        # ---------------------------------------------------------------------
        # Reactor Conditions (for documentation/calibration)
        # ---------------------------------------------------------------------

        set Pressure_mTorr {Pressure_mTorr}
        set ICPPower_W {ICPPower_W}
        set Bias_V {Bias_V}

        set SF6_Flux       {SF6_Flux}
        set IonFlux        {IonFlux}
        set IonEnergy_eV   {IonEnergy_eV}

        set C4F8_Flux      {C4F8_Flux}
        """
        self.write_template()
    
    def set_etching_paramters(self, PolymerDepRate=0.01, SiliconEtchRate=0.5387, DepTime=2.0, EtchTime=5.0, NumCycles=5):
        self.template = f"""
        # ---------------------------------------------------------------------
        # Convert Physical Fluxes -> Effective Process Parameters
        #
        # These values would normally come from calibration,
        # reactor simulation, or experiment.
        # ---------------------------------------------------------------------

        set PolymerDepRate {PolymerDepRate}
        set SiliconEtchRate {SiliconEtchRate}

        set DepTime {DepTime}
        set EtchTime {EtchTime}

        set NumCycles {NumCycles}
        """
        self.write_template()

    # Alias to handle correct spelling
    set_etching_parameters = set_etching_paramters
    
    def set_mesh(self, x_location_left=0.0, x_location_right=1.0, region="Silicon", y_location_top=0.0, y_location_bottom=5.0, spacing=0.1):
        self.template = f"""
        # ---------------------------------------------------------------------
        # Mesh
        # ---------------------------------------------------------------------

        line x location={x_location_left} spacing={spacing} tag=Left
        line x location={x_location_right} spacing={spacing} tag=Right

        line y location={y_location_top} spacing={spacing} tag=Top
        line y location={y_location_bottom} spacing={spacing} tag=Bottom
        
        # ---------------------------------------------------------------------
        # {region} Region
        # ---------------------------------------------------------------------

        region {region} \\
            xlo=Left xhi=Right \\
            ylo=Top yhi=Bottom 
        """
        self.write_template()
         
    def set_mask(self, mask_material="Oxide", thickness_deposit=0.20, mask_name="via", mask_left=0.45, mask_right=0.55, photo_thickness=0.5, etch_thickness=0.25, strip_material="PhotoResist"):
        self.template = f"""
        init

        # ---------------------------------------------------------------------
        # Hard Mask
        # ---------------------------------------------------------------------

        deposit material={mask_material} \\
            type=isotropic \\
            thickness={thickness_deposit}

        mask name={mask_name} \\
            left={mask_left} right={mask_right} 

        photo mask={mask_name} thickness={photo_thickness}

        etch material={mask_material} \\
            type=anisotropic \\
            thickness={etch_thickness}

        strip {strip_material}
        """
        self.write_template()
        
    def create_etching_cycle(self, passivation_material="PhotoResist", etch_material="Silicon"):
        self.template = f"""
        # ---------------------------------------------------------------------
        # Bosch Loop
        # ---------------------------------------------------------------------

        for {{set cycle 1}} {{$cycle <= $NumCycles}} {{incr cycle}} {{

            puts "Starting Bosch cycle $cycle"

            # Passivation
            deposit material={passivation_material} \\
                type=isotropic \\
                rate=$PolymerDepRate \\
                time=$DepTime

            # Directional Silicon Etch
            etch material={etch_material} \\
                type=anisotropic \\
                rate=$SiliconEtchRate \\
                time=$EtchTime

            grid remesh

            puts "Completed Bosch cycle $cycle"
        }}
        """
        self.write_template()
        
    def create_geometry(self, filename="OxideMaskedHighAspectRatioEtch_withFlux_run_1"):
        self.template = f"""
        # ---------------------------------------------------------------------
        # Save Final Geometry
        # ---------------------------------------------------------------------

        struct tdr={filename}
        """
        self.write_template()