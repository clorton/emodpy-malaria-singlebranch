import emod_api.config.default_from_schema_no_validation as dfs
import manifest
import emodpy_malaria.config as conf

def set_config( config ):
    config.parameters.Acquisition_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Acquisition_Blocking_Immunity_Duration_Before_Decay = 0
    config.parameters.Infectious_Period_Constant = 0
    config.parameters.Enable_Demographics_Birth = 1
    config.parameters.Enable_Demographics_Reporting = 0
    config.parameters.Enable_Immune_Decay = 0
    config.parameters.Migration_Model = "NO_MIGRATION"
    config.parameters.Mortality_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Mortality_Blocking_Immunity_Duration_Before_Decay = 270
    config.parameters.Enable_Demographics_Risk = 1
    config.parameters.Enable_Maternal_Infection_Transmission = 0
    
    config.parameters.x_Base_Population =0.5
    config.parameters.Enable_Disease_Mortality =0
    config.parameters.Max_Individual_Infections = 10
    config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION" # implicit

    # MIGRATION

    """
    config.parameters.x_Local_Migration = 0.03
    config.parameters.Local_Migration_Roundtrip_Duration = 2  # mean of exponential days-at-destination distribution
    config.parameters.Local_Migration_Roundtrip_Probability = 1  # fraction that return
    """

    return config


def set_vsp(config, manifest):
    vsp_default = {"parameters": {"schema": {}}}

    vsp = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorSpeciesParameters"])

    # Add a Vector Species Params set. Opposite of MDP, go with defaults wherever possible
    # These are here, commented out, just to show what can be set. If we want some preset groups, we could have some functions
    # in the emodpy-malaria module.
    vsp.parameters.Name = "SillySkeeter"
    # vsp.parameters.Acquire_Modifier = 1
    vsp.parameters.Adult_Life_Expectancy = 20
    vsp.parameters.Anthropophily = 0.95
    vsp.parameters.Aquatic_Arrhenius_1 = 84200000000
    vsp.parameters.Aquatic_Arrhenius_2 = 8328
    vsp.parameters.Aquatic_Mortality_Rate = 0.1
    ##vsp.parameters.Cycle_Arrhenius_1 = 1
    ##vsp.parameters.Cycle_Arrhenius_2 = 1
    ##vsp.parameters.Cycle_Arrhenius_Reduction_Factor = 1
    vsp.parameters.Days_Between_Feeds = 3
    vsp.parameters.Egg_Batch_Size = 100
    # vsp.parameters.Drivers = []
    # vsp.parameters.Immature_Duration = 2
    # vsp.parameters.Indoor_Feeding_Fraction = 1
    vsp.parameters.Infected_Arrhenius_1 = 117000000000
    vsp.parameters.Infected_Arrhenius_2 = 8336
    vsp.parameters.Infected_Egg_Batch_Factor = 0.8
    vsp.parameters.Infectious_Human_Feed_Mortality_Factor = 1.5
    vsp.parameters.Male_Life_Expectancy = 10
    # vsp.parameters.Transmission_Rate = 1
    # vsp.parameters.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_NONE"

    lhm = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
    lhm.parameters.Max_Larval_Capacity = 398107170.5534969
    lhm.parameters.Vector_Habitat_Type = "LINEAR_SPLINE"
    lhm.parameters.Capacity_Distribution_Number_Of_Years = 1
    lhm.parameters.Capacity_Distribution_Over_Time.Times = [0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583]
    lhm.parameters.Capacity_Distribution_Over_Time.Values = [3, 0.8, 1.25, 0.1, 2.7, 10, 6, 35, 2.8, 1.5, 1.6, 2.1]
    lhm.parameters.finalize()
    vsp.parameters.Larval_Habitat_Types.append( lhm.parameters )
    vsp.parameters.finalize()

    # config.parameters.Vector_Species_Params = list() # won't need this after schema is fixed.
    config.parameters.Vector_Species_Params.append(vsp.parameters)
    return config


def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "MALARIA_SIM"
    config = conf.set_team_defaults( config, manifest )
    config = set_config( config )

    lhm = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
    lhm.parameters.Max_Larval_Capacity = 398107170.5534969
    lhm.parameters.Vector_Habitat_Type = "LINEAR_SPLINE"
    lhm.parameters.Capacity_Distribution_Number_Of_Years = 1
    lhm.parameters.Capacity_Distribution_Over_Time.Times = [0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583]
    lhm.parameters.Capacity_Distribution_Over_Time.Values = [3, 0.8, 1.25, 0.1, 2.7, 10, 6, 35, 2.8, 1.5, 1.6, 2.1]
    lhm.parameters.finalize()
    conf.get_species_params( config, "gambiae" ).Larval_Habitat_Types.append( lhm.parameters )

    config.parameters.Simulation_Duration = 365*5
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    config.parameters.Enable_Vector_Species_Report = 1
    config.parameters.pop( "Serialized_Population_Filenames" )

    # Vector Species Params
    config = set_vsp( config, manifest )
    conf.set_species( config, [ "SillySkeeter" ] )
    return config
