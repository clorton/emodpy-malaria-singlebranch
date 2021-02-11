import emod_api.interventions.utils as utils
from emod_api import schema_to_class as s2c

schema_path=None

###
### Malaria
###

def MalariaDiagnostic(
        camp,
        Base_Sensitivity,
        Base_Specificity,
        Measurement_Sensitivity,
        Detection_Threshold,
        Diagnostic_Type,
        Event_Or_Config="Config"
    ):

    # Shares lots of code with Standard. Not obvious if code minimization maximizes readability.
    global schema_path 
    schema_path = camp.schema_path if camp is not None else schema_path
    # First, get the objects

    intervention = s2c.get_class_with_defaults( "MalariaDiagnostic", schema_path )
    intervention.Base_Sensitivity = Base_Sensitivity 
    intervention.Base_Specificity = Base_Specificity 
    intervention.Measurement_Sensitivity = Measurement_Sensitivity 
    intervention.Detection_Threshold = Detection_Threshold 
    intervention.Diagnostic_Type = Diagnostic_Type 
    intervention.Event_Or_Config = Event_Or_Config

    # Fourth/finally, purge the schema bits
    #intervention.finalize()

    return intervention


def AntiMalarialDrug( camp, Drug_Type, ctc=1.0 ):

    global schema_path 
    schema_path = camp.schema_path if camp is not None else schema_path
    intervention = s2c.get_class_with_defaults( "AntimalarialDrug", schema_path )
    intervention.Drug_Type = Drug_Type 
    intervention.Cost_To_Consumer = ctc
    return intervention


