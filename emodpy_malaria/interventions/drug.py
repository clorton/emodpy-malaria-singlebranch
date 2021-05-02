"""
This module contains functionality for defining antimalarial drug interventions.
"""

from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

iv_name = "AntimalarialDrug"

def AntiMalarialDrug( 
        camp, 
        start_day=1, 
        coverage=1.0, 
        drug_name="Chloroquine",
        node_ids=None
    ):
    """
    Add an antimalarial drug intervention to your campaign. This is equivalent to 
    :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug`.

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added. 
        start_day: The day of the simulation on which the drug is distributed. We recommend 
            aligning this with the start of the simulation. 
        coverage: The proportion of the population that will receive the drug.
        drug_name: The name of the drug to distribute in a drug intervention. Possible values are 
            contained in **Malaria_Drug_Params** in :doc:`emod-malaria:parameter-configuration-drugs`.
            Use :py:meth:`~emodpy_malaria.config.set_team_drug_params` to set those values.
        node_ids: The IDs of the nodes in which to distribute the drug.

    Returns:
        The intervention event.
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
    coordinator.Demographic_Coverage = coverage

    #intervention.Expiration_Constant = constant_duration
    #intervention.Cost_To_Consumer = 3.75
    # 'Cost_To_Consumer', 'Drug_Type'
    intervention.Drug_Type = drug_name 

    event.Nodeset_Config = utils.do_nodes( schema_path, node_ids )

    return event


def new_intervention_as_file( camp, start_day, filename=None ):
    """
    Take an :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug`
    intervention from a JSON file and add it to your campaign.

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added. 
        start_day: The day of the simulation on which the drug is distributed. We recommend 
            aligning this with the start of the simulation.
        filename: The JSON file that contains the intervention.

    Returns:
        The filename.
    """
    camp.add( AntiMalarialDrug( camp, start_day ), first=True )
    if filename is None:
        filename = "AntimalarialDrug.json"
    camp.save( filename )
    return filename
