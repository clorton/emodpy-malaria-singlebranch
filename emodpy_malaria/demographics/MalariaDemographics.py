"""
This module contains the classes and functions for creating demographics files
for malaria simulations. For more information on |EMOD_s| demographics files,
see :doc:`emod-malaria:software-demographics`. 
"""

import emod_api.demographics.Demographics as Demog
from emod_api.demographics import DemographicsTemplates as DT

class MalariaDemographics(Demog.Demographics):
    """
    This class is derived from :py:class:`emod_api:emod_api.demographics.Demographics.Demographics` 
    and sets certain defaults for malaria in construction.

    Args:
        nodes: The number of nodes to create.
        idref: Method describing how the latitude and longitude values are created
            for each of the nodes in a simulation. "Gridded world" values use a grid 
            overlaid across the globe at some arcsec resolution. You may also generate 
            the grid using another tool or coordinate system. For more information,
            see :ref:`emod-malaria:demo-metadata`.
        base_file: A basic demographics file used as a starting point for
            creating more complicated demographics files. For example,
            using a single node file to create a multi-node file for spatial
            simulations. 
        init_prev: The initial malaria prevalence of the population.

    Returns: 
        None 
     """
    def __init__(self, nodes, idref="Gridded world grump2.5arcmin", base_file=None, init_prev=0.2): 
        super().__init__( nodes, idref, base_file )
        #super().SetDefaultProperties()
        super().SetDefaultNodeAttributes(birth=True)
        DT.InitPrevUniform( self, init_prev )
        DT.FullRisk( self )
        super().SetDefaultFromTemplate(DT.NoMigrationHeterogeneity())

def from_template_node(lat=0, lon=0, pop=1e6, name=1, forced_id=1, init_prev=0.2):
    """
    Create a single-node :py:class:`~emodpy_malaria.demographics.MalariaDemographics`
    instance from the parameters you supply.

    Args:
        lat: Latitude of the centroid of the node to create.
        lon: Longitude of the centroid of the node to create.
        pop: Human population of the node. 
        name: The name of the node. This may be a characteristic of the 
            node, such as "rural" or "urban", or an identifying integer.
        forced_id: The node ID for the single node.
        init_prev: The initial malaria prevalence of the node.

    Returns:
        A :py:class:`~emodpy_malaria.demographics.MalariaDemographics` instance.
    """
    new_nodes = [ Demog.Node(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id) ] 
    return MalariaDemographics(nodes=new_nodes, init_prev=init_prev)

def from_pop_csv( pop_filename_in, pop_filename_out="spatial_gridded_pop_dir", site="No_Site" ):
    """
    Create a multi-node :py:class:`~emodpy_malaria.demographics.MalariaDemographics`
    instance from a CSV file describing a population.

    Args:
        pop_filename_in: The path to the demographics file to ingest.
        pop_filename_out: The path to the file to output.
        site: A string to identify the country, village, or trial site.

    Returns:
        A :py:class:`~emodpy_malaria.demographics.MalariaDemographics` instance.
    """
    generic_demog = Demog.from_pop_csv( pop_filename_in, pop_filename_out, site )
    nodes = generic_demog.nodes
    return MalariaDemographics(nodes=nodes, idref=site)

def from_params(tot_pop=1e6, num_nodes=100, frac_rural=0.3, id_ref="from_params" ):
    """
    Create a multi-node :py:class:`~emodpy_malaria.demographics.MalariaDemographics`
    instance as a synthetic population based on a few parameters.

    Args:
        tot_pop: The total human population in the node.
        num_nodes: The number of nodes to create.
        frac_rural: The fraction of the population that is rural.
        id_ref: Method describing how the latitude and longitude values are created
            for each of the nodes in a simulation. "Gridded world" values use a grid 
            overlaid across the globe at some arcsec resolution. You may also generate 
            the grid using another tool or coordinate system. For more information,
            see :ref:`emod-malaria:demo-metadata`.

    Returns:
        A :py:class:`~emodpy_malaria.demographics.MalariaDemographics` instance.
    """
    generic_demog = Demog.from_params(tot_pop, num_nodes, frac_rural, id_ref )
    nodes = generic_demog.nodes
    return MalariaDemographics(nodes=nodes, idref=id_ref )
