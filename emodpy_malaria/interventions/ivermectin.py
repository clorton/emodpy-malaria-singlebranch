from emod_api import schema_to_class as s2c
iv_name = "Ivermectin"


def Ivermectin (
        schema_path_container
        , killing_effect
        , start_day=0
        , target_coverage=1.0
        , target_num_individuals=None
        , killing_duration_box=0
        , killing_duration_exponential=0
):
    """

    Args:
        start_day: day to give out this ivermectin
        target_coverage: probability of choosing an individual
        target_num_individuals: number of individuals to choose
        killing_effect: initial parasite killing effect
        killing_duration_box: box duration for killing effect
        killing_duration_exponential: decay_time_constant for killing effect

    Returns: campaign event

    """

    schema_path = schema_path_container.schema_path

    # First, get the objects and configure
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event.Start_Day = start_day

    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    if target_num_individuals is not None:
        coordinator.Target_Num_Individuals = target_num_individuals
    else:
        coordinator.Demographic_Coverage = target_coverage

    intervention = s2c.get_class_with_defaults("Ivermectin", schema_path)
    efficacy_profile = None

    killing = s2c.get_class_with_defaults("WaningEffectBoxExponential", schema_path)
    killing.Decay_Time_Constant = killing_duration_exponential
    killing.Box_Duration = killing_duration_box
    killing.Initial_Effect = killing_effect

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing

    # Third, cleanup
    killing.finalize()
    intervention.finalize()
    coordinator.finalize()
    event.finalize()

    return event

