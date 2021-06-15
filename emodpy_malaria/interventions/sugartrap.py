from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "SugarTrap"
#dupe_policy = "Replace" # or "Add" or "Abort" -- from covid branch
# Note that duration (what we call waning profile) needs to be configurable, but in an intuitive way

def SugarTrap(
        camp,
        start_day,
        coverage=1.0,
        killing_eff=1,
        insecticide=None,
        constant_duration=100,
        node_ids=None
    ): 
    """
        Create anew SugarTrap scheduled campaign event.  
    """
    schema_path = camp.schema_path
    # First, get the objects
    event = s2c.get_class_with_defaults( "CampaignEvent", schema_path )
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", schema_path )
    if coordinator is None:
        print( "s2c.get_class_with_defaults returned None. Maybe no schema.json was provided." )
        return ""

    intervention = s2c.get_class_with_defaults( "SugarTrap", schema_path )
    killing = utils.get_waning_from_params( schema_path, killing_eff, 0, 0 ) # constant

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing 

    event.Start_Day = float(start_day)

    # Third, do the actual settings
    intervention.Intervention_Name = iv_name 
    if insecticide is None:
        intervention.pop( "Insecticide_Name" ) # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide 

    intervention.Expiration_Constant = constant_duration

    event.Nodeset_Config = utils.do_nodes( schema_path, node_ids )

    return event

def new_intervention_as_file( camp, start_day, filename=None ):
    camp.add( SugarTrap( camp, start_day ), first=True ) 
    if filename is None:
        filename = "SugarTrap.json"
    camp.save( filename )
    return filename

