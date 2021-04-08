#!/usr/bin/env python3

import pathlib # for a join
from functools import partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection
from idmtools_models.templated_script_task import get_script_wrapper_unix_task

# emodpy
from emodpy.emod_task import EMODTask
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
from emodpy_malaria.reporters.builtin import ReportVectorGenetics
import emod_api.config.default_from_schema_no_validation as dfs
from emodpy.emod_campaign import EMODCampaign

from emodpy_malaria import config as malconf
import params
import set_config
import manifest

# ****************************************************************
# Features to support:
#
#  Read experiment info from a json file
#  Add Eradication.exe as an asset (Experiment level)
#  Add Custom file as an asset (Simulation level)
#  Add the local asset directory to the task
#  Use builder to sweep simulations
#  How to run dtk_pre_process.py as pre-process
#  Save experiment info to file
# ****************************************************************

def update_sim_bic(simulation, value):
    simulation.task.config.parameters.Base_Infectivity_Constant  = value*0.1
    return {"Base_Infectivity": value}

def update_sim_random_seed(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}

def update_camp_start_day(simulation, value):
    #simulation.task.config.parameters.Run_Number = value
    build_camp_partial = partial( build_camp, start_day_in=80+value*10 )
    simulation.task.create_campaign_from_callback( build_camp_partial )
    return {"Start_Day": 80+value*10}


def print_params():
    """
    Just a useful convenience function for the user.
    """
    # Display exp_name and nSims
    # TBD: Just loop through them
    print("exp_name: ", params.exp_name)
    print("nSims: ", params.nSims)


def set_vsp( config, mani ):
    vsp = malconf.set_genetics( malconf.get_species_params( config, "gambiae" ), mani )

    # config.parameters.Vector_Species_Params = list() # won't need this after schema is fixed.
    # I think the new way should just set this in place. Check this!!!
    #config.parameters.Vector_Species_Params = vsp.parameters
    lhm = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
    lhm.parameters.Max_Larval_Capacity = 225000000
    lhm.parameters.Vector_Habitat_Type = "TEMPORARY_RAINFALL"
    malconf.get_species_params( config, "gambiae" ).Larval_Habitat_Types.append( lhm.parameters )
    return config

def set_param_fn(config): 
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "MALARIA_SIM"

    import emodpy_malaria.config as conf
    config = conf.set_team_defaults( config, manifest ) # team defaults
    conf.set_species( config, [ "gambiae" ] )
    config = set_config.set_config( config ) # you can set scenario config params in a standalone file

    # or you can set the here.
    config.parameters.Base_Rainfall = 150
    config.parameters.Simulation_Duration = 365

    config.parameters.Base_Rainfall = 150
    config.parameters.Simulation_Duration = 365
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    #config.parameters.Serialization_Times = [ 365 ]
    config.parameters.Enable_Vector_Species_Report = 1
    #config["parameters"]["Insecticides"] = [] # emod_api gives a dict right now.
    config.parameters.pop( "Serialized_Population_Filenames" ) 

    # Vector Genetics
    malconf.add_alleles( [ "tom", "dick", "harry" ], [ 0.5, 0.5, 0 ] )
    malconf.add_mutation( from_allele="tom", to_allele="dick", rate=0.5 )
    malconf.add_mutation( from_allele="tom", to_allele="harry", rate=0.1 )
    malconf.add_mutation( from_allele="dick", to_allele="harry", rate=0.1 )
    malconf.add_mutation( from_allele="harry", to_allele="tom", rate=0.3 )
    malconf.add_alleles( [ "this", "that", "the_other" ], [ 0.9, 0.05, 0.05 ] )
    malconf.add_mutation( from_allele="this", to_allele="that", rate=0.4444 )
    malconf.add_trait( manifest, [[ "X", "X" ], [ "tom", "dick" ]], "INFECTED_BY_HUMAN", 0 )
    malconf.add_resistance( manifest, "pyrethroid", "gambiae", [ [ "this", "that" ] ] )
    config = malconf.set_resistances( config )

    # Vector Species Params
    config = set_vsp( config, manifest )
    return config

def build_camp( start_day_in=100 ):
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp
    import emod_api.interventions.outbreak as ob
    import emodpy_malaria.interventions.bednet as bednet

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file
    
    # print( f"Telling emod-api to use {manifest.schema_file} as schema." )
    camp.add( bednet.Bednet( camp, start_day=start_day_in, coverage=0.5, killing_eff=0.5, blocking_eff=0.5, usage_eff=0.5, insecticide="pyrethroid" ), first=True )
    return camp


def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics # OK to call into emod-api
    import emod_api.demographics.DemographicsTemplates as DT

    demog = Demographics.from_template_node( lat=0, lon=0, pop=10000, name=1, forced_id=1 )
    return demog


def general_sim( erad_path, ep4_scripts ):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    print_params()

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores")

    #pl = RequirementsToAssetCollection( platform, requirements_path=manifest.requirements )

    # create EMODTask 
    print("Creating EMODTask (from files)...")
    
    task = EMODTask.from_default2(
            config_path="my_config.json",
            eradication_path=manifest.eradication_path,
            campaign_builder=build_camp,
            schema_path=manifest.schema_file,
            param_custom_cb=set_param_fn,
            ep4_custom_cb=None,
            demog_builder=build_demog,
            plugin_report=None # report
        )

    #demog_path = build_demog()
    #task.common_assets.add_asset( demog_path )

    def rvg_config_builder( params ):
        params.Include_Vector_State_Columns = False
        params.Allele_Combinations_For_Stratification = [
            ["tom"],
            ["dick"]
        ]
        # params.Alleles_For_Stratification = [ "tom", "dick" ] # this works
        # params.Specific_Genome_Combinations_For_Stratification = 
        """
        E.g.,
        [
            {
                "Allele_Combination": [
                    ["X", "X"],
                    ["a1", "*"]
                ]
            },
            {
                "Allele_Combination": [
                    ["X", "X"],
                    ["a0", "a0"]
                ]
            }
        ]
        """
        return params

    reporter = ReportVectorGenetics()  # Create the reporter
    reporter.config( rvg_config_builder, manifest )  # Config the reporter
    task.reporters.add_reporter(reporter)  # Add thre reporter

    # Set task.campaign to None to not send any campaign to comps since we are going to override it later with
    # dtk-pre-process.
    print("Adding local assets (py scripts mainly)...")

    if ep4_scripts is not None:
        for asset in ep4_scripts:
            pathed_asset = Asset(pathlib.PurePath.joinpath(manifest.ep4_path, asset), relative_path="python")
            task.common_assets.add_asset(pathed_asset)

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    #builder.add_sweep_definition( update_sim_random_seed, range(params.nSims) )
    builder.add_sweep_definition( update_camp_start_day, range(params.nSims) )

    # create experiment from builder
    print( f"Prompting for COMPS creds if necessary..." ) 
    experiment  = Experiment.from_builder(builder, task, name=params.exp_name) 

    #other_assets = AssetCollection.from_id(pl.run())
    #experiment.assets.add_assets(other_assets)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.")

    # Save experiment id to file
    with open("COMPS_ID", "w") as fd:
        fd.write(experiment.uid.hex)
    print()
    print(experiment.uid.hex) 
    

def run_test( erad_path ):
    general_sim( erad_path, manifest.my_ep4_assets )

if __name__ == "__main__":
    # TBD: user should be allowed to specify (override default) erad_path and input_path from command line 
    plan = EradicationBambooBuilds.MALARIA_LINUX
    print("Retrieving Eradication and schema.json from Bamboo...")
    get_model_files( plan, manifest )
    print("...done.") 
    run_test( manifest.eradication_path )
