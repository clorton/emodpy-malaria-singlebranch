from emod_api import schema_to_class as s2c
from emod_api.interventions.common import utils, BroadcastEvent, MultiInterventionDistributor


def add_outbreak_individual(campaign,
                            start_day: int = 1,
                            demographic_coverage: float = 1.0,
                            target_num_individuals: int = None,
                            node_ids: list = None,
                            repetitions: int = 1,
                            timesteps_between_repetitions: int = 365,
                            ind_property_restrictions: list = None,
                            node_property_restrictions: list = None,
                            target_age_min: int = 0,
                            target_age_max: int = 125,
                            target_gender: str = "All",
                            ignore_immunity: bool = True,
                            incubation_period_override: int = -1,
                            antigen: int = 0,
                            genome: int = 0,
                            broadcast_event: str = None):
    """
    Adds a scheduled OutbreakIndividual intervention. This is set up to be used with Malaria-Ongoing branch.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group. If this value is set,
            demographic_coverage parameter is ignored
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        ignore_immunity: Individuals will be force-infected (with a specific strain) regardless of actual
            immunity level when set to True (1). Default is True (1). The person will or will not get an infection
            based on their immunity level if this is set to False.
        incubation_period_override: The incubation period, in days, that infected individuals will go through before
            becoming infectious. This value overrides the incubation period set in the configuration file.
            Set to -1 to honor the configuration parameter settings
        antigen: The antigenic base strain ID of the outbreak infection
        genome: The genetic substrain ID of the outbreak infection
        broadcast_event: Optional event that will be sent out at the same time as outbreak is distributed

    Returns:
        Nothing
    """
    schema_path = campaign.schema_path

    # configuring the intervention itself
    intervention = s2c.get_class_with_defaults("OutbreakIndividual", schema_path)
    intervention.Antigen = antigen
    intervention.Genome = genome
    intervention.Ignore_Immunity = 1 if ignore_immunity else 0
    intervention.Incubation_Period_Override = incubation_period_override

    if broadcast_event:
        intervention = MultiInterventionDistributor(campaign, [intervention, BroadcastEvent(campaign)])

    add_campaign_event(campaign, start_day=start_day, demographic_coverage=demographic_coverage,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       ind_property_restrictions=ind_property_restrictions,
                       node_property_restrictions=node_property_restrictions,
                       target_age_min=target_age_min, target_age_max=target_age_max, target_gender=target_gender,
                       target_num_individuals=target_num_individuals, node_ids=node_ids, intervention=intervention)


def add_outbreak_malaria_genetics(campaign,
                                  start_day: int = 1,
                                  demographic_coverage: float = 1.0,
                                  target_num_individuals: int = None,
                                  node_ids: list = None,
                                  repetitions: int = 1,
                                  timesteps_between_repetitions: int = 365,
                                  ind_property_restrictions: list = None,
                                  node_property_restrictions: list = None,
                                  target_age_min: int = 0,
                                  target_age_max: int = 125,
                                  target_gender: str = "All",
                                  ignore_immunity: bool = True,
                                  incubation_period_override: int = -1,
                                  create_nucleotide_sequence_from: str = "BARCODE_STRING",
                                  barcode_string: str = None,
                                  drug_resistant_string: str = None,
                                  msp_variant_value: int = None,
                                  pfemp1_variants_values: list = None,
                                  barcode_allele_frequencies_per_genome_location: list = None,
                                  drug_resistant_allele_frequencies_per_genome_location: list = None):
    """
        Creates a scheduled OutbreakIndividualMalariaGenetics CampaignEvent which can then
        be added to a campaign.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group. If this value is set,
            demographic_coverage parameter is ignored.
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        ignore_immunity: Individuals will be force-infected (with a specific strain) regardless of actual
            immunity level when set to True (1). Default is True (1). The person will or will not get an infection
            based on their immunity level if this is set to False.
        incubation_period_override: The incubation period, in days, that infected individuals will go through before
            becoming infectious. This value overrides the incubation period set in the configuration file.
            Set to -1 to honor the configuration parameter settings
        create_nucleotide_sequence_from: A string that indicates how the genomes are created.
            Possible values are: BARCODE_STRING, ALLELE_FREQUENCIES, NUCLEOTIDE_SEQUENCE.
        barcode_string: A series of nucleotide base letters (A, C, G, T) that represent the values at locations in
            the genome. The length of the string depends on the number of locations defined in
            config.Parasite_Genetics.Barcode_Genome_Locations. Each character of the string corresponds
            to one of the locations. The locations are assumed to be in ascending order. Also depends
            on create_nucleotide_sequence_from when it is equal to NUCLEOTIDE_SEQUENCE or BARCODE_STRING.
        drug_resistant_string: A series of nucleotide base letters (A, C, G, T) that represent the values at
            locations in the genome. The length of the string depends on the number of locations defined in
            config.Parasite_Genetics.Drug_Resistant_Genome_Locations. Each character of the string corresponds
            to one of the locations. The locations are assumed to be in ascending order. Also depends on
            create_nucleotide_sequence_from when it is equal to NUCLEOTIDE_SEQUENCE or BARCODE_STRING.
        msp_variant_value: The Merozoite Surface Protein value used to determine how the antibodies recognizes
            the merzoites. This value depends on config.Falciparum_MSP_Variants and must be less than or equal to it.
            It also depends on create_nucleotide_sequence_from when it is equal to NUCLEOTIDE_SEQUENCE.
        pfemp1_variants_values: The PfEMP1 Variant values / major epitopes used to define how the antibodies recognize
            the infected red blood cells. The values of the array depend on config.Falciparum_PfEMP1_Variants and
            must be less than or equal to it. There must be exactly 50 values – one for each epitope. It also depends
            on create_nucleotide_sequence_from when it is equal to NUCLEOTIDE_SEQUENCE.
        barcode_allele_frequencies_per_genome_location: The fractions of allele occurrences for each location in the
            barcode. This 2D array should have one array for each location/character in the barcode. For each location,
            there should be four values between 0 and 1 indicating the probability that specific character appears.
            The possible letters are: A=0, C=1, G=2, T=3. It also depends on create_nucleotide_sequence_from when
            it is equal to ALLELE_FREQUENCIES. The frequencies should sum up to 1.
        drug_resistant_allele_frequencies_per_genome_location: The fractions of allele occurrences for each location
            in the drug resistant markers. This 2D array should have one array for each drug resistant location.
            For each location, there should be four values between 0 and 1 indicating the probability that specific
            character will appear. The possible letters are'A'=0, 'C'=1, 'G'=2, 'T'=3. It also depends on
            create_nucleotide_sequence_from when it is equal to ALLELE_FREQUENCIES. The frequencies should sum up to 1.


    Returns:
        CampaignEvent which then can be added to the campaign file
    """
    if create_nucleotide_sequence_from == "BARCODE_STRING" and not barcode_string:
        raise ValueError(f"You must define barcode_string with {create_nucleotide_sequence_from} setting.\n")
    elif create_nucleotide_sequence_from == "BARCODE_STRING" and (msp_variant_value or pfemp1_variants_values
                                                                  or barcode_allele_frequencies_per_genome_location):
        raise ValueError(f"With {create_nucleotide_sequence_from} setting does not use msp_variant_value or "
                         f"pfemp1_variants_values or barcode_allele_frequencies_per_genome_location. "
                         f"Please do not set them.\n")
    elif create_nucleotide_sequence_from == "NUCLEOTIDE_SEQUENCE" and not (
            msp_variant_value and pfemp1_variants_values):
        raise ValueError(f"You must define msp_variant_value and pfemp1_variants_values with "
                         f"{create_nucleotide_sequence_from} setting.\n")
    elif create_nucleotide_sequence_from == "NUCLEOTIDE_SEQUENCE" and (barcode_string or
                                                                       barcode_allele_frequencies_per_genome_location):
        raise ValueError(f"With {create_nucleotide_sequence_from} setting does not use barcode_string "
                         f"or barcode_allele_frequencies_per_genome_location. Please do not set them.\n")
    elif create_nucleotide_sequence_from == "ALLELE_FREQUENCIES" and not barcode_allele_frequencies_per_genome_location:
        raise ValueError(f"You must define barcode_allele_frequencies_per_genome_location with "
                         f"{create_nucleotide_sequence_from} setting.\n")
    elif create_nucleotide_sequence_from == "ALLELE_FREQUENCIES" and (barcode_string or
                                                                      msp_variant_value or pfemp1_variants_values):
        raise ValueError(f"With {create_nucleotide_sequence_from} setting does not use barcode_string "
                         f"or msp_variant_value or pfemp1_variants_values. Please do not set them.\n")

    schema_path = campaign.schema_path

    intervention = s2c.get_class_with_defaults("OutbreakIndividualMalariaGenetics", schema_path)

    if create_nucleotide_sequence_from == "BARCODE_STRING":
        intervention.Barcode_String = barcode_string
        if drug_resistant_string:
            intervention.Drug_Resistant_String = drug_resistant_string
    elif create_nucleotide_sequence_from == "NUCLEOTIDE_SEQUENCE":
        intervention.MSP_Variant_Value = msp_variant_value
        intervention.Barcode_String = barcode_string
        intervention.PfEMP1_Variants_Values = pfemp1_variants_values
        if drug_resistant_string:
            intervention.Drug_Resistant_String = drug_resistant_string
    elif create_nucleotide_sequence_from == "ALLELE_FREQUENCIES":
        intervention.Barcode_Allele_Frequencies_Per_Genome_Location = barcode_allele_frequencies_per_genome_location
        if drug_resistant_allele_frequencies_per_genome_location:
            intervention.Drug_Resistant_Allele_Frequencies_Per_Genome_Location = drug_resistant_allele_frequencies_per_genome_location
    else:
        raise ValueError(f"Unknown create_nucleotide_sequence_from option - {create_nucleotide_sequence_from}.\n")

    intervention.Create_Nucleotide_Sequence_From = create_nucleotide_sequence_from
    intervention.Ignore_Immunity = 1 if ignore_immunity else 0
    intervention.Incubation_Period_Override = incubation_period_override

    add_campaign_event(campaign, start_day=start_day, demographic_coverage=demographic_coverage,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       ind_property_restrictions=ind_property_restrictions,
                       node_property_restrictions=node_property_restrictions,
                       target_age_min=target_age_min, target_age_max=target_age_max, target_gender=target_gender,
                       target_num_individuals=target_num_individuals, node_ids=node_ids, intervention=intervention)


def add_outbreak_malaria_var_genes(campaign,
                                   start_day: int = 1,
                                   demographic_coverage: float = 1.0,
                                   target_num_individuals: int = None,
                                   node_ids: list = None,
                                   repetitions: int = 1,
                                   timesteps_between_repetitions: int = 365,
                                   ind_property_restrictions: list = None,
                                   node_property_restrictions: list = None,
                                   target_age_min: int = 0,
                                   target_age_max: int = 125,
                                   target_gender: str = "All",
                                   ignore_immunity: bool = True,
                                   incubation_period_override: int = -1,
                                   irbc_type: list = None,
                                   minor_epitope_type: list = None,
                                   msp_type: int = None):
    """
        Creates a scheduled OutbreakIndividualMalariaGenetics CampaignEvent which can then
        be added to a campaign.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group. If this value is set,
            demographic_coverage parameter is ignored
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        ignore_immunity: Individuals will be force-infected (with a specific strain) regardless of actual
            immunity level when set to True (1). Default is True (1). The person will or will not get an infection
            based on their immunity level if this is set to False.
        incubation_period_override: The incubation period, in days, that infected individuals will go through before
            becoming infectious. This value overrides the incubation period set in the configuration file.
            Set to -1 to honor the configuration parameter settings
        irbc_type: The array PfEMP1 Major epitope variant values. There must be exactly 50 values. Min value = 0,
            MAX value = config.Falciparum_PfEMP1_Variants.
        minor_epitope_type: The array PfEMP1 Minor epitope variant values. There must be exactly 50 values.
            Min value = 0, MAX value = config.Falciparum_Nonspecific_Types * MINOR_EPITOPE_VARS_PER_SET(=5) .
        msp_type: The Merozoite Surface Protein variant value of this infection. Min value = 0,
            MAX value = config.Falciparum_MSP_Variants.

    Returns:
        CampaignEvent which then can be added to the campaign file
    """
    if not irbc_type or not minor_epitope_type or not msp_type:
        raise ValueError(f"irbc_type, minor_epitope_type, msp_type all must be defined.\n")
    elif irbc_type and len(irbc_type) != 50:
        raise ValueError(f"irbc_type needs to have 50 values, you have {len(irbc_type)}.\n")
    elif minor_epitope_type and len(minor_epitope_type) != 50:
        raise ValueError(f"minor_epitope_type needs to have 50 values, you have {len(minor_epitope_type)}.\n")

    schema_path = campaign.schema_path

    intervention = s2c.get_class_with_defaults("OutbreakIndividualMalariaVarGenes", schema_path)
    intervention.MSP_Type = msp_type
    intervention.Minor_Epitope_Type = minor_epitope_type
    intervention.IRBC_Type = irbc_type
    intervention.Ignore_Immunity = 1 if ignore_immunity else 0
    intervention.Incubation_Period_Override = incubation_period_override

    add_campaign_event(campaign, start_day=start_day, demographic_coverage=demographic_coverage,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       ind_property_restrictions=ind_property_restrictions,
                       node_property_restrictions=node_property_restrictions,
                       target_age_min=target_age_min, target_age_max=target_age_max, target_gender=target_gender,
                       target_num_individuals=target_num_individuals, node_ids=node_ids, intervention=intervention)


def add_campaign_event(campaign,
                       start_day: int = 1,
                       demographic_coverage: float = 1.0,
                       target_num_individuals: int = None,
                       node_ids: list = None,
                       repetitions: int = 1,
                       timesteps_between_repetitions: int = 365,
                       ind_property_restrictions: list = None,
                       node_property_restrictions: list = None,
                       target_age_min: int = 0,
                       target_age_max: int = 125,
                       target_gender: str = "All",
                       intervention: any = None):
    """
        Adds a campaign event to the campaign with a passed in intervention.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group. If this value is set,
            demographic_coverage parameter is ignored
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        intervention: Intervention to be distributed by this event
    Returns:

    """
    schema_path = campaign.schema_path
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event.Start_Day = start_day
    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)

    # configuring the coordinator
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    if target_num_individuals is not None:
        coordinator.Target_Num_Individuals = target_num_individuals
    else:
        coordinator.Demographic_Coverage = demographic_coverage
    coordinator.Number_Repetitions = repetitions
    coordinator.Timesteps_Between_Repetitions = timesteps_between_repetitions
    coordinator.Node_Property_Restrictions = node_property_restrictions if node_property_restrictions else []
    coordinator.Property_Restrictions_Within_Node = ind_property_restrictions if ind_property_restrictions else []
    coordinator.Property_Restrictions = []  # not using; Property_Restrictions_Within_Node are more flexible

    if target_age_min > 0 or target_age_max < 125:
        coordinator.Target_Age_Min = target_age_min
        coordinator.Target_Age_Max = target_age_max
    if target_gender != "All":
        coordinator.Target_Gender = target_gender
        coordinator.Target_Demographic = "ExplicitAgeRangesAndGender"

    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention

    campaign.add(event)
