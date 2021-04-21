from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

def new_intervention(
        camp,
        monthly_eir,
        age_dependence
    ):
    intervention = s2c.get_class_with_defaults( "InputEIR", camp.schema_path )
    if len(monthly_eir) != 12:
        raise ValueError( f"monthly_eir array needs to have 1 element per month (i.e., 12)." )
    if any(i > 1000 for i in monthly_eir):
        raise ValueError( f"All monthly_eir array elements need to be <= 1000." )
    if any(i < 0 for i in monthly_eir):
        raise ValueError( f"All monthly_eir array elements need to be positive." )

    intervention.Monthly_EIR = monthly_eir
    intervention.Age_Dependence = age_dependence
    return intervention


def InputEIR( 
        camp, 
        eir,
        start_day=1, 
        node_ids=None,
        age_dep="OFF"
    ):
    """
        InpputEIR intervention wrapper.
    """
    # First, get the objects
    event = s2c.get_class_with_defaults( "CampaignEvent", camp.schema_path )
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", camp.schema_path )
    if coordinator is None:
        print( "s2c.get_class_with_defaults returned None. Maybe no schema.json was provided." )
        return ""

    intervention = new_intervention( camp, eir, age_dep )
    coordinator.Intervention_Config = intervention
    coordinator.pop( "Node_Property_Restrictions" )

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    event.Start_Day = float(start_day) 
    event.Nodeset_Config = utils.do_nodes( camp.schema_path, node_ids )

    return event


def new_intervention_as_file( camp, start_day, eir, filename=None ):
    camp.add( InputEIR( camp, eir, start_day ), first=True)
    if filename is None:
        filename = "InputEIR.json"
    camp.save( filename )
    return filename

