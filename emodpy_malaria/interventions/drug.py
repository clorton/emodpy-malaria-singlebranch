from emod_api import schema_to_class as s2c
import json

schema_path = None
iv_name = "AntiMalarialDrug"
#dupe_policy = "Replace" # or "Add" or "Abort" -- from covid branch
# Note that duration (what we call waning profile) needs to be configurable, but in an intuitive way

def AntiMalarialDrug( camp, start_day, coverage=1.0, drug_name="Chloroquine" ):
    """
    AntiMalarialDrug intervention wrapper.
    """
    schema_path = camp.schema_path
    # First, get the objects
    event = s2c.get_class_with_defaults( "CampaignEvent", schema_path )
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", schema_path )
    if coordinator is None:
        print( "s2c.get_class_with_defaults returned None. Maybe no schema.json was provided." )
        return ""

    intervention = s2c.get_class_with_defaults( "AntimalarialDrug", schema_path )

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention

    event.Start_Day = float(start_day)

    # Third, do the actual settings
    intervention.Intervention_Name = iv_name

    #intervention.Expiration_Constant = constant_duration
    #intervention.Cost_To_Consumer = 3.75
    # 'Cost_To_Consumer', 'Drug_Type'
    intervention.Drug_Type = drug_name 

    # Fourth/finally, purge the schema bits
    coordinator.finalize()
    intervention.finalize()
    event.finalize()
    #event["Name"] = "MCV1" # ???

    return event

def new_intervention_as_file( start_day, filename=None ):
    campaign = {}
    campaign["Events"] = []
    campaign["Events"].append( new_intervention( start_day, vaccine_type, iv_name ) )
    if filename is None:
        filename = "AntiMalarialDrug.json"
    with open( filename, "w" ) as camp_file:
        json.dump( campaign, camp_file, sort_keys=True, indent=4 )
    return filename

