from emod_api import schema_to_class as s2c
import json

schema_path = None
iv_name = "Bednet"
#dupe_policy = "Replace" # or "Add" or "Abort" -- from covid branch
# Note that duration (what we call waning profile) needs to be configurable, but in an intuitive way

def Bednet( camp, start_day, coverage=1.0, blocking_eff=1, killing_eff=1, repelling_eff=1, usage_eff=1 ):
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

    intervention = s2c.get_class_with_defaults( "SimpleBednet", schema_path )
    efficacy_profile = "WaningEffectConstant"
    blocking = s2c.get_class_with_defaults( efficacy_profile, schema_path )
    killing = s2c.get_class_with_defaults( efficacy_profile, schema_path )
    repelling = s2c.get_class_with_defaults( efficacy_profile, schema_path )
    usage = s2c.get_class_with_defaults( efficacy_profile, schema_path )
    blocking.Initial_Effect = blocking_eff
    killing.Initial_Effect = killing_eff
    repelling.Initial_Effect = repelling_eff
    usage.Initial_Effect = usage_eff

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing 
    intervention.Blocking_Config = blocking 
    intervention.Repelling_Config = repelling 
    intervention.Usage_Config = usage 
    event.Start_Day = float(start_day)

    # Third, do the actual settings
    #intervention.Vaccine_Type = "AcquisitionBlocking"
    intervention.Intervention_Name = iv_name 
    intervention.pop( "Insecticide_Name" ) # this is not permanent
    #intervention.Duplicate_Policy = dupe_policy

    # Fourth/finally, purge the schema bits
    coordinator.finalize()
    intervention.finalize()
    blocking.finalize()
    killing.finalize()
    repelling.finalize()
    usage.finalize()
    event.finalize()
    #event["Name"] = "MCV1" # ???

    return event

def new_intervention_as_file( start_day, filename=None ):
    campaign = {}
    campaign["Events"] = []
    campaign["Events"].append( new_intervention( start_day, vaccine_type, iv_name ) )
    if filename is None:
        filename = "bednet.json"
    with open( filename, "w" ) as camp_file:
        json.dump( campaign, camp_file, sort_keys=True, indent=4 )
    return filename

