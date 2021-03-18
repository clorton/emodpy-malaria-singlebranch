from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "MosquitoRelease"

def MosquitoRelease(
        camp,
        start_day,
        by_number=True,
        number=10000,
        percentage=0.1,
        infectious=0.0,
        species="arabiensis",
        genome=[["X","X"]],
        node_ids=None
    ):
    """
    Release mosquitoes of a given species and genome into each node
    :param start_day The day to release the vectors
    :param by_number True if releasing a fixed number of vectors else a percentage of the current population of the
                     gender specified in the genome
    :param number: The number of vectors to release
    :param percentage: The percentage of the current poulation of mosquitoes to release.  The 'population' will
                       depend on the gender of the mosquitos being released and it will be the population from
                      the previous time step.
    :param infectious The fraction of vectors released that are to be infectious.  One can only use this
                      feature when 'Malaria_Model'!='MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS'
                      and there are no 'Genome_Markers'.
    :param species: The case sensitive name of the species of vectors to be released
    :param genome: This defines the alleles of the genome of the vectors to be released.  It must define all of
                   the alleles including the gender 'gene'.  '*' is not allowed.
    :param node_ids The list of node IDs to receive a release of vectors.  The same number of vectors will be released
                    to each node
    """
    schema_path = camp.schema_path
    # First, get the objects
    event = s2c.get_class_with_defaults( "CampaignEvent", schema_path )
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", schema_path )

    intervention = s2c.get_class_with_defaults( "MosquitoRelease", schema_path )

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    event.Start_Day = float(start_day)

    # Third, do the actual settings
    intervention.Intervention_Name = iv_name

    if by_number:
        intervention.Released_Type = "FIXED_NUMBER"
        intervention.Released_Number = number
    else:
        intervention.Released_Type = "PERCENTAGE"
        intervention.Released_Percentage = percentage

    intervention.Released_Infectious = infectious
    intervention.Released_Species = species
    intervention.Released_Genome = genome
    intervention.Released_Wolbachia = "VECTOR_WOLBACHIA_FREE"

    #intervention.Duplicate_Policy = dupe_policy
    event.Nodeset_Config = utils.do_nodes( schema_path, node_ids )

    return event

def new_intervention_as_file( camp, start_day, filename=None ):
    camp.add( MosquitoRelease( camp, start_day ), first=True )
    if filename is None:
        filename = "MosquitoRelease.json"
    camp.save( filename )
    return filename
