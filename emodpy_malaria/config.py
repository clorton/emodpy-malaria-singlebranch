import emod_api.config.default_from_schema_no_validation as dfs
import csv
import os

alleles = list()
mutations = dict()
traits = list()
insecticides = dict()

#
# PUBLIC API section
#

def get_file_from_http( url ):
    """
        Get data files from simple http server.
    """
    import urllib.request as req
    import tempfile
    
    path = tempfile.NamedTemporaryFile()
    path.close()
    req.urlretrieve( url, path.name )
    return path.name 


def set_team_defaults( config, mani ):
    """
        Set configuration defaults using team-wide values, including drugs and vector species.
    """
    #config.parameters.Malaria_Model = "MALARIA_MECHANISTIC_MODEL" 
    config.parameters.Malaria_Strain_Model = "FALCIPARUM_RANDOM_STRAIN"
    #config.parameters.Enable_Malaria_CoTransmission = 0


    # INFECTION
    config.parameters.PKPD_Model = "CONCENTRATION_VERSUS_TIME" 
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

    #180824 Prashanth parameters [description?]
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
    config.parameters.Parasite_Mortality_Threshold = 10**5.93
    config.parameters.Parasite_Severe_Inverse_Width = 56.5754896048744
    config.parameters.Parasite_Severe_Threshold = 10**5.929945527

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

    config.parameters.Gametocyte_Smear_Sensitivity = 0.1
    config.parameters.Parasite_Smear_Sensitivity = 0.1  # 10/uL

    # VECTOR_SIM parameters (formerly lived in dtk-tools/dtk/vector/params.py)
    config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION"
    config.parameters.Incubation_Period_Constant = 25

    config.parameters.Infectious_Period_Distribution = "EXPONENTIAL_DISTRIBUTION"
    config.parameters.Infectious_Period_Exponential = 180
    config.parameters.Base_Infectivity = 1

    config.parameters.Enable_Superinfection = 1
    config.parameters.Max_Individual_Infections = 5
    config.parameters.Infection_Updates_Per_Timestep = 1

    config.parameters.Post_Infection_Acquisition_Multiplier = 1
    config.parameters.Post_Infection_Mortality_Multiplier = 1
    config.parameters.Post_Infection_Transmission_Multiplier = 1

    config.parameters.Enable_Vector_Species_Report =  0
    config.parameters.Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
    config.parameters.Mosquito_Weight = 1

    config.parameters.Enable_Vector_Aging = 0
    config.parameters.Enable_Vector_Mortality = 1
    config.parameters.Enable_Vector_Migration = 0
    config.parameters.Enable_Vector_Migration_Human = 0
    config.parameters.Enable_Vector_Migration_Local = 0
    config.parameters.Enable_Vector_Migration_Wind = 0
    config.parameters.Enable_Temperature_Dependent_Feeding_Cycle = 0
    config.parameters.Enable_Vector_Migration_Regional = 0
    config.parameters.x_Vector_Migration_Local = 0
    config.parameters.x_Vector_Migration_Regional = 0
    config.parameters.Vector_Migration_Filename_Local = ""
    config.parameters.Vector_Migration_Filename_Regional = ""

    # placeholder param values
    config.parameters.Vector_Migration_Habitat_Modifier = 6.5
    config.parameters.Vector_Migration_Food_Modifier = 0
    config.parameters.Vector_Migration_Stay_Put_Modifier = 0.3

    config.parameters.Age_Dependent_Biting_Risk_Type = "SURFACE_AREA_DEPENDENT"
    config.parameters.Newborn_Biting_Risk_Multiplier = 0.2  # for LINEAR option (also picked up by InputEIR)
    config.parameters.Human_Feeding_Mortality = 0.1

    config.parameters.Wolbachia_Infection_Modification = 1.0
    config.parameters.Wolbachia_Mortality_Modification = 1.0
    config.parameters.HEG_Homing_Rate = 0.0
    config.parameters.HEG_Fecundity_Limiting = 0.0
    config.parameters.HEG_Model = "OFF"

    config.parameters.x_Temporary_Larval_Habitat = 1
    config.parameters.Vector_Species_Params = []
    config.parameters.Egg_Hatch_Density_Dependence = "NO_DENSITY_DEPENDENCE"
    config.parameters.Enable_Temperature_Dependent_Egg_Hatching = 0
    config.parameters.Enable_Egg_Mortality = 0
    config.parameters.Enable_Drought_Egg_Hatch_Delay = 0
    config.parameters.Temperature_Dependent_Feeding_Cycle = "NO_TEMPERATURE_DEPENDENCE"
    config.parameters.Insecticides = []
    config.parameters.Genome_Markers = []

    # Other defaults from dtk-tools transition  #fixme very likely needs pruning
    config.parameters.Base_Individual_Sample_Rate = 1
    config.parameters.Base_Mortality = 1
    config.parameters.Enable_Initial_Prevalence = 1
    config.parameters.Egg_Saturation_At_Oviposition = "SATURATION_AT_OVIPOSITION"
    config.parameters.Enable_Demographics_Initial = 1
    config.parameters.Enable_Demographics_Other = 1
    config.parameters.Enable_Demographics_Risk = 1
    config.parameters.Enable_Demographics_Reporting = 0
    config.parameters.Enable_Demographics_Birth = 0
    config.parameters.Enable_Disease_Mortality = 0
    config.parameters.Enable_Natural_Mortality = 0
    config.parameters.Enable_Nondisease_Mortality = 0
    config.parameters.Enable_Immunity = 1
    config.parameters.Enable_Initial_Prevalence = 1
    config.parameters.Enable_Rainfall_Stochasticity = 1
    config.parameters.Max_Node_Population_Samples = 40
    config.parameters.Minimum_Adult_Age_Years = 15
    config.parameters.Mortality_Blocking_Immunity_Duration_Before_Decay = 90
    config.parameters.Node_Grid_Size = 0.042
    config.parameters.Number_Substrains = 1
    config.parameters.Population_Density_C50 = 30
    config.parameters.Population_Scale_Type = "FIXED_SCALING"
    config.parameters.Post_Infection_Acquisition_Multiplier = 1
    config.parameters.Post_Infection_Mortality_Multiplier = 1
    config.parameters.Post_Infection_Transmission_Multiplier = 1
    config.parameters.Python_Script_Path = ""
    config.parameters.Susceptibility_Initialization_Distribution_Type = "DISTRIBUTION_OFF"
    config.parameters.Susceptibility_Scale_Type = "CONSTANT_SUSCEPTIBILITY"
    config.parameters.Symptomatic_Infectious_Offset = 0
    config.parameters.Transmission_Blocking_Immunity_Decay_Rate = 0.01
    config.parameters.Transmission_Blocking_Immunity_Duration_Before_Decay = 90




    # params obsolete in Jan 2018 DTK update of MalariaDiagnostic
    #config.parameters.Fever_Detection_Threshold = ... # not in config schema
    #config.parameters.PCR_Sensitivity = 20  # 0.05/u... # not in config schema
    #config.parameters.RDT_Sensitivity = 0.01  # 100/uL # not in config schema
    #config.parameters.New_Diagnostic_Sensitivity = 0.025  # 40/uL # not in config schema

    config = set_team_drug_params( config, mani )
    config = set_team_vs_params( config, mani )

    return config

def set_team_vs_params( config, mani ):
    with open( os.path.join( os.path.dirname(__file__), 'malaria_vs_params.csv' ), newline='') as csvfile:
        my_reader = csv.reader( csvfile )
        header = next(my_reader)
        drug_name_idx = header.index("Name")
        for row in my_reader:
            vsp = dfs.schema_to_config_subnode(mani.schema_file, ["idmTypes","idmType:VectorSpeciesParameters"] )
            vsp.parameters.Anthropophily = float(row[ header.index("Anthropophily") ]) 
            vsp.parameters.Name = row[ header.index("Name") ]
            vsp.parameters.Acquire_Modifier = float( row[ header.index( "Acquire_Modifier" ) ] )
            vsp.parameters.Adult_Life_Expectancy = float( row[ header.index( "Adult_Life_Expectancy" ) ] )
            vsp.parameters.Aquatic_Arrhenius_1 = float( row[ header.index( "Aquatic_Arrhenius_1" ) ] )
            vsp.parameters.Aquatic_Arrhenius_2 = float( row[ header.index( "Aquatic_Arrhenius_2" ) ] )
            vsp.parameters.Aquatic_Mortality_Rate = float( row[ header.index( "Aquatic_Mortality_Rate" ) ] )
            #vsp.parameters.Cycle_Arrhenius_1 = float( row[ header.index( "Cycle_Arrhenius_1" ) ] )
            #vsp.parameters.Cycle_Arrhenius_2 = float( row[ header.index( "Cycle_Arrhenius_2" ) ] )
            #vsp.parameters.Cycle_Arrhenius_Reduction_Factor = float( row[ header.index( "Cycle_Arrhenius_Reduction_Factor" ) ] )
            vsp.parameters.Days_Between_Feeds = float( row[ header.index( "Days_Between_Feeds" ) ] )
            vsp.parameters.Egg_Batch_Size = float( row[ header.index( "Egg_Batch_Size" ) ] )
            #vsp.parameters.Gene_To_Trait_Modifiers = float( row[ header.index( "Gene_To_Trait_Modifiers" ) ] )
            #vsp.parameters.Genes = float( row[ header.index( "Genes" ) ] )
            vsp.parameters.Immature_Duration = float( row[ header.index( "Immature_Duration" ) ] )
            vsp.parameters.Indoor_Feeding_Fraction = float( row[ header.index( "Indoor_Feeding_Fraction" ) ] )
            vsp.parameters.Infected_Arrhenius_1 = float( row[ header.index( "Infected_Arrhenius_1" ) ] )
            vsp.parameters.Infected_Arrhenius_2 = float( row[ header.index( "Infected_Arrhenius_2" ) ] )
            #vsp.parameters.Infected_Egg_Batch_Factor  = float( row[ header.index( "Infected_Egg_Batch_Factor " ) ] )
            vsp.parameters.Infectious_Human_Feed_Mortality_Factor = float( row[ header.index( "Infectious_Human_Feed_Mortality_Factor" ) ] )
            vsp.parameters.Male_Life_Expectancy = float( row[ header.index( "Male_Life_Expectancy" ) ] )
            vsp.parameters.Transmission_Rate = float( row[ header.index( "Transmission_Rate" ) ] )
            vsp.parameters.Vector_Sugar_Feeding_Frequency = row[ header.index( "Vector_Sugar_Feeding_Frequency" ) ]
            config.parameters.Vector_Species_Params.append( vsp.parameters )
    return config

def get_species_params(cb, species):
    for idx, vector_species in enumerate(cb.parameters.Vector_Species_Params):
        if vector_species.Name == species:
            return cb.parameters.Vector_Species_Params[idx]
    raise ValueError( f"{species} not found." )

def set_team_drug_params( config, mani ):
    
    # TBD: load csv with drug params and populate from that.
    with open( os.path.join( os.path.dirname(__file__), 'malaria_drug_params.csv' ), newline='') as csvfile:
        my_reader = csv.reader( csvfile )

        header = next(my_reader)
        drug_name_idx = header.index("Name")
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
            mdp = dfs.schema_to_config_subnode(mani.schema_file, ["idmTypes","idmType:MalariaDrugTypeParameters"] )
            mdp.parameters.Drug_Cmax = float(row[ drug_cmax_idx ])
            mdp.parameters.Drug_Decay_T1 = float(row[ drug_decayt1_idx ])
            mdp.parameters.Drug_Decay_T2 = float(row[ drug_decayt2_idx ])
            mdp.parameters.Drug_Vd = float(row[ drug_vd_idx ]) 
            mdp.parameters.Drug_Vd = float(row[ drug_vd_idx ]) 
            mdp.parameters.Drug_PKPD_C50 = float(row[ drug_pkpdc50_idx ])
            mdp.parameters.Drug_Fulltreatment_Doses = float(row[ drug_ftdoses_idx ]) 
            mdp.parameters.Drug_Dose_Interval = float(row[ drug_dose_interval_idx ])
            mdp.parameters.Drug_Gametocyte02_Killrate = float(row[ drug_gam02_idx ]) 
            mdp.parameters.Drug_Gametocyte34_Killrate = float(row[ drug_gam34_idx ]) 
            mdp.parameters.Drug_GametocyteM_Killrate = float(row[ drug_gamM_idx ]) 
            mdp.parameters.Drug_Hepatocyte_Killrate = float(row[ drug_hep_idx ]) 
            mdp.parameters.Max_Drug_IRBC_Kill = float(row[ drug_maxirbc_idx ]) 
            mdp.parameters.Name = row[ drug_name_idx ] 
            #mdp.parameters.Drug_Adherence_Rate = float(row[ drug_adher_idx ]) 
            mdp.parameters.Bodyweight_Exponent = float(row[ drug_bwexp_idx ]) 

            try:
                ages = [ float(x) for x in row[ drug_fracdos_key_idx ].strip('[]').split(",") ]
                values = [ float(x) for x in row[ drug_fracdos_val_idx ].strip('[]').split(",") ]
            except Exception as ex:
                print( str( ex ) )
                ages = []
                values = []
            for idx in range(len(ages)):
                fdbua = dict()
                # this is what we want but not ready yet 
                #fdbua = dfs.schema_to_config_subnode(mani.schema_file, ["idmTypes","idmType:DoseMap"] ) 
                #fdbua.Upper_Age_In_Years = ages[idx]
                #fdbua.Fraction_Of_Adult_Dose = values[idx]
                fdbua[ "Upper_Age_In_Years" ] = ages[idx]
                fdbua[ "Fraction_Of_Adult_Dose" ] = values[idx]
                #fdbua.finalize()
                mdp.parameters.Fractional_Dose_By_Upper_Age.append( fdbua )

            config.parameters.Malaria_Drug_Params.append( mdp.parameters )
    # end
    
    return config

def get_drug_params(cb, drug_name):
    for idx, drug_params in enumerate(cb.parameters.Malaria_Drug_Params):
        if drug_params.Name == drug_name:
            return cb.parameters.Malaria_Drug_Params[idx]
    raise ValueError( f"{drug_name} not found." )

def set_species( config, species_to_select ):
    """
        Use this function to specify which mosquito species to use in the simulation.

        Args:
            config: schema-backed config smart dict
            species_to_list: list of 1 or more strings.

        Returns:
            None
    """

    if type(species_to_select) is str:
        sts = species_to_select 
        species_to_select = list()
        species_to_select.append( sts )
        
    if len(species_to_select) == 0:
        raise ValueError( f"{species_to_select} can not be empty in set_species." )

    new_vsp = list()
    for idx in range(len(config.parameters.Vector_Species_Params)):
        vsp = config.parameters.Vector_Species_Params[ idx ]
        if vsp.Name in species_to_select:
            new_vsp.append( vsp )
            species_to_select.remove( vsp.Name )

    if len(species_to_select) > 0:
        raise ValueError( f"Not able to find {species_to_select} in vector species lookup list." )
    else:
        config.parameters.Vector_Species_Params = new_vsp


def set_resistances( config ):
    """
    Use this function after you're done calling add_resistance. config is the input and the output
    """
    for name, insect in insecticides.items():
        config.parameters.Insecticides.append( insect.parameters ) 
    return config

def add_alleles( allele_names_in, allele_inits_in ):
    """ 
    This is public API function for user to add alleles. User specifies the list of alleles and corresponding initial distribution.
    """
    # This is just wrong.
    allele_dict = _allele_data_to_dict( allele_names_in, allele_inits_in )
    alleles.append( allele_dict )

def add_mutation( from_allele, to_allele, rate ):
    # Need to worry about allele sets
    """ 
    Public API function for user to add mutations as part of vector genetics configuration.
    A mutation is specified with a source allele, a destination allele, and a rate
    """
    mut_dict = dict()
    key = f"{from_allele}:{to_allele}"
    mut_dict[ key ] = rate
    allele_set_uniq_key = _get_allele_set_key_from_allele( from_allele )
    if allele_set_uniq_key not in mutations:
        mutations[ allele_set_uniq_key ] = dict()
    mutations[allele_set_uniq_key].update( mut_dict )

def add_trait( manifest, sex_genes, allele_pair, trait_name, trait_value ):

    """ 
    Use this function to add traits as part of vector genetics configuration.
    Should produce something like:: 

        {
           "Allele_Combinations": [["X", "X"],["a0", "a1"]],
           "Trait_Modifiers": {"INFECTED_BY_HUMAN": 0}
        },
    """
    if len(sex_genes) != 2 or sex_genes[0] not in [ "X", "Y" ] or sex_genes[1] not in [ "X", "Y" ]:
        raise ValueError( "sex_genes needs to have two values and can only be X or Y" )
    if len(allele_pair) != 2:
        raise ValueError( "allele_pair should have 2 values" )
    # TBD: Add check that the alleles referenced here have been 'declared' previously
    trait = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:GeneToTraitModifierConfig"] )
    trait.parameters.Allele_Combinations.append( sex_genes )
    trait.parameters.Allele_Combinations.append( allele_pair )

    # Trait_Modifiers is a keys-as-value thing so don't really have any schema help here.  
    trait_mod = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:TraitModifier"] )
    trait_mod.parameters.Trait = trait_name
    trait_mod.parameters.Modifier = trait_value 
    trait.parameters.Trait_Modifiers.append( trait_mod.parameters )
    # Store these and put them in config later
    traits.append( trait )

def add_resistance( manifest, insecticide_name, species, combo, blocking = 1.0, killing = 1.0 ):
    """
        Use this function to add insecticide resistances. An insecticide can have a list of resistances.
        Add each resistance separately with the same name::
    
            Insecticides = [
            {
              "Name": "pyrethroid",
              "Resistances": [
                {
                  "Allele_Combinations": [
                  [
                    "a1",
                    "a1"
                  ]
                 ],
                "Blocking_Modifier": 1.0,
                "Killing_Modifier": pyrethroid_killing,
                "Species": "gambiae"
              }
             ]
            },
    """
    def get_insecticide_by_name( insecticide_name ): 
        if insecticide_name in insecticides:
            #  print( "Found existing insecticide." )
            return insecticides[ insecticide_name ]

        new_insecticide = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:Insecticide"] )
        new_insecticide.parameters.Name = insecticide_name
        insecticides[ insecticide_name ] = new_insecticide
        #  print( "New insecticide." )
        return new_insecticide 

    insecticide = get_insecticide_by_name( insecticide_name )

    resistance = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:AlleleComboProbabilityConfig"] )
    resistance.parameters.Blocking_Modifier = blocking
    resistance.parameters.Killing_Modifier = killing
    resistance.parameters.Species = species
    resistance.parameters.Allele_Combinations = combo
    insecticide.parameters.Resistances.append( resistance.parameters )

# 
# INTERNAL VEC-GEN FUNCTIONS
#
def _allele_data_to_dict( allele_names, allele_values ):
    """
    This function creates a dictionary out of matching names and values arrays.
    The user shouldn't have to create dicts.
    """
    allele_dict = {}
    for idx in range(len(allele_names) ):
        allele = allele_names[ idx ]
        value = allele_values[ idx ]
        allele_dict[ allele ] = value
    return allele_dict

def set_genetics( vsp, manifest ):
    """ 
    Don't need to pass these anymore since they are module variables. But actually need to try with more than
    one set and see where I end up in terms of design.
    """
    for allele_dict in alleles:
    #for 
    #for all_idx in range(len(allele_names)):
        genes = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:VectorGene"] )
        for allele_name, allele_value in allele_dict.items():
            allele_from_schema = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:VectorAllele"] )
            allele_from_schema.parameters.Name = allele_name
            allele_from_schema.parameters.Initial_Allele_Frequency = allele_value
            genes.parameters.Alleles.append( allele_from_schema.parameters )
            allele_set_uniq_key = [ x for x in allele_dict.keys() ][ 0 ] # get 'hash' for dict
            if allele_set_uniq_key  in mutations.keys():
                mut_dict = mutations[allele_set_uniq_key]
                for mut_key, mut_value in mut_dict.items():
                    mutation = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:VectorAlleleMutation"] )
                    mutation.parameters.Mutate_From = mut_key.split(":")[0]
                    mutation.parameters.Mutate_To  = mut_key.split(":")[1]
                    mutation.parameters.Probability_Of_Mutation  = mut_value
                    mutation.parameters.finalize()
                    # Mutations - each element has three parameters "Mutate_From", "Mutate_To", and "Probability_Of_Mutation"
                    genes.parameters.Mutations.append( mutation.parameters )
        vsp.Genes.append( genes.parameters ) # too many 'parameters' 
    for trait in traits:
        vsp.Gene_To_Trait_Modifiers.append( trait.parameters )
    return vsp

def _get_allele_set_key_from_allele( allele_in ):
    """
    An internal utility function that gets the 'hash' to use as the key into the mutations dict for any given allele.
    """
    # Loop through allele_names and find list where this allele exists. Then get first element in that list.
    ret_key = None 
    #for allele_name, allele_value in alleles.items():
    #    if allele_in == allele_name:
    #        keys_list = [ x for x in alleles.keys() ]
    for allele_set in alleles:
        if allele_in in allele_set.keys():
            keys_list = [ x for x in allele_set.keys() ]
            ret_key = keys_list[0]
            break

    return ret_key 

