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
def set_team_defaults(config, mani):
    """
        Set configuration defaults using team-wide values, including drugs and vector species.
    """
    # INFECTION
    config.parameters.Simulation_Type = "VECTOR_SIM"
    config.parameters.Infection_Updates_Per_Timestep = 8
    config.parameters.Incubation_Period_Constant = 7
    config.parameters.Infectious_Period_Constant = 10
    #config.parameters.Number_Substrains = 1

    # VECTOR_SIM parameters (formerly lived in dtk-tools/dtk/vector/params.py)
    config.parameters.Enable_Vector_Species_Report = 0
    config.parameters.Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
    config.parameters.Mosquito_Weight = 1

    config.parameters.Enable_Vector_Aging = 0
    config.parameters.Enable_Vector_Mortality = 1
    config.parameters.Enable_Vector_Migration = 0
    config.parameters.Enable_Vector_Migration_Local = 0
    config.parameters.Enable_Vector_Migration_Regional = 0

    # placeholder param values
    config.parameters.Vector_Migration_Habitat_Modifier = 6.5
    config.parameters.Vector_Migration_Food_Modifier = 0
    config.parameters.Vector_Migration_Stay_Put_Modifier = 0.3

    config.parameters.Age_Dependent_Biting_Risk_Type = "SURFACE_AREA_DEPENDENT"
    config.parameters.Human_Feeding_Mortality = 0.1

    config.parameters.Wolbachia_Infection_Modification = 1.0
    config.parameters.Wolbachia_Mortality_Modification = 1.0

    config.parameters.x_Temporary_Larval_Habitat = 1
    config.parameters.Vector_Species_Params = []
    config.parameters.Egg_Hatch_Density_Dependence = "NO_DENSITY_DEPENDENCE"
    config.parameters.Enable_Temperature_Dependent_Egg_Hatching = 0
    config.parameters.Enable_Egg_Mortality = 0
    config.parameters.Enable_Drought_Egg_Hatch_Delay = 0
    config.parameters.Insecticides = []
    config.parameters.Genome_Markers = []

    # Other defaults from dtk-tools transition  #fixme very likely needs pruning
    config.parameters.Egg_Saturation_At_Oviposition = "SATURATION_AT_OVIPOSITION"
    config.parameters.Enable_Demographics_Risk = 1
    config.parameters.Enable_Demographics_Reporting = 0
    config.parameters.Enable_Demographics_Birth = 0
    config.parameters.Enable_Disease_Mortality = 0
    config.parameters.Enable_Natural_Mortality = 0
    config.parameters.Enable_Rainfall_Stochasticity = 1
    config.parameters.Minimum_Adult_Age_Years = 15
    config.parameters.Node_Grid_Size = 0.042
    config.parameters.Population_Density_C50 = 30
    config.parameters.Population_Scale_Type = "FIXED_SCALING"

    # setting up parameters for climate constant
    config.parameters.Base_Rainfall = 10
    config.parameters.Base_Air_Temperature = 27
    config.parameters.Base_Land_Temperature = 27
    config.parameters.Base_Relative_Humidity = 0.75
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"

    config.parameters.Simulation_Duration = 365

    config = set_team_vs_params(config, mani)

    return config


def set_team_vs_params(config, mani):
    with open(os.path.join(os.path.dirname(__file__), 'malaria_vs_params.csv'), newline='') as csvfile:
        my_reader = csv.reader(csvfile)
        header = next(my_reader)
        drug_name_idx = header.index("Name")
        for row in my_reader:
            vsp = dfs.schema_to_config_subnode(mani.schema_file, ["idmTypes", "idmType:VectorSpeciesParameters"])
            vsp.parameters.Anthropophily = float(row[header.index("Anthropophily")])
            vsp.parameters.Name = row[header.index("Name")]
            vsp.parameters.Acquire_Modifier = float(row[header.index("Acquire_Modifier")])
            vsp.parameters.Adult_Life_Expectancy = float(row[header.index("Adult_Life_Expectancy")])
            vsp.parameters.Aquatic_Arrhenius_1 = float(row[header.index("Aquatic_Arrhenius_1")])
            vsp.parameters.Aquatic_Arrhenius_2 = float(row[header.index("Aquatic_Arrhenius_2")])
            vsp.parameters.Aquatic_Mortality_Rate = float(row[header.index("Aquatic_Mortality_Rate")])
            # vsp.parameters.Cycle_Arrhenius_1 = float( row[ header.index( "Cycle_Arrhenius_1" ) ] )
            # vsp.parameters.Cycle_Arrhenius_2 = float( row[ header.index( "Cycle_Arrhenius_2" ) ] )
            # vsp.parameters.Cycle_Arrhenius_Reduction_Factor = float( row[ header.index( "Cycle_Arrhenius_Reduction_Factor" ) ] )
            vsp.parameters.Days_Between_Feeds = float(row[header.index("Days_Between_Feeds")])
            vsp.parameters.Egg_Batch_Size = float(row[header.index("Egg_Batch_Size")])
            # vsp.parameters.Gene_To_Trait_Modifiers = float( row[ header.index( "Gene_To_Trait_Modifiers" ) ] )
            # vsp.parameters.Genes = float( row[ header.index( "Genes" ) ] )
            vsp.parameters.Immature_Duration = float(row[header.index("Immature_Duration")])
            vsp.parameters.Indoor_Feeding_Fraction = float(row[header.index("Indoor_Feeding_Fraction")])
            vsp.parameters.Infected_Arrhenius_1 = float(row[header.index("Infected_Arrhenius_1")])
            vsp.parameters.Infected_Arrhenius_2 = float(row[header.index("Infected_Arrhenius_2")])
            # vsp.parameters.Infected_Egg_Batch_Factor  = float( row[ header.index( "Infected_Egg_Batch_Factor " ) ] )
            vsp.parameters.Infectious_Human_Feed_Mortality_Factor = float(
                row[header.index("Infectious_Human_Feed_Mortality_Factor")])
            vsp.parameters.Male_Life_Expectancy = float(row[header.index("Male_Life_Expectancy")])
            vsp.parameters.Transmission_Rate = float(row[header.index("Transmission_Rate")])
            vsp.parameters.Vector_Sugar_Feeding_Frequency = row[header.index("Vector_Sugar_Feeding_Frequency")]
            vsp.parameters.Larval_Habitat_Types = [{"Vector_Habitat_Type": row[header.index("LHT1_Key")],
                                                    "Max_Larval_Capacity": float(row[header.index("LHT1_Value")])}]
            if row[header.index("LHT2_Key")]:
                vsp.parameters.Larval_Habitat_Types.append({"Vector_Habitat_Type": row[header.index("LHT2_Key")],
                                                            "Max_Larval_Capacity": float(
                                                                row[header.index("LHT2_Value")])})

            config.parameters.Vector_Species_Params.append(vsp.parameters)
    return config


def get_species_params(cb, species):
    for idx, vector_species in enumerate(cb.parameters.Vector_Species_Params):
        if vector_species.Name == species:
            return cb.parameters.Vector_Species_Params[idx]
    raise ValueError(f"{species} not found.")


def set_species(config, species_to_select):
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
        species_to_select.append(sts)

    if len(species_to_select) == 0:
        raise ValueError(f"{species_to_select} can not be empty in set_species.")

    new_vsp = list()
    for idx in range(len(config.parameters.Vector_Species_Params)):
        vsp = config.parameters.Vector_Species_Params[idx]
        if vsp.Name in species_to_select:
            new_vsp.append(vsp)
            species_to_select.remove(vsp.Name)

    if len(species_to_select) > 0:
        raise ValueError(f"Not able to find {species_to_select} in vector species lookup list.")
    else:
        config.parameters.Vector_Species_Params = new_vsp


def set_resistances(config):
    """
    Use this function after you're done calling add_resistance. config is the input and the output
    """
    for name, insect in insecticides.items():
        config.parameters.Insecticides.append(insect.parameters)
    return config


def add_alleles(allele_names_in, allele_inits_in):
    """ 
    This is public API function for user to add alleles. User specifies the list of alleles and corresponding initial distribution.
    """
    # This is just wrong.
    allele_dict = _allele_data_to_dict(allele_names_in, allele_inits_in)
    alleles.append(allele_dict)


def add_mutation(from_allele, to_allele, rate):
    # Need to worry about allele sets
    """ 
    Public API function for user to add mutations as part of vector genetics configuration.
    A mutation is specified with a source allele, a destination allele, and a rate
    """
    mut_dict = dict()
    key = f"{from_allele}:{to_allele}"
    mut_dict[key] = rate
    allele_set_uniq_key = _get_allele_set_key_from_allele(from_allele)
    if allele_set_uniq_key not in mutations:
        mutations[allele_set_uniq_key] = dict()
    mutations[allele_set_uniq_key].update(mut_dict)


def add_trait(manifest, allele_combo, trait_name, trait_value):
    """
    Use this function to add traits as part of vector genetics configuration.
    Should produce something like:: 

        {
           "Allele_Combinations": [["X", "X"],["a0", "a1"]],
           "Trait_Modifiers": {"INFECTED_BY_HUMAN": 0}
        },
    """
    if len(allele_combo) == 0:
        raise ValueError("allele_combo must define some alleles to target")
    for combo in allele_combo:
        if (len(combo) != 2):
            raise ValueError(
                "Each combo in allele_combo must have two values - one for each chromosome, '*' is acceptable")

    # TBD: Add check that the alleles referenced here have been 'declared' previously
    trait = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:GeneToTraitModifierConfig"])
    trait.parameters.Allele_Combinations = allele_combo

    # Trait_Modifiers is a keys-as-value thing so don't really have any schema help here.  
    trait_mod = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:TraitModifier"])
    trait_mod.parameters.Trait = trait_name
    trait_mod.parameters.Modifier = trait_value
    trait.parameters.Trait_Modifiers.append(trait_mod.parameters)
    # Store these and put them in config later
    traits.append(trait)


def add_resistance(manifest, insecticide_name, species, combo, blocking=1.0, killing=1.0, repelling=1.0,
                   larval_killing=1.0):
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

    def get_insecticide_by_name(insecticide_name):
        if insecticide_name in insecticides:
            #  print( "Found existing insecticide." )
            return insecticides[insecticide_name]

        new_insecticide = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:Insecticide"])
        new_insecticide.parameters.Name = insecticide_name
        insecticides[insecticide_name] = new_insecticide
        #  print( "New insecticide." )
        return new_insecticide

    insecticide = get_insecticide_by_name(insecticide_name)

    resistance = dfs.schema_to_config_subnode(manifest.schema_file,
                                              ["idmTypes", "idmType:AlleleComboProbabilityConfig"])
    resistance.parameters.Blocking_Modifier = blocking
    resistance.parameters.Killing_Modifier = killing
    resistance.parameters.Repelling_Modifier = repelling
    resistance.parameters.Larval_Killing_Modifier = larval_killing
    resistance.parameters.Species = species
    resistance.parameters.Allele_Combinations = combo
    insecticide.parameters.Resistances.append(resistance.parameters)


#
# INTERNAL VEC-GEN FUNCTIONS
#
def _allele_data_to_dict(allele_names, allele_values):
    """
    This function creates a dictionary out of matching names and values arrays.
    The user shouldn't have to create dicts.
    """
    allele_dict = {}
    for idx in range(len(allele_names)):
        allele = allele_names[idx]
        value = allele_values[idx]
        allele_dict[allele] = value
    return allele_dict


def set_genetics(vsp, manifest):
    """ 
    Don't need to pass these anymore since they are module variables. But actually need to try with more than
    one set and see where I end up in terms of design.
    """
    for allele_dict in alleles:
        # for
        # for all_idx in range(len(allele_names)):
        genes = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorGene"])
        for allele_name, allele_value in allele_dict.items():
            allele_from_schema = dfs.schema_to_config_subnode(manifest.schema_file,
                                                              ["idmTypes", "idmType:VectorAllele"])
            allele_from_schema.parameters.Name = allele_name
            allele_from_schema.parameters.Initial_Allele_Frequency = allele_value
            genes.parameters.Alleles.append(allele_from_schema.parameters)
            allele_set_uniq_key = [x for x in allele_dict.keys()][0]  # get 'hash' for dict
            if allele_set_uniq_key in mutations.keys():
                mut_dict = mutations[allele_set_uniq_key]
                for mut_key, mut_value in mut_dict.items():
                    mutation = dfs.schema_to_config_subnode(manifest.schema_file,
                                                            ["idmTypes", "idmType:VectorAlleleMutation"])
                    mutation.parameters.Mutate_From = mut_key.split(":")[0]
                    mutation.parameters.Mutate_To = mut_key.split(":")[1]
                    mutation.parameters.Probability_Of_Mutation = mut_value
                    mutation.parameters.finalize()
                    # Mutations - each element has three parameters "Mutate_From", "Mutate_To", and "Probability_Of_Mutation"
                    genes.parameters.Mutations.append(mutation.parameters)
        vsp.Genes.append(genes.parameters)  # too many 'parameters'
    for trait in traits:
        vsp.Gene_To_Trait_Modifiers.append(trait.parameters)
    return vsp


def _get_allele_set_key_from_allele(allele_in):
    """
    An internal utility function that gets the 'hash' to use as the key into the mutations dict for any given allele.
    """
    # Loop through allele_names and find list where this allele exists. Then get first element in that list.
    ret_key = None
    # for allele_name, allele_value in alleles.items():
    #    if allele_in == allele_name:
    #        keys_list = [ x for x in alleles.keys() ]
    for allele_set in alleles:
        if allele_in in allele_set.keys():
            keys_list = [x for x in allele_set.keys()]
            ret_key = keys_list[0]
            break

    return ret_key
