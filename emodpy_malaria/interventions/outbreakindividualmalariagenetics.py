from emod_api import schema_to_class as s2c


def outbreakindividualmalariagenetics(schema_path_container,
                                      start_day: int = 1,
                                      demographic_coverage: float = 1.0,
                                      target_num_individuals: int = None,
                                      create_nucleotide_sequence_from: str = "BARCODE_STRING",
                                      barcode_string: str = None,
                                      drug_resistant_string: str = None,
                                      msp_variant_value: int = None,
                                      pfemp1_variants_values: list = None,
                                      barcode_allele_frequencies_per_genome_location: list = None,
                                      drug_resistant_allele_frequencies_per_genome_location: list = None
                                      ):
    """
        Creates a scheduled OutbreakIndividualMalariaGenetics CampaignEvent which can then
        be added to a campaign.

    Args:
        schema_path_container: thing you need to pass in for this to work. I dunno.
        start_day: The day the intervention is given out.
        create_nucleotide_sequence_from: A string that indicates how the genome are created.
            Possible values are: BARCODE_STRING, ALLELE_FREQUENCIES, NUCLEOTIDE_SEQUENCE.
        barcode_string: A series of nucleotide base letters (A, C, G, T) that represent the values at locations in
            the genome.  The length of the string depends on the number of locations defined in
            config.Parasite_Genetics.Barcode_Genome_Locations.  Each character of the string corresponds
            to one of the locations.  The locations are assumed to be in ascending order.  Also depends
            on Create_Nucleotide_Sequence_From when it is equal to NUCLEOTIDE_SEQUENCE or BARCODE_STRING.
        drug_resistant_string: A series of nucleotide base letters (A, C, G, T) that represent the values at
            locations in the genome.  The length of the string depends on the number of locations defined in
            config.Parasite_Genetics.Drug_Resistant_Genome_Locations.  Each character of the string corresponds
            to one of the locations.  The locations are assumed to be in ascending order.  Also depends on
            Create_Nucleotide_Sequence_From when it is equal to NUCLEOTIDE_SEQUENCE or BARCODE_STRING.
        msp_variant_value: The Merozoite Surface Protein value used to determine how the antibodies recognizes
            the merzoites. This value depends on config. Falciparum_MSP_Variants and must be less than or equal to it.
            It also depends on Create_Nucleotide_Sequence_From when it is equal to NUCLEOTIDE_SEQUENCE.
        pfemp1_variants_values: The PfEMP1 Variant values / major epitopes used to define how the antibodies recognize
            the infected red blood cells.  The values of the array depend on config. Falciparum_PfEMP1_Variants and
            must be less than or equal to it.  There must be exactly 50 values – one for each epitope.  It also depends
            on Create_Nucleotide_Sequence_From when it is equal to NUCLEOTIDE_SEQUENCE.
        barcode_allele_frequencies_per_genome_location: The fractions of allele occurrences for each location in the
            barcode. This 2D array should have one array for each location/character in the barcode. For each location,
            there should be four values between 0 and 1 indicating the probability that specific character appears.
            The possible letters are: A=0, C=1, G=2, T=3.
        drug_resistant_allele_frequencies_per_genome_location: "The fractions of allele occurrences for each location
            in the drug resistant markers.  This 2D array should have one array for each drug resistant location.
            For each location, there should be four values between 0 and 1 indicating the probability that specific
            character will appear.  The possible letters are'A'=0, 'C'=1, 'G'=2, 'T'=3.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group.

    Returns:
        CampaignEvent which then can be added to the campaign file
    """
    if create_nucleotide_sequence_from == "BARCODE_STRING" and not barcode_string:
        raise ValueError(f"You must define barcode_string with {create_nucleotide_sequence_from} setting.\n")
    elif create_nucleotide_sequence_from == "NUCLEOTIDE_SEQUENCE" and not (msp_variant_value and pfemp1_variants_values):
        raise ValueError(f"You must define msp_variant_value and pfemp1_variants_values with "
                         f"{create_nucleotide_sequence_from} setting.\n")
    elif create_nucleotide_sequence_from == "ALLELE_FREQUENCIES" and not barcode_allele_frequencies_per_genome_location:
        raise ValueError(f"You must define barcode_allele_frequencies_per_genome_location with "
                         f"{create_nucleotide_sequence_from} setting.\n")

    schema_path = schema_path_container.schema_path

    # First, get the objects and configure
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    intervention = s2c.get_class_with_defaults("OutbreakIndividualMalariaGenetics", schema_path)

    # configuring the main event
    event.Start_Day = start_day

    # configuring the coordinator
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    coordinator.Node_Property_Restrictions = []
    coordinator.Property_Restrictions_Within_Node = []
    coordinator.Property_Restrictions = []

    if target_num_individuals is not None:  # emod-api sets Individual_Selection_Type automatically
        coordinator.Target_Num_Individuals = target_num_individuals
    else:
        coordinator.Demographic_Coverage = demographic_coverage

    intervention.Create_Nucleotide_Sequence_From = create_nucleotide_sequence_from
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

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention

    return event
