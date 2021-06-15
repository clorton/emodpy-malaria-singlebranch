"""
This module contains functionality common to many interventions.
"""

import emod_api.interventions.utils as utils
from emod_api import schema_to_class as s2c

schema_path=None

###
### Malaria
###

def MalariaDiagnostic(
        camp,
        Measurement_Sensitivity,
        Detection_Threshold,
        Diagnostic_Type 
    ):
    """
    Add a malaria diagnostic intervention to your campaign. This is equivalent
    to :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`. 

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention 
            will be added. 
        Measurement_Sensitivity: The setting for **Measurement_Sensitivity**
            in :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
        Detection_Threshold: The setting for **Detection_Threshold** in 
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`. 
        Diagnostic_Type: The setting for **Diagnostic_Type** in 
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
            In addition to the accepted values listed there, you may also set
            TRUE_INFECTION_STATUS, which calls 
            :doc:`emod-malaria:parameter-campaign-individual-standarddiagnostic`
            instead.
    Returns:
      The diagnostic intervention event.
    """
    # Shares lots of code with Standard. Not obvious if code minimization maximizes readability.
    global schema_path 
    schema_path = camp.schema_path if camp is not None else schema_path
    # First, get the objects

    intervention = s2c.get_class_with_defaults( "MalariaDiagnostic", schema_path )
    intervention.Measurement_Sensitivity = Measurement_Sensitivity 
    intervention.Detection_Threshold = Detection_Threshold 
    intervention.Diagnostic_Type = Diagnostic_Type 

    return intervention


def AntiMalarialDrug( camp, Drug_Type, ctc=1.0 ):
    """
    Add an antimalarial drug intervention to your campaign. This is equivalent to
    :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug`.

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added. 
        Drug_Type: The name of the drug to distribute in a drugs intervention.
            Possible values are contained in **Malaria_Drug_Params**. 
        ctc: The cost to consumer.

    Returns:
      The antimalarial drug intervention event.
    """
    global schema_path 
    schema_path = camp.schema_path if camp is not None else schema_path
    intervention = s2c.get_class_with_defaults( "AntimalarialDrug", schema_path )
    intervention.Drug_Type = Drug_Type 
    intervention.Cost_To_Consumer = ctc
    return intervention


