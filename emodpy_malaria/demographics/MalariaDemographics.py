from emod_api.demographics.Demographics import Demographics, Node
from emod_api.demographics import DemographicsTemplates as DT

class MalariaDemographics(Demographics):
    """
    This class is derived from emod_api.demographics' Demographics class so that we can set 
    certain defaults for Malaria in construction. Keen observers will note thatt SetDefaultProperties
    does not look like a measles-specific function. But as we add other disease types the 
    generatlizations and speicfics will become clearer. The architectural point is solid.
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
    new_nodes = [ Node(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id) ]
    return MalariaDemographics(nodes=new_nodes, implicits=implicit_config_fns)

