import emod_api.demographics.Demographics as Demog
from emod_api.demographics import DemographicsTemplates as DT

class MalariaDemographics(Demog.Demographics):
    """
    This class is derived from emod_api.demographics' Demographics class so that we can set 
    certain defaults for Malaria in construction.
    """
    def __init__(self, nodes, idref="Gridded world grump2.5arcmin", base_file=None, init_prev=0.2): 
        super().__init__( nodes, idref, base_file )
        #super().SetDefaultProperties()
        super().SetDefaultNodeAttributes(birth=True)
        DT.InitPrevUniform( self, init_prev )
        DT.FullRisk( self )
        super().SetDefaultFromTemplate(DT.NoMigrationHeterogeneity())

def fromBasicNode(lat=0, lon=0, pop=1e6, name=1, forced_id=1, init_prev=0.2 ):
    """
    This function creates a single-node MalariaDemographics instance from the params you give it. 
    """
    new_nodes = [ Demog.Node(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id) ] 
    return MalariaDemographics(nodes=new_nodes, init_prev=init_prev)

def from_pop_csv( pop_filename_in, pop_filename_out="spatial_gridded_pop_dir", site="No_Site" ):
    generic_demog = Demog.from_pop_csv( pop_filename_in, pop_filename_out, site )
    nodes = generic_demog.nodes
    return MalariaDemographics(nodes=nodes, idref=site)

def from_synth_pop(tot_pop=1e6, num_nodes=100, frac_rural=0.3, id_ref="from_synth_pop" ):
    generic_demog = Demog.from_synth_pop(tot_pop, num_nodes, frac_rural, id_ref )
    nodes = generic_demog.nodes
    return MalariaDemographics(nodes=nodes, idref=id_ref )
