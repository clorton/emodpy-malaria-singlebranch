from emod_api import schema_to_class as s2c


def outbreakindividualmalariavargenes(schema_path_container,
                                      start_day: int = 1,
                                      demographic_coverage: float = 1.0,
                                      target_num_individuals: int = None,
                                      irbc_type: list = None,
                                      minor_epitope_type: list = None,
                                      msp_type: int = None
                                      ):
    """
        Creates a scheduled OutbreakIndividualMalariaGenetics CampaignEvent which can then
        be added to a campaign.

    Args:
        schema_path_container: thing you need to pass in for this to work. I dunno.
        start_day: The day the intervention is given out.
        irbc_type: The array PfEMP1 Major epitope variant values. There must be exactly 50 values. Min value = 0,
            MAX value = Falciparum_PfEMP1_Variants.
        minor_epitope_type: The array PfEMP1 Minor epitope variant values. There must be exactly 50 values.
            Min value = 0, MAX value = Falciparum_Nonspecific_Types * MINOR_EPITOPE_VARS_PER_SET(=5) .
        msp_type: The Merozoite Surface Protein variant value of this infection. Min value = 0,
            MAX value = Falciparum_MSP_Variants.
        demographic_coverage: . This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group.

    Returns:
        CampaignEvent which then can be added to the campaign file
    """
    if not irbc_type or not minor_epitope_type or not msp_type:
        raise ValueError(f"irbc_type, minor_epitope_type, msp_type all must be defined.\n")
    elif irbc_type and len(irbc_type) != 50:
        raise ValueError(f"irbc_type needs to have 50 values, you have {len(irbc_type)}.\n")
    elif minor_epitope_type and len(minor_epitope_type) != 50:
        raise ValueError(f"minor_epitope_type needs to have 50 values, you have {len(minor_epitope_type)}.\n")

    schema_path = schema_path_container.schema_path

    # First, get the objects and configure
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    intervention = s2c.get_class_with_defaults("OutbreakIndividualMalariaVarGenes", schema_path)

    intervention.MSP_Type = msp_type
    intervention.Minor_Epitope_Type = minor_epitope_type
    intervention.IRBC_Type = irbc_type

    # configuring the main event
    event.Start_Day = start_day

    # configuring the coordinator
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    coordinator.Node_Property_Restrictions = []
    coordinator.Property_Restrictions_Within_Node = []
    coordinator.Property_Restrictions = []
    if target_num_individuals is not None:
        coordinator.Target_Num_Individuals = target_num_individuals
    else:
        coordinator.Demographic_Coverage = demographic_coverage



    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention

    return event
