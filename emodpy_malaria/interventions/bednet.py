from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "Bednet"

def Bednet(
        camp,
        start_day,
        coverage=1.0,
        blocking_eff=1,
        killing_eff=1,
        repelling_eff=1,
        usage_eff=1,
        blocking_decay_rate=0,
        blocking_predecay_duration=365,
        killing_decay_rate=0,
        killing_predecay_duration=365,
        repelling_decay_rate=0,
        repelling_predecay_duration=365,
        usage_decay_rate=0,
        usage_predecay_duration=365,
        node_ids=None,
        insecticide=None
    ):
    """
        Simple Bednet with small param set.
        Note Start_Day is initialized as 1, recommend that this be aligned with the start of the simulation
    """
    global schema_path 
    schema_path = camp.schema_path
    # First, get the objects
    event = s2c.get_class_with_defaults( "CampaignEvent", schema_path )
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", schema_path )
    coordinator.Demographic_Coverage = coverage

    intervention = s2c.get_class_with_defaults( "SimpleBednet", schema_path )
    blocking = utils.get_waning_from_params( schema_path, blocking_eff, blocking_predecay_duration, blocking_decay_rate ) 
    killing = utils.get_waning_from_params( schema_path, killing_eff, killing_predecay_duration, killing_decay_rate ) 
    repelling = utils.get_waning_from_params( schema_path, repelling_eff, repelling_predecay_duration, repelling_decay_rate ) 
    usage = utils.get_waning_from_params( schema_path, usage_eff, usage_predecay_duration, usage_decay_rate ) 

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
    repelling.finalize()
    usage.finalize()
    event.finalize()

    return event

def BabyBednet( camp, start_day, coverage=1.0, blocking_eff=1, killing_eff=1, repelling_eff=1, usage_eff=1, insecticide=None ):
    """
        BabyBednet is not for babies. It's simpler bednet with just the basic configuration controls.
    """
    return Bednet( camp, start_day, coverage, blocking_eff, killing_eff, repelling_eff, usage_eff, insecticide )


def new_intervention_as_file( camp, start_day, filename=None ):
    campaign = {}
    campaign["Events"] = []
    campaign["Events"].append( Bednet( camp, start_day ) )
    if filename is None:
        filename = "bednet.json"
    with open( filename, "w" ) as camp_file:
        json.dump( campaign, camp_file, sort_keys=True, indent=4 )
    return filename