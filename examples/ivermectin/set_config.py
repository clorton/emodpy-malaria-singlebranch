import emod_api.config.default_from_schema_no_validation as dfs
import manifest

def set_config( config ):
    config.parameters.Simulation_Type = "MALARIA_SIM" 

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
    config.parameters.Enable_Natural_Mortality = 1
    
    config.parameters.x_Base_Population =0.5
    config.parameters.Enable_Disease_Mortality =0
    config.parameters.Enable_Malaria_CoTransmission = 1
    config.parameters.Max_Individual_Infections = 10
    config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION" # implicit

    # MIGRATION

    """
    config.parameters.x_Local_Migration = 0.03
    config.parameters.Local_Migration_Roundtrip_Duration = 2  # mean of exponential days-at-destination distribution
    config.parameters.Local_Migration_Roundtrip_Probability = 1  # fraction that return
    """

    return config


def set_mdp(config, manifest):
    """
    Use
    dfs._set_defaults_for_schema_group(default,schema_json["config"]["MALARIA_SIM"]["Malaria_Drug_Params"]["<malaria_drug_name_goes_here>"])
    to get default malaria drug param dict. Convert to schema-backed version (that's an emod_api responsibility)
    dfs.load_config_as_rod

    Set params as desired.
    Do this for each malaria drug.
    Add to config (through emod_api if necessary, this might end up being an insertion which would normally be forbidden by schema-backed non-insertable dict)
    """
    # This initial code is just fumbling my way towards a solution; this code will be deeper down in a util function when done.
    # I'd rather these next two lines be under-the-hood
    mdp_default = {"parameters": {"schema": {}}}
    mdp = dfs.schema_to_config_subnode(manifest.schema_file, ["config", "MALARIA_SIM", "Malaria_Drug_Params",
                                                              "<malaria_drug_name_goes_here>"])

    # Just demonstrating that we can set drug params. Values mean nothing at this time.
    mdp.parameters.Bodyweight_Exponent = 45
    mdp.parameters.Drug_Cmax = 100
    mdp.parameters.Drug_Decay_T1 = 1
    mdp.parameters.Drug_Decay_T2 = 1
    mdp.parameters.Drug_Dose_Interval = 1
    mdp.parameters.Drug_Fulltreatment_Doses = 1
    mdp.parameters.Drug_Gametocyte02_Killrate = 1
    mdp.parameters.Drug_Gametocyte34_Killrate = 1
    mdp.parameters.Drug_GametocyteM_Killrate = 1
    mdp.parameters.Drug_Hepatocyte_Killrate = 1
    mdp.parameters.Drug_PKPD_C50 = 1
    mdp.parameters.Drug_Vd = 1
    # This needs to be changed ASAP
    """
    mdp.parameters.Fractional_Dose_By_Upper_Age = [
                {
                    "Fraction_Of_Adult_Dose": 0.5,
                    "Upper_Age_In_Years": 5
                }
            ]
    """
    mdp.parameters.Max_Drug_IRBC_Kill = 1

    mdp_map = {}
    mdp.parameters.finalize()
    mdp_map["Chloroquine"] = mdp.parameters

    config.parameters.Malaria_Drug_Params = mdp_map
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

    # This needs to be changed once the schema for Larval_Habitat_Types is fixed.
    # Keys-as-values means we have to do this
    vsp.parameters.Larval_Habitat_Types = {
        "LINEAR_SPLINE": { \
            "Capacity_Distribution_Number_Of_Years": 1, \
            "Capacity_Distribution_Over_Time": { \
                "Times": [0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167,
                          334.583],
                "Values": [3, 0.8, 1.25, 0.1, 2.7, 10, 6, 35, 2.8, 1.5, 1.6, 2.1]
            },
            "Max_Larval_Capacity": 398107170.5534969
        }
    }
    vsp.parameters.finalize()

    # config.parameters.Vector_Species_Params = list() # won't need this after schema is fixed.
    config.parameters.Vector_Species_Params.append(vsp.parameters)
    return config


def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config = set_config( config )

    config.parameters.Simulation_Duration = 365*5
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    config.parameters.Enable_Vector_Species_Report = 1
    config.parameters.pop( "Serialized_Population_Filenames" )

    # Set MalariaDrugParams
    config = set_mdp( config, manifest )

    # Vector Species Params
    config = set_vsp( config, manifest )
    return config
