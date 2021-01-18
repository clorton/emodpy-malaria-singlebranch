from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "IRSHousingModification"
#dupe_policy = "Replace" # or "Add" or "Abort" -- from covid branch
# Note that duration (what we call waning profile) needs to be configurable, but in an intuitive way

def IRSHousingModification(
        camp,
        start_day,
        coverage=1.0,
        blocking_eff=1,
        killing_eff=1,
        insecticide=None,
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
    coordinator.Demographic_Coverage = coverage
    if coordinator is None:
        print( "s2c.get_class_with_defaults returned None. Maybe no schema.json was provided." )
        return ""

    intervention = s2c.get_class_with_defaults( "IRSHousingModification", schema_path )

    blocking = utils.get_waning_from_params( schema_path, blocking_eff, 90, 1./150 ) 
    killing = utils.get_waning_from_params( schema_path, killing_eff, 90, 1./90 )

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing 
    intervention.Blocking_Config = blocking 
    event.Start_Day = float(start_day)

    # Third, do the actual settings
    #intervention.Vaccine_Type = "AcquisitionBlocking"
    intervention.Intervention_Name = iv_name 
    if insecticide is None:
        intervention.pop( "Insecticide_Name" ) # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide
    #intervention.Duplicate_Policy = dupe_policy

    event.Nodeset_Config = utils.do_nodes( schema_path, node_ids )

    # Fourth/finally, purge the schema bits
    coordinator.finalize()
    intervention.finalize()
    blocking.finalize()
    killing.finalize()
    event.finalize()
    #event["Name"] = "MCV1" # ???

    return event

def new_intervention_as_file( camp, start_day, filename=None ):
    campaign = {}
    campaign["Events"] = []
    campaign["Events"].append( IRSHousingModification( camp, start_day ) )
    if filename is None:
        filename = "IRSHousingModification.json"
    with open( filename, "w" ) as camp_file:
        json.dump( campaign, camp_file, sort_keys=True, indent=4 )
    return filename