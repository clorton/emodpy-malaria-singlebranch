from emod_api import schema_to_class as s2c
from emod_api.interventions import utils

iv_name = "OutdoorRestKill"
schema_path = None

def OutdoorRestKill (
        schema_path_container
        , killing_effect
        , insecticide_name = None
        , start_day=0
        , target_coverage=1.0
        , killing_predecay_duration=0
        , killing_decay_rate=0
        , node_ids=None
):
    """

    Args:
        schema_path_container:
        killing_effect:
        insecticide_name:
        start_day:
        target_coverage:
        killing_predcay_duration:
        killing_decay_rate:

    Returns:

    """

    schema_path = schema_path_container.schema_path
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", schema_path )
    coordinator.Demographic_Coverage = target_coverage

    intervention = s2c.get_class_with_defaults("OutdoorRestKill", schema_path)
    intervention.Insecticide_Name = insecticide_name
    killing = utils.get_waning_from_params(schema_path, killing_effect,
                                           killing_predecay_duration,
                                           killing_decay_rate)

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing
    event.Start_Day = float(start_day)
    event.Nodeset_Config = utils.do_nodes( schema_path, node_ids )

    # Third, cleanup
    killing.finalize()
    intervention.finalize()
    coordinator.finalize()
    event.finalize()

    return event

