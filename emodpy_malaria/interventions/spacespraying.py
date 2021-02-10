from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "SpaceSpraying"

def SpaceSpraying(
        camp,
        start_day,
        coverage=1.0,
        killing_eff=1,
        insecticide=None,
        constant_duration=100,
        node_ids=None
    ):
    """
    MCV1 Campaign
    :param coverage: Demographic Coverage
    :param blocking: 
    :param killing: 
    Note Start_Day is initialized as 1, recommend that this be aligned with the start of the simulation
    """
    schema_path = camp.schema_path
    # First, get the objects
    event = s2c.get_class_with_defaults( "CampaignEvent", schema_path )
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", schema_path )
    if coordinator is None:
        print( "s2c.get_class_with_defaults returned None. Maybe no schema.json was provided." )
        return ""

    intervention = s2c.get_class_with_defaults( "SpaceSpraying", schema_path )
    killing = utils.get_waning_from_params( schema_path, killing_eff, constant_duration, 0 ) # box-style

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing
    intervention.Spray_Coverage = coverage
    event.Start_Day = float(start_day)

    # Third, do the actual settings
    intervention.Intervention_Name = iv_name
    if insecticide is None:
        intervention.pop( "Insecticide_Name" ) # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide

    #intervention.Duplicate_Policy = dupe_policy
    event.Nodeset_Config = utils.do_nodes( schema_path, node_ids )

    return event

def new_intervention_as_file( camp, start_day, filename=None ):
    campaign = {}
    campaign["Events"] = []
    campaign["Events"].append( SpaceSpraying( camp, start_day ) )
    if filename is None:
        filename = "SpaceSpraying.json"
    with open( filename, "w" ) as camp_file:
        json.dump( campaign, camp_file, sort_keys=True, indent=4 )
    return filename
