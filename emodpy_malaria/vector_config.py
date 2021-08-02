import emod_api.config.default_from_schema_no_validation as dfs
import csv
import os

#
# PUBLIC API section
#
def set_team_defaults(config, manifest):
    """
    Set configuration defaults using team-wide values, including drugs and vector species.

    Args:
        config:
        manifest:

    Returns:
        configured config
    """

    # INFECTION
    config.parameters.Simulation_Type = "VECTOR_SIM"
    config.parameters.Infection_Updates_Per_Timestep = 8
    config.parameters.Incubation_Period_Constant = 7
    config.parameters.Infectious_Period_Constant = 10

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
    config.parameters.Inset_Chart_Reporting_Include_30Day_Avg_Infection_Duration = 0
    config.parameters.Simulation_Duration = 365
    config = add_species(config, manifest, ["gambiae", "funestus", "arabiensis"])

    return config


def get_species_params(config, species: str = None):
    """
    Returns the species parameters dictionary with the matching species **Name**

    Args:
        config:
        species: Species to look up

    Returns:
        Dictionary of species paramteres with the matching name
    """
    for idx, vector_species in enumerate(config.parameters.Vector_Species_Params):
        if vector_species.Name == species:
            return config.parameters.Vector_Species_Params[idx]
    raise ValueError(f"{species} not found.")


def set_species_param(config, species, parameter, value, overwrite=False):
    """
        Sets a parameter value for a specific species.
        Raises value error if species not found

    Args:
        config:
        species: name of species for which to set the parameter
        parameter: parameter to set
        value: value to set the parameter to
        overwrite: if set to True and parameter is a list, overwrites the parameter with value, appends by default

    Returns:
        Nothing
    """
    for vector_species in config.parameters.Vector_Species_Params:
        if vector_species.Name == species:
            if parameter in vector_species and isinstance(vector_species[parameter], list) and not overwrite:
                if isinstance(value, list):
                    for val in value:
                        vector_species[parameter].append(val)
            else:
                vector_species[parameter] = value
            return
    raise ValueError(f"Species {species} not found.\n")


def add_species(config, manifest, species_to_select):
    """
    Adds species with preset parameters from 'malaria_vector_species_params.csv', if species
    name not found - "gambiae" parameters are added and the new species name assigned.

    Args:
        config: schema-backed config smart dict
        manifest:
        species_to_select: a list of species or a name of a single species you'd like to set from
            malaria_vector_species_params.csv

    Returns:
        configured config
    """

    if type(species_to_select) is str:
        species_to_select = [species_to_select]

    for species in species_to_select:
        found = False
        with open(os.path.join(os.path.dirname(__file__), 'malaria_vector_species_params.csv'),
                  newline='') as csvfile:
            my_reader = csv.reader(csvfile)
            header = next(my_reader)
            for row in my_reader:
                if species == row[header.index("Name")]:
                    found = True
                    vsp = dfs.schema_to_config_subnode(manifest.schema_file,
                                                       ["idmTypes", "idmType:VectorSpeciesParameters"])
                    vsp.parameters.Anthropophily = float(row[header.index("Anthropophily")])
                    vsp.parameters.Name = row[header.index("Name")]
                    vsp.parameters.Acquire_Modifier = float(row[header.index("Acquire_Modifier")])
                    vsp.parameters.Adult_Life_Expectancy = float(row[header.index("Adult_Life_Expectancy")])
                    vsp.parameters.Aquatic_Arrhenius_1 = float(row[header.index("Aquatic_Arrhenius_1")])
                    vsp.parameters.Aquatic_Arrhenius_2 = float(row[header.index("Aquatic_Arrhenius_2")])
                    vsp.parameters.Aquatic_Mortality_Rate = float(row[header.index("Aquatic_Mortality_Rate")])
                    vsp.parameters.Days_Between_Feeds = float(row[header.index("Days_Between_Feeds")])
                    vsp.parameters.Egg_Batch_Size = float(row[header.index("Egg_Batch_Size")])
                    vsp.parameters.Immature_Duration = float(row[header.index("Immature_Duration")])
                    vsp.parameters.Indoor_Feeding_Fraction = float(row[header.index("Indoor_Feeding_Fraction")])
                    vsp.parameters.Infected_Arrhenius_1 = float(row[header.index("Infected_Arrhenius_1")])
                    vsp.parameters.Infected_Arrhenius_2 = float(row[header.index("Infected_Arrhenius_2")])
                    vsp.parameters.Infectious_Human_Feed_Mortality_Factor = float(
                        row[header.index("Infectious_Human_Feed_Mortality_Factor")])
                    vsp.parameters.Male_Life_Expectancy = float(row[header.index("Male_Life_Expectancy")])
                    vsp.parameters.Transmission_Rate = float(row[header.index("Transmission_Rate")])
                    vsp.parameters.Vector_Sugar_Feeding_Frequency = row[header.index("Vector_Sugar_Feeding_Frequency")]
                    vsp.parameters.Larval_Habitat_Types = [{"Vector_Habitat_Type": row[header.index("LHT1_Key")],
                                                            "Max_Larval_Capacity": float(
                                                                row[header.index("LHT1_Value")])}]
                    if row[header.index("LHT2_Key")]:
                        vsp.parameters.Larval_Habitat_Types.append(
                            {"Vector_Habitat_Type": row[header.index("LHT2_Key")],
                             "Max_Larval_Capacity": float(
                                 row[header.index("LHT2_Value")])})

                    config.parameters.Vector_Species_Params.append(vsp.parameters)

        if not found:
            add_species(config, manifest, "gambiae")
            set_species_param(config, "gambiae", "Name", species)
            print(f"{species} not found in list, adding 'gambiae' settings and renaming to '{species}', \n"
                  f"you can edit the settings via set_species_params().\n")

    return config


def add_alleles(config, manifest, species: str = None, alleles: list = None):
    """
    Adds alleles to a species

    Args:
        config:
        manifest:
        species: species to which to assign the alleles
        alleles: List of tuples of (**Name**, **Initial_Allele_Frequency**) for a set of alleles
            **Example**::

            [("a0", 0.5), ("a1", 0.35), ("a2", 0.15)]

    Returns:
        configured config
    """

    if not species or not alleles or not config or not manifest:
        raise ValueError("Please set all parameters, 'alleles' needs to be a list of tuples.\n")

    gene = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorGene"])
    for index, allele in enumerate(alleles):
        vector_allele = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorAllele"])
        vector_allele.parameters.Name = allele[0]
        vector_allele.parameters.Initial_Allele_Frequency = allele[1]
        gene.parameters.Alleles.append(vector_allele.parameters)

    species_params = get_species_params(config, species)
    species_params.Genes.append(gene.parameters)
    return config


def add_mutation(config, manifest, species, mutate_from, mutate_to, probability):
    """
    Adds to **Mutations** parameter in a Gene which has the matching **Alleles**

    Args:
        config:
        manifest:
        species: Name of vector species to which we're adding mutations
        mutate_from: The allele in the gamete that could mutate
        mutate_to: The allele that this locus will change to during gamete generation
        probability: The probability that the allele will mutate from one allele to the other during the
            creation of the gametes

    Returns:
        configured config
    """

    species_params = get_species_params(config, species)
    found = False
    for gene in species_params["Genes"]:
        allele_names = []
        for allele in gene["Alleles"]:
            allele_names.append(allele["Name"])
        if mutate_from in allele_names and mutate_to in allele_names:
            found = True
            mutations = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorAlleleMutation"])
            mutations.parameters.Mutate_From = mutate_from
            mutations.parameters.Mutate_To = mutate_to
            mutations.parameters.Probability_Of_Mutation = probability
            gene.Mutations.append(mutations.parameters)

    if not found:
        raise ValueError(f"Allele name(s) '{mutate_from}' and/or '{mutate_to}' were not found for {species}.\n")

    return config


def add_trait(config, manifest, species, allele_combo: list = None, trait_modifiers: list = None):
    """
    Use this function to add traits as part of vector genetics configuration, the trait is assigned to the
    species' **Gene_To_Trait_Modifiers** parameter
    Should produce something like **Example**::

                {
                    "Allele_Combinations" : [
                        [  "X",  "X" ],
                        [ "a0", "a1" ]
                    ],
                    "Trait_Modifiers" : [
                        {
                            "Trait" : "FECUNDITY",
                            "Modifier": 0.7
                        }
                    ]
                }

    Args:
        config:
        manifest:
        species: **Name** of species for which to add this  **Gene_To_Trait_Modifiers**
        allele_combo: List of lists, This defines a possible subset of allele pairs that a vector could have.
            Each pair are alleles from one gene.  If the vector has this subset, then the associated traits will
            be adjusted.  Order does not matter.  '*' is allowed when only the occurrence of one allele is important.
            **Example**::

            [[  "X",  "X" ], [ "a0", "a1" ]]

        trait_modifiers:  List of tuples of (**Trait**, **Modifier**) for the *Allele_Combinations**
            **Example**::

            [("FECUNDITY", 0.5), ("X_SHRED", 0.80)]

    Returns:
        configured config
    """

    if len(allele_combo) == 0:
        raise ValueError("allele_combo must define some alleles to target")
    for combo in allele_combo:
        if len(combo) != 2:
            raise ValueError(
                "Each combo in allele_combo must have two values - one for each chromosome, '*' is acceptable")

    species_params = get_species_params(config, species)
    # Check that the alleles referenced here have been 'declared' previously
    allele_names = []
    allele_names_in_combo = []
    for gene in species_params.Genes:
        for allele in gene["Alleles"]:
            allele_names.append(allele["Name"])

    for combo in allele_combo:
        for allele_name in combo:
            if allele_name != "X" and allele_name != "Y" and allele_name != "*":
                allele_names_in_combo.append(allele_name)

    for alnic in allele_names_in_combo:
        if alnic not in allele_names:
            raise ValueError(f"Allele name {alnic} submitted in one of the allele_combos is not found"
                             f" in Genes parameterf for {species}.\n")

    trait = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:GeneToTraitModifierConfig"])
    trait.parameters.Allele_Combinations = allele_combo

    for index, trait_modifier in enumerate(trait_modifiers):
        trait_mod = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:TraitModifier"])
        trait_mod.parameters.Trait = trait_modifier[0]
        trait_mod.parameters.Modifier = trait_modifier[1]
        trait.parameters.Trait_Modifiers.append(trait_mod.parameters)

    species_params.Gene_To_Trait_Modifiers.append(trait.parameters)

    return config


def add_insecticide_resistance(config, manifest, insecticide_name: str = "", species: str = "",
                               allele_combo: list = None, blocking: float = 1.0, killing: float = 1.0,
                               repelling: float = 1.0, larval_killing: float = 1.0):
    """
        Use this function to add to the list of **Resistances** parameter for a specific insecticide
        Add each resistance separately.
        **Example**::

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
                "Killing_Modifier": 0.85,
                "Repelling_Modifier": 0.72,
                "Larval_Killing_Modifier": 0,
                "Species": "gambiae"
              }
             ]
            },
            {..}

    Args:
        config:
        manifest:
        insecticide_name: The name of the insecticide to which attach the resistance.
        species: Name of the species of vectors.
        allele_combo: List of combination of alleles that vectors must have in order to be resistant.
        blocking: The value used to modify (multiply) the blocking effectivity of an intervention.
        killing: The value used to modify (multiply) the killing effectivity of an intervention.
        repelling: The value used to modify (multiply) the repelling effectivity of an intervention.
        larval_killing: The value used to modify (multiply) the larval killing effectivity of an intervention.

    Returns:
        configured config
    """
    resistance = dfs.schema_to_config_subnode(manifest.schema_file,
                                              ["idmTypes", "idmType:AlleleComboProbabilityConfig"])
    resistance.parameters.Blocking_Modifier = blocking
    resistance.parameters.Killing_Modifier = killing
    resistance.parameters.Repelling_Modifier = repelling
    resistance.parameters.Larval_Killing_Modifier = larval_killing
    resistance.parameters.Species = species
    resistance.parameters.Allele_Combinations = allele_combo

    insecticides = config.parameters.Insecticides
    for an_insecticide in insecticides:
        if an_insecticide.Name == insecticide_name:
            an_insecticide.Resistances.append(resistance.parameters)
            return config

    new_insecticide = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:Insecticide"])
    new_insecticide.parameters.Name = insecticide_name
    new_insecticide.parameters.Resistances.append(resistance.parameters)
    config.parameters.Insecticides.append(new_insecticide.parameters)

    return config


def add_species_drivers(config, manifest, species: str = "", driving_allele: str = "", driver_type: str = "CLASSIC",
                        to_copy: str = "", to_replace: str = "", likelihood_list: list = None):
    """
        Adds one **Alleles_Driven** item to the Alleles_Driven list, using **Driving_Allele** as key if matching one
        already exists.
        **Example**::

            {
                "Driver_Type": "INTEGRAL_AUTONOMOUS",
                "Driving_Allele": "Ad",
                "Alleles_Driven": [
                    {
                        "Allele_To_Copy": "Ad",
                        "Allele_To_Replace": "Aw",
                        "Copy_To_Likelihood": [
                            {
                                "Copy_To_Allele": "Aw",
                                "Likelihood": 0.1
                            },
                            {
                                "Copy_To_Allele": "Ad",
                                "Likelihood": 0.3
                            },
                            {
                                "Copy_To_Allele": "Am",
                                "Likelihood": 0.6
                            }
                        ]
                    },
                                                {
                        "Allele_To_Copy": "Ce",
                        "Allele_To_Replace": "Cw",
                        "Copy_To_Likelihood": [
                            {
                                "Copy_To_Allele": "Cw",
                                "Likelihood": 0.1
                            },
                            {
                                "Copy_To_Allele": "Ce",
                                "Likelihood": 0.3
                            },
                            {
                                "Copy_To_Allele": "Cm",
                                "Likelihood": 0.6
                            }
                        ]
                    }
                ]
            }

    Args:
        config:
        manifest:
        species: Name of the species for which we're setting the drivers
        driving_allele: This is the allele that is known as the driver
        driver_type: This indicates the type of driver.
            CLASSIC-The driver can only drive if the one gamete has the driving allele and the other has a specific
            allele to be replaced
            INTEGRAL_AUTONOMOUS-At least one of the gametes must have the driver.  Alleles can still be driven if the
            driving allele is in both gametes or even if the driving allele cannot replace the allele in the
            other gamete
        to_copy: The main allele to be copied **Allele_To_Copy**
        to_replace: The allele that must exist and will be replaced by the copy **Allele_To_Replace**
        likelihood_list: A list of tuples in format: [(**Copy_To_Allele**, **Likelihood**),(),()] to assign to
            **Copy_To_Likelyhood** list

    Returns:
        configured config
    """

    if not config or not manifest or not species or not driving_allele or not to_copy or not to_replace or not likelihood_list:
        raise ValueError(f"Please define all the parameters for this function.\n")

    species_params = get_species_params(config, species)
    allele_driven = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:AlleleDriven"])
    allele_driven.parameters.Allele_To_Copy = to_copy
    allele_driven.parameters.Allele_To_Replace = to_replace
    for index, likely in enumerate(likelihood_list):
        c2likelyhood = dfs.schema_to_config_subnode(manifest.schema_file,
                                                    ["idmTypes", "idmType:CopyToAlleleLikelihood"])
        c2likelyhood.parameters.Copy_To_Allele = likely[0]
        c2likelyhood.parameters.Likelihood = likely[1]
        allele_driven.parameters.Copy_To_Likelihood.append(c2likelyhood.parameters)

    # check if the Driving_Allele already exists
    if "Drivers" in species_params:
        for driver in species_params.Drivers:
            if driving_allele == driver["Driving_Allele"]:
                driver["Alleles_Driven"].append(allele_driven.parameters)
                return config

    gene_driver = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorGeneDriver"])
    gene_driver.parameters.Driving_Allele = driving_allele
    gene_driver.parameters.Driver_Type = driver_type

    gene_driver.parameters.Alleles_Driven.append(allele_driven.parameters)
    species_params.Drivers.append(gene_driver.parameters)
    return config

