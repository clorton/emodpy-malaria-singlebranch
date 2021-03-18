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
        Measurement_Sensitivity: The number of microliters of blood tested to find single 
            parasite/gameotcyte in a traditional smear (corresponds to inverse parasites/microliters 
            sensitivity). This is similar to **Parasite_Smear_Sensitivity** and 
            **Gametocyte_Smear_Sensitivity** in the config used for reports, but this is for 
            this instance of the diagnostic. In the following equation, if **measurement** 
            is larger than **Detection_Threshold** a positive diagnosis is made::

                measurement = float(1.0/Measurement_Sensitivity*GetRng()->
                              Poisson(Measurement_Sensitivity*true_parasite_density)) 

            Used only when **Diagnostic_Type** is set to BLOOD_SMEAR_PARASITES or 
            BLOOD_SMEAR_GAMETOCYTES.

        Detection_Threshold: The diagnostic detection threshold for parasites, in units 
            of microliters of blood. 
        Diagnostic_Type: The type of malaria diagnostic used. Possible values are:

                * BLOOD_SMEAR_PARASITES
                * BLOOD_SMEAR_GAMETOCYTES
                * PCR_PARASITES
                * PCR_GAMETOCYTES
                * PF_HRP2
                * TRUE_PARASITE_DENSITY
                * FEVER

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


