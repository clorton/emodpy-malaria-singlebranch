import emod_api.demographics.Demographics as Demog
from emod_api.demographics import DemographicsTemplates as DT

class MalariaDemographics(Demog.Demographics):
    """
    This class is derived from emod_api.demographics' Demographics class so that we can set 
    certain defaults for Malaria in construction.
    """
    def __init__(self, nodes, idref="Gridded world grump2.5arcmin", base_file=None, implicits=None): 
        super().__init__( nodes, idref, base_file, implicits )
        #super().SetDefaultProperties()
        super().SetDefaultNodeAttributes(birth=True)
        DT.InitPrevUniform( self, 0.2 )
        DT.FullRisk( self )

def fromBasicNode(lat=0, lon=0, pop=1e6, name=1, forced_id=1, implicit_config_fns = None ):
    """
    This function creates a single-node MalariaDemographics instance from the params you give it. 
    """
    new_nodes = [ Demog.Node(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id) ]
    return MalariaDemographics(nodes=new_nodes, implicits=implicit_config_fns)

def from_pop_csv( pop_filename_in, pop_filename_out="spatial_gridded_pop_dir", site="No_Site", implicit_config_fns = None ):
    generic_demog = Demog.from_pop_csv( pop_filename_in, pop_filename_out, site )
    nodes = generic_demog.nodes
    return MalariaDemographics(nodes=nodes, idref=site, implicits=implicit_config_fns)
