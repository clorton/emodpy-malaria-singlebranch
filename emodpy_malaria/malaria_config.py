import emod_api.config.default_from_schema_no_validation as dfs
import csv
import os
from . import vector_config

#
# PUBLIC API section
#

def get_file_from_http(url):
    """
        Get data files from simple http server.
    """
    import urllib.request as req
    import tempfile

    path = tempfile.NamedTemporaryFile()
    path.close()
    req.urlretrieve(url, path.name)
    return path.name


def set_team_defaults(config, mani):
    """
        Set configuration defaults using team-wide values, including drugs and vector species.
    """
    vector_config.set_team_defaults( config, mani )
    config.parameters.Simulation_Type = "MALARIA_SIM"
    config.parameters.Malaria_Strain_Model = "FALCIPARUM_RANDOM_STRAIN"
    # config.parameters.Enable_Malaria_CoTransmission = 0

    # INFECTION

    config.parameters.Max_MSP1_Antibody_Growthrate = 0
    config.parameters.Min_Adapted_Response = 0
    config.parameters.Infection_Updates_Per_Timestep = 8
    config.parameters.Enable_Superinfection = 1
    config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION"
    config.parameters.Incubation_Period_Constant = 7
    config.parameters.Antibody_IRBC_Kill_Rate = 1.596
    config.parameters.RBC_Destruction_Multiplier = 3.29
    config.parameters.Parasite_Switch_Type = "RATE_PER_PARASITE_7VARS"

    # 150305 calibration by JG to Burkina data + 6 of Kevin's sites
    # N.B: severe disease re-calibration not done
    # 'Base_Gametocyte_Production_Rate': 0.044,
    # config.parameters.Gametocyte_Stage_Survival_Rate = 0.82,
    # 'Antigen_Switch_Rate': 2.96e-9,
    # 'Falciparum_PfEMP1_Variants': 1112,
    # 'Falciparum_MSP_Variants': 7,
    # 'MSP1_Merozoite_Kill_Fraction': 0.43,
    # 'Falciparum_Nonspecific_Types': 90,
    # 'Nonspecific_Antigenicity_Factor': 0.42,
    # 'Base_Gametocyte_Mosquito_Survival_Rate': 0.00088,
    # config.parameters.Max_Individual_Infections = 5,

    # 180824 Prashanth parameters [description?]
    import math
    config.parameters.Antigen_Switch_Rate = math.pow(10, -9.116590124)
    config.parameters.Base_Gametocyte_Production_Rate = 0.06150582
    config.parameters.Base_Gametocyte_Mosquito_Survival_Rate = 0.002011099
    config.parameters.Falciparum_MSP_Variants = 32
    config.parameters.Falciparum_Nonspecific_Types = 76
    config.parameters.Falciparum_PfEMP1_Variants = 1070
    config.parameters.Gametocyte_Stage_Survival_Rate = 0.588569307
    config.parameters.MSP1_Merozoite_Kill_Fraction = 0.511735322
    config.parameters.Max_Individual_Infections = 3
    config.parameters.Nonspecific_Antigenicity_Factor = 0.415111634

    # IMMUNITY; these are NOT schema defaults
    config.parameters.Antibody_CSP_Killing_Threshold = 20
    config.parameters.Antigen_Switch_Rate = math.pow(10, -9.116590124)
    config.parameters.Base_Gametocyte_Production_Rate = 0.06150582
    config.parameters.Base_Gametocyte_Mosquito_Survival_Rate = 0.002011099
    config.parameters.Pyrogenic_Threshold = 1.5e4
    config.parameters.Falciparum_MSP_Variants = 32
    config.parameters.Falciparum_Nonspecific_Types = 76
    config.parameters.Falciparum_PfEMP1_Variants = 1070
    config.parameters.Fever_IRBC_Kill_Rate = 1.4
    config.parameters.Gametocyte_Stage_Survival_Rate = 0.588569307
    config.parameters.Max_MSP1_Antibody_Growthrate = 0.045
    config.parameters.MSP1_Merozoite_Kill_Fraction = 0.511735322
    config.parameters.Max_Individual_Infections = 3
    config.parameters.Nonspecific_Antigenicity_Factor = 0.415111634
    config.parameters.Antibody_Capacity_Growth_Rate = 0.09
    config.parameters.Antibody_Stimulation_C50 = 30
    config.parameters.Antibody_Memory_Level = 0.34
    config.parameters.Min_Adapted_Response = 0.05
    config.parameters.Cytokine_Gametocyte_Inactivation = 0.01667
    config.parameters.Enable_Maternal_Antibodies_Transmission = 1
    config.parameters.Maternal_Antibodies_Type = "SIMPLE_WANING"
    config.parameters.Maternal_Antibody_Protection = 0.1327

    # SYMPTOMATICITY
    config.parameters.Anemia_Mortality_Inverse_Width = 1
    config.parameters.Anemia_Mortality_Threshold = 0.654726662830038
    config.parameters.Anemia_Severe_Inverse_Width = 10
    config.parameters.Anemia_Severe_Threshold = 4.50775824973078

    config.parameters.Fever_Mortality_Inverse_Width = 1895.51971624351
    config.parameters.Fever_Mortality_Threshold = 3.4005008555391
    config.parameters.Fever_Severe_Inverse_Width = 27.5653580403806
    config.parameters.Fever_Severe_Threshold = 3.98354299722192

    config.parameters.Parasite_Mortality_Inverse_Width = 327.51594505874
    config.parameters.Parasite_Mortality_Threshold = 10 ** 5.93
    config.parameters.Parasite_Severe_Inverse_Width = 56.5754896048744
    config.parameters.Parasite_Severe_Threshold = 10 ** 5.929945527

    config.parameters.Clinical_Fever_Threshold_High = 1.5
    config.parameters.Clinical_Fever_Threshold_Low = 0.5
    config.parameters.Min_Days_Between_Clinical_Incidents = 14

    # updated from mambrose Oct 11 2019, personal communication with M Plucinski
    config.parameters.PfHRP2_Boost_Rate = 0.018  # original value: 0.07
    config.parameters.PfHRP2_Decay_Rate = 0.167  # original value: 0.172

    config.parameters.Report_Detection_Threshold_Blood_Smear_Gametocytes = 20
    config.parameters.Report_Detection_Threshold_Blood_Smear_Parasites = 20
    config.parameters.Report_Detection_Threshold_Fever = 1.0
    config.parameters.Report_Detection_Threshold_PCR_Gametocytes = 0.05
    config.parameters.Report_Detection_Threshold_PCR_Parasites = 0.05
    config.parameters.Report_Detection_Threshold_PfHRP2 = 5.0
    config.parameters.Report_Detection_Threshold_True_Parasite_Density = 0.0

    config.parameters.Report_Gametocyte_Smear_Sensitivity = 0.1
    config.parameters.Report_Parasite_Smear_Sensitivity = 0.1  # 10/uL

    config = set_team_drug_params(config, mani)

    return config


def set_team_drug_params(config, mani):
    # TBD: load csv with drug params and populate from that.
    with open(os.path.join(os.path.dirname(__file__), 'malaria_drug_params.csv'), newline='') as csvfile:
        my_reader = csv.reader(csvfile)

        header = next(my_reader)
        drug_name_idx = header.index("Name")
        # drug_pkpd_model_idx = header.index("PKPD_Model")
        drug_cmax_idx = header.index("Drug_Cmax")
        drug_decayt1_idx = header.index("Drug_Decay_T1")
        drug_decayt2_idx = header.index("Drug_Decay_T2")
        drug_vd_idx = header.index("Drug_Vd")
        drug_pkpdc50_idx = header.index("Drug_PKPD_C50")
        drug_ftdoses_idx = header.index("Drug_Fulltreatment_Doses")
        drug_dose_interval_idx = header.index("Drug_Dose_Interval")
        drug_gam02_idx = header.index("Drug_Gametocyte02_Killrate")
        drug_gam34_idx = header.index("Drug_Gametocyte34_Killrate")
        drug_gamM_idx = header.index("Drug_GametocyteM_Killrate")
        drug_hep_idx = header.index("Drug_Hepatocyte_Killrate")
        drug_maxirbc_idx = header.index("Max_Drug_IRBC_Kill")
        drug_adher_idx = header.index("Drug_Adherence_Rate")
        drug_bwexp_idx = header.index("Bodyweight_Exponent")
        drug_fracdos_key_idx = header.index("Upper_Age_In_Years")
        drug_fracdos_val_idx = header.index("Fraction_Of_Adult_Dose")

        # for each
        for row in my_reader:
            mdp = dfs.schema_to_config_subnode(mani.schema_file, ["idmTypes", "idmType:MalariaDrugTypeParameters"])
            mdp.parameters.Drug_Cmax = float(row[drug_cmax_idx])
            mdp.parameters.Drug_Decay_T1 = float(row[drug_decayt1_idx])
            mdp.parameters.Drug_Decay_T2 = float(row[drug_decayt2_idx])
            mdp.parameters.Drug_Vd = float(row[drug_vd_idx])
            mdp.parameters.Drug_Vd = float(row[drug_vd_idx])
            mdp.parameters.Drug_PKPD_C50 = float(row[drug_pkpdc50_idx])
            mdp.parameters.Drug_Fulltreatment_Doses = float(row[drug_ftdoses_idx])
            mdp.parameters.Drug_Dose_Interval = float(row[drug_dose_interval_idx])
            mdp.parameters.Drug_Gametocyte02_Killrate = float(row[drug_gam02_idx])
            mdp.parameters.Drug_Gametocyte34_Killrate = float(row[drug_gam34_idx])
            mdp.parameters.Drug_GametocyteM_Killrate = float(row[drug_gamM_idx])
            mdp.parameters.Drug_Hepatocyte_Killrate = float(row[drug_hep_idx])
            mdp.parameters.Max_Drug_IRBC_Kill = float(row[drug_maxirbc_idx])
            # mdp.parameters.PKPD_Model = row[drug_pkpd_model_idx]
            mdp.parameters.Name = row[drug_name_idx]
            # mdp.parameters.Drug_Adherence_Rate = float(row[ drug_adher_idx ])
            mdp.parameters.Bodyweight_Exponent = float(row[drug_bwexp_idx])

            try:
                ages = [float(x) for x in row[drug_fracdos_key_idx].strip('[]').split(",")]
                values = [float(x) for x in row[drug_fracdos_val_idx].strip('[]').split(",")]
            except Exception as ex:
                print(str(ex))
                ages = []
                values = []
            for idx in range(len(ages)):
                fdbua = dict()
                # this is what we want but not ready yet 
                # fdbua = dfs.schema_to_config_subnode(mani.schema_file, ["idmTypes","idmType:DoseMap"] )
                # fdbua.Upper_Age_In_Years = ages[idx]
                # fdbua.Fraction_Of_Adult_Dose = values[idx]
                fdbua["Upper_Age_In_Years"] = ages[idx]
                fdbua["Fraction_Of_Adult_Dose"] = values[idx]
                # fdbua.finalize()
                mdp.parameters.Fractional_Dose_By_Upper_Age.append(fdbua)

            config.parameters.Malaria_Drug_Params.append(mdp.parameters)
    # end

    return config


def get_drug_params(cb, drug_name):
    for idx, drug_params in enumerate(cb.parameters.Malaria_Drug_Params):
        if drug_params.Name == drug_name:
            return cb.parameters.Malaria_Drug_Params[idx]
    raise ValueError(f"{drug_name} not found.")


def set_drug_param(config, drug_name: str = None, parameter: str = None, value: any = None):
    """
     Set a drug parameter, by passing in drug name, parameter and the parameter value.
     Added to facilitate adding drug Resistances, example:
     artemether_drug_resistance = [{
        "Drug_Resistant_String": "A",
        "PKPD_C50_Modifier": 2.0,
        "Max_IRBC_Kill_Modifier": 0.9}]
    set_drug_param(cb, drug_name='Artemether', parameter="Resistances", value=artemether_drug_resistance)
    Args:
        config:
        drug_name: The drug that has a parameter to set
        parameter: The parameter to set
        value: The new value to set

    Returns:
        Nothing or error if drug name is not found
    """

    if not drug_name or not parameter or not value:
        raise Exception("Please pass in all: drug_name, parameter, and value.\n")
    for drug in config.parameters.Malaria_Drug_Params:
        if drug.Name == drug_name:
            drug[parameter] = value
            return  # should I return anything here?
    raise ValueError(f"{drug_name} not found.\n")


def set_species_param(cb, species, parameter, value):
    """
        Pass through for vector version of function.
    """
    return vector_config.set_species_param(cb, species, parameter, value)


def set_species(config, species_to_select):
    """
        Pass through for vector version of function.
    """
    vector_config.set_species(config, species_to_select)
