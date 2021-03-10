

from emodpy_malaria.reporters.builtin import ReportVectorGenetics, ReportVectorStats

"""
class GeneticsStratification:
    Genome = "GENOME"
    Specific_Genome = "SPECIFIC_GENOME"
    Allele = "ALLELE"
    Allele_Frequency = "ALLELE_FREQUENCY"
"""

class VectorGender:
    Female = "VECTOR_FEMALE"
    Male = "VECTOR_MALE"
    Both = "VECTOR_BOTH_GENDERS"


def _rvg_config_builder_female( params ):
    # defaults as of 27Nov2020
    # end defaults

    params.Include_Vector_State_Columns = False
    params.Gender = "VECTOR_FEMALE"
    params.Start_Day = 85
    params.Duration_Days = 30

    return params

def _rvg_config_builder_male( params ):
    params.Include_Vector_State_Columns = False
    params.Gender = "VECTOR_MALE"
    params.Start_Day = 85
    params.Duration_Days = 30

    return params

def get_report_vector_genetics(manifest, sex:VectorGender):
    reporter = ReportVectorGenetics()  # Create the reporter
    if sex == VectorGender.Female:
        reporter.config( _rvg_config_builder_female,
                         manifest)
    elif sex == VectorGender.Male:
        reporter.config( _rvg_config_builder_male,
                         manifest)
    return reporter

_rvs_species_list = ["Gambiae"]
def _rvs_config_builder( params ):
    params.Include_Gestation_Columns = True
    params.Species_List = _rvs_species_list
    params.Stratify_By_Species = True
    params.Include_Wolbachia_Columns = True
    return params

def get_report_vector_stats(manifest, species_list=None):
    reporter = ReportVectorStats()
    if species_list:
        _rvs_species_list = species_list
    reporter.config(_rvs_config_builder, manifest)
    return reporter

