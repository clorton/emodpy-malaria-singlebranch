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


def print_params():
    """
    Just a useful convenience function for the user.
    """
    # Display exp_name and nSims
    # TBD: Just loop through them
    print("exp_name: ", params.exp_name)
    print("nSims: ", params.nSims)

def set_param_fn(config): 
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "MALARIA_SIM"

    import emodpy_malaria.config as conf
    config = conf.set_team_defaults( config, manifest )
    conf.set_species( config, [ "gambiae" ] )
    config = set_config.set_config( config )

    lhm = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
    lhm.parameters.Max_Larval_Capacity = 225000000
    lhm.parameters.Vector_Habitat_Type = "TEMPORARY_RAINFALL"
    conf.get_species_params( config, "gambiae" ).Larval_Habitat_Types.append( lhm.parameters )

    config.parameters.Base_Rainfall = 150
    config.parameters.Simulation_Duration = 365
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    #config.parameters.Serialization_Times = [ 365 ]
    config.parameters.Enable_Vector_Species_Report = 1
    #config["parameters"]["Insecticides"] = [] # emod_api gives a dict right now.
    config.parameters.Enable_Migration_Heterogeneity = 0
    config.parameters.pop( "Serialized_Population_Filenames" ) 

    config.parameters.Custom_Individual_Events = [ "Bednet_Got_New_One", "Bednet_Using", "Bednet_Discarded" ]
    config.parameters.Enable_Spatial_Output = 1 # remove when emodpy-malaria #35 is closed
    config.parameters.Spatial_Output_Channels = [
        "Adult_Vectors"
        , "New_Infections"
        , "Infectious_Vectors"
    ]

    """
    # Vector Genetics
    malconf.add_alleles( [ "tom", "dick", "harry" ], [ 0.5, 0.5, 0 ] )
    malconf.add_mutation( from_allele="tom", to_allele="dick", rate=0.5 )
    malconf.add_mutation( from_allele="tom", to_allele="harry", rate=0.1 )
    malconf.add_mutation( from_allele="dick", to_allele="harry", rate=0.1 )
    malconf.add_mutation( from_allele="harry", to_allele="tom", rate=0.3 )
    malconf.add_alleles( [ "this", "that", "the_other" ], [ 0.9, 0.05, 0.05 ] )
    malconf.add_mutation( from_allele="this", to_allele="that", rate=0.4444 )
    malconf.add_trait( manifest, [ "X", "X" ], [ "tom", "dick" ], "INFECTED_BY_HUMAN", 0 )
    malconf.add_resistance( manifest, "pyrethroid", "gambiae", [ [ "this", "that" ] ] )
    config = malconf.set_resistances( config )
    """

    # Vector Species Params
    return config

def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp
    import emod_api.interventions.outbreak as ob
    import emodpy_malaria.interventions.bednet as bednet 
    import emodpy_malaria.interventions.udbednet as udb

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file
    
    # print( f"Telling emod-api to use {manifest.schema_file} as schema." ) 
    nodes = [1402941398, 1402941399, 1402941400, 1402941401, 1402941404, 1402941410, 1403072469, 1403072470, 1403072471, 1403072472 ]
    camp.add( udb.UDBednet( camp, start_day=10, coverage=0.5, killing_eff=0.5, blocking_eff=0.5, node_ids=nodes ) )
    #camp.add( bednet.Bednet( camp, start_day=100, coverage=0.5, killing_eff=0.5, blocking_eff=0.5, usage_eff=0.5, insecticide="pyrethroid", node_ids=nodes ) )
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

    #demog = Demographics.from_template_node( lat=0, lon=0, pop=10000, name=1, forced_id=1 )
    input_file = malconf.get_file_from_http( "http://ipadvweb02.linux.idm.ctr:8000/" + manifest.population_input_path )
    demog = Demographics.from_pop_csv( input_file, site='burkina' )

    import emod_api.migration as mig 
    mig_partial = partial( mig.from_demog_and_param_gravity, gravity_params = [7.50395776e-06, 9.65648371e-01, 9.65648371e-01, -1.10305489e+00], id_ref='burkina', migration_type=mig.Migration.REGIONAL ) 

    return demog, mig_partial
    #return demog

def ep4_fn(task):
    task = emod_task.add_ep4_from_path(task, manifest.ep4_dir)
    return task


def general_sim( erad_path ):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    print_params()

    # Create a platform
    # Show how to dynamically set priority and node_group

    # create EMODTask 
    print("Creating EMODTask (from files)...")

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores")
    pl = RequirementsToAssetCollection( platform, requirements_path=manifest.requirements )

    # create EMODTask
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


    # Set task.campaign to None to not send any campaign to comps since we are going to override it later with
    # dtk-pre-process.
    print("Adding local assets (py scripts mainly)...")

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition( update_sim_random_seed, range(params.nSims) )

    # create experiment from builder
    print( f"Prompting for COMPS creds if necessary..." )
    experiment  = Experiment.from_builder(builder, task, name=params.exp_name) 

    other_assets = AssetCollection.from_id(pl.run())
    experiment.assets.add_assets(other_assets)

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
    general_sim( erad_path )

if __name__ == "__main__":
    # TBD: user should be allowed to specify (override default) erad_path and input_path from command line 
    plan = EradicationBambooBuilds.MALARIA_LINUX
    print("Retrieving Eradication and schema.json from Bamboo...")
    get_model_files( plan, manifest )
    print("...done.") 
    run_test( manifest.eradication_path )
