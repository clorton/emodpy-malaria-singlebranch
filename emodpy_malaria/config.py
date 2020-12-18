import emod_api.config.default_from_schema_no_validation as dfs

alleles = list()
mutations = dict()
traits = list()
insecticides = dict()

#
# PUBLIC API section
#
def set_resistances( config ):
    """
    Use this function after you're done calling add_resistance. config is the input and the output
    """
    for name, insect in insecticides.items():
        insect.parameters.finalize()
        config.parameters.Insecticides.append( insect.parameters )
    return config

def add_alleles( allele_names_in, allele_inits_in ):
    """
    This is public API function for user to add alleles. User specifies the list of alleles and corresponding initial distribution.
    """
    allele_dict = _allele_data_to_dict( allele_names_in, allele_inits_in )
    alleles.append( allele_dict )

def add_mutation( from_allele, to_allele, rate ):
    # Need to worry about allele sets
    """
    Public API function for user to add mutations as part of vector genetics configuration.
    A mutation is specified with a source allele, a destination allele, and a rate
    """
    mut_dict = dict()
    key = f"{from_allele}:{to_allele}"
    mut_dict[ key ] = rate
    allele_set_uniq_key = _get_allele_set_key_from_allele( from_allele )
    if allele_set_uniq_key not in mutations:
        mutations[ allele_set_uniq_key ] = dict()
    mutations[allele_set_uniq_key].update( mut_dict )

def add_trait( manifest, sex_genes, allele_pair, trait_name, trait_value ):
    """ 
    Use this function to add traits as part of vector genetics configuration.
    Should produce something like:: 

        {
           "Allele_Combinations": [["X", "X"],["a0", "a1"]],
           "Trait_Modifiers": {"INFECTED_BY_HUMAN": 0}
        },
    """
    if len(sex_genes) != 2 or sex_genes[0] not in [ "X", "Y" ] or sex_genes[1] not in [ "X", "Y" ]:
        raise ValueError( "sex_genes needs to have two values and can only be X or Y" )
    if len(allele_pair) != 2:
        raise ValueError( "allele_pair should have 2 values" )
    # TBD: Add check that the alleles referenced here have been 'declared' previously
    trait = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:GeneToTraitModifierConfig"] )
    trait.parameters.Allele_Combinations.append( sex_genes )
    trait.parameters.Allele_Combinations.append( allele_pair )

    # Trait_Modifiers is a keys-as-value thing so don't really have any schema help here.
    trait_dict = dict()
    trait_dict[ trait_name ] = trait_value
    trait.parameters.Trait_Modifiers.update( trait_dict )
    trait.parameters.finalize()
    # Store these and put them in config later
    traits.append( trait )

def add_resistance( manifest, insecticide_name, species, combo, blocking = 1.0, killing = 1.0 ):
    """
        Use this function to add insecticide resistances. An insecticide can have a list of resistances.
        Add each resistance separately with the same name::
    
            Insecticides = [
            {
              "Name": "pyrethroid",
              "Resistances": [
                {
                  "Allele_Combinations": [
                  [
                    "a1",
                    "a1"
                  ]
                 ],
                "Blocking_Modifier": 1.0,
                "Killing_Modifier": pyrethroid_killing,
                "Species": "gambiae"
              }
             ]
            },
    """
    def get_insecticide_by_name( insecticide_name ): 
        if insecticide_name in insecticides:
            #  print( "Found existing insecticide." )
            return insecticides[ insecticide_name ]

        new_insecticide = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:Insecticide"] )
        new_insecticide.parameters.Name = insecticide_name
        insecticides[ insecticide_name ] = new_insecticide
        #  print( "New insecticide." )
        return new_insecticide 

    insecticide = get_insecticide_by_name( insecticide_name )

    resistance = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:AlleleComboProbabilityConfig"] )
    resistance.parameters.Blocking_Modifier = blocking
    resistance.parameters.Killing_Modifier = killing
    resistance.parameters.Species = species
    resistance.parameters.Allele_Combinations = combo
    resistance.parameters.finalize()

    insecticide.parameters.Resistances.append( resistance.parameters )

# 
# INTERNAL VEC-GEN FUNCTIONS
#
def _allele_data_to_dict( allele_names, allele_values ):
    """
    This function creates a dictionary out of matching names and values arrays.
    The user shouldn't have to create dicts.
    """
    allele_dict = {}
    for idx in range(len(allele_names) ):
        allele = allele_names[ idx ]
        value = allele_values[ idx ]
        allele_dict[ allele ] = value
    return allele_dict

def set_genetics( vsp, manifest ):
    """
    set_genetics is a bit of glue code that needs to be called towards end of setting up VectorSpeciesParmeters.
    """
    for allele_dict in alleles:
        genes = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:VectorGene"] )
        genes.parameters.Alleles = allele_dict 
        allele_set_uniq_key = [ x for x in allele_dict.keys() ][ 0 ] # get 'hash' for dict
        if allele_set_uniq_key  in mutations.keys():
            mut_dict = mutations[allele_set_uniq_key]
            genes.parameters.Mutations = mut_dict
        genes.parameters.finalize()
        vsp.parameters.Genes.append( genes.parameters ) # too many 'parameters' 
    for trait in traits:
        vsp.parameters.Gene_To_Trait_Modifiers.append( trait.parameters )
    return vsp

def _get_allele_set_key_from_allele( allele_in ):
    """
    An internal utility function that gets the 'hash' to use as the key into the mutations dict for any given allele.
    """
    # Loop through allele_names and find list where this allele exists. Then get first element in that list.
    ret_key = None
    for allele_set in alleles:
        if allele_in in allele_set.keys():
            keys_list = [ x for x in allele_set.keys() ]
            ret_key = keys_list[0]
            break
    return ret_key 

