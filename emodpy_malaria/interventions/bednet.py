"""
This module contains functionality for bednet distribution.
"""

from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "Bednet"


def Bednet(campaign,
           start_day: int = 0,
           coverage: float = 1.0,
           blocking_eff: float = 1,
           killing_eff: float = 1,
           repelling_eff: float = 1,
           usage_eff: float = 1,
           blocking_decay_rate: float = 0,
           blocking_predecay_duration: int = 365,
           killing_decay_rate: float = 0,
           killing_predecay_duration: int = 365,
           repelling_decay_rate: float = 0,
           repelling_predecay_duration: int = 365,
           usage_decay_rate: float = 0,
           usage_predecay_duration: int = 365,
           node_ids: list = None,
           insecticide: str = None
           ):
    """
    Add a simple insecticide-treated bednet intervention with configurable efficacy and usage 
    that can decay over time to your campaign. This is equivalent to 
    :doc:`emod-malaria:parameter-campaign-individual-usagedependentbednet` with exponential
    waning.

    Args:
        campaign: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added.
        start_day: The day of the simulation on which the bednets are distributed. We recommend 
            aligning this with the start of the simulation.
        coverage: The proportion of the population that will receive a bednet.
        blocking_eff: The efficacy of the bednet at blocking mosquitoes from feeding.
        killing_eff: The efficacy of the bednet at killing mosquitoes that land on it.
        repelling_eff: The efficacy of the bednet at repelling mosquitoes.
        usage_eff: The proportion of time that individuals with a bednet use it. This effectively
            reduces the other efficacy measures by the amount specified; a value of 0.5 will reduce
            blocking, killing, and repelling efficacies by half.
        blocking_decay_rate: The exponential decay length, in days, where the current effect is equal 
            initial efficacy - dt/decay rate.  
        blocking_predecay_duration: The time, in days, before bednet efficacy begins to decay.
        killing_decay_rate: The exponential decay length, in days, where the current effect is equal 
            initial efficacy - dt/decay rate. 
        killing_predecay_duration: The time, in days, before bednet efficacy begins to decay.
        repelling_decay_rate: The exponential decay length, in days, where the current effect is equal 
            initial efficacy - dt/decay rate. 
        repelling_predecay_duration: The time, in days, before bednet efficacy begins to decay.
        usage_decay_rate: The exponential decay length, in days, where the current usage is equal 
            initial efficacy - dt/decay rate. 
        usage_predecay_duration: The time, in days, before bednet usage begins to decay.
        node_ids: The IDs of the nodes in which to distribute the bednets.
        insecticide: The name of the insecticide used in the bednet.

    Returns:
        The bednet intervention event.
    """
    global schema_path
    schema_path = campaign.schema_path
    # First, get the objects
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    coordinator.Demographic_Coverage = coverage
    coordinator.Node_Property_Restrictions = []
    coordinator.Property_Restrictions_Within_Node = []
    coordinator.Property_Restrictions = []

    intervention = s2c.get_class_with_defaults("SimpleBednet", schema_path)
    blocking = utils.get_waning_from_params(schema_path, blocking_eff, blocking_predecay_duration, blocking_decay_rate)
    killing = utils.get_waning_from_params(schema_path, killing_eff, killing_predecay_duration, killing_decay_rate)
    repelling = utils.get_waning_from_params(schema_path, repelling_eff, repelling_predecay_duration,
                                             repelling_decay_rate)
    usage = utils.get_waning_from_params(schema_path, usage_eff, usage_predecay_duration, usage_decay_rate)

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing
    intervention.Blocking_Config = blocking
    intervention.Repelling_Config = repelling
    intervention.Usage_Config = usage
    event.Start_Day = float(start_day)

    # Third, do the actual settings
    intervention.Intervention_Name = iv_name
    if insecticide is None:
        intervention.pop("Insecticide_Name")  # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide

    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)

    return event


def BasicBednet(camp, start_day, coverage=1.0, blocking_eff=1, killing_eff=1, repelling_eff=1, usage_eff=1,
                 insecticide=None):
    """
    Add a simpler insecticide-treated bednet intervention with constant efficacy and usage
    to your campaign. This is equivalent to :doc:`emod-malaria:parameter-campaign-individual-simplebednet`.

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will 
            be added. 
        start_day: The day of the simulation on which the bednets are distributed. We recommend 
            aligning this with the start of the simulation.
        coverage: The proportion of the population that will receive a bednet.
        blocking_eff: The efficacy of the bednet at blocking mosquitoes from feeding.
        killing_eff: The efficacy of the bednet at killing mosquitoes that land on it.
        repelling_eff: The efficacy of the bednet at repelling mosquitoes.
        usage_eff: The proportion of individuals with a bednet who use it.
        insecticide: The insecticide used in the bednet.

    Returns:
        The bednet intervention event.
    """
    return Bednet(camp, start_day, coverage, blocking_eff, killing_eff, repelling_eff, usage_eff, insecticide)


def new_intervention_as_file(camp, start_day, filename=None):
    """
    Write a campaign file to disk with a single bednet event, using defaults. Useful for testing and learning.

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added. 
        start_day: The day of the simulation on which the bednets are distributed. We recommend 
            aligning this with the start of the simulation.
        filename: The campaign filename; can be omitted and default will be used and returned to user.

    Returns:
        The campaign filename written to disk.
    """
    camp.add(Bednet(camp, start_day), first=True)
    if filename is None:
        filename = "BedNet.json"
    camp.save(filename)
    return filename
