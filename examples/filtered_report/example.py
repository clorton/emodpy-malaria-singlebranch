#!/usr/bin/env python3

import pathlib # for a join
from functools import partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
# from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection
# from idmtools_models.templated_script_task import get_script_wrapper_unix_task

# emodpy
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
from emodpy.reporters.custom import *
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
    config = conf.set_team_defaults(config, manifest)
    config = set_config.set_config(config)
    conf.set_species( config, [ "gambiae" ] )

    lhm = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
    lhm.parameters.Max_Larval_Capacity = 2*112500000
    lhm.parameters.Vector_Habitat_Type = "TEMPORARY_RAINFALL"
    conf.get_species_params( config, "gambiae" ).Larval_Habitat_Types.append( lhm.parameters )

    conf.get_drug_params( config, "Chloroquine" ).Drug_Cmax = 44 # THIS IS NOT SCHEMA ENFORCED. Needs design thought. 
    config.parameters.Base_Rainfall = 150
    config.parameters.Simulation_Duration = 365
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    #config.parameters.Serialization_Times = [ 365 ]
    config.parameters.Enable_Vector_Species_Report = 1
    #config["parameters"]["Insecticides"] = [] # emod_api gives a dict right now.
    config.parameters.pop( "Serialized_Population_Filenames" ) 

    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp
    import emod_api.interventions.outbreak as ob
    import emodpy_malaria.interventions.bednet as bednet
    import emodpy_malaria.interventions.treatment_seeking as ts

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file
    
    # print( f"Telling emod-api to use {manifest.schema_file} as schema." ) 
    #camp.add( bednet.Bednet( camp, start_day=100, coverage=1.0, killing_eff=1.0, blocking_eff=1.0, usage_eff=1.0, node_ids=[321] ) )
    ts.add( camp, start_day=1, node_ids=[321] )
    return camp


def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics # OK to call into emod-api

    demog = Demographics.from_template_node( lat=1, lon=2, pop=12345, name="Atlantic Base", forced_id=321, init_prev=0.005 )
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


    # Add event report
    reporter = ReportEventCounter()  # Create the reporter
    def rec_config_builder( params ): # not used yet
        return params
    task.reporters.add_reporter(reporter)


    from emodpy_malaria.reporters.builtin import FilteredMalariaReport
    def fmr_config_builder( params ):
        throwaway = 0
        start_day=throwaway * 365
        end_day=(throwaway + 1) * 365
        """
        These are the params from the schema at time of coding (3/23/21):
        Start_Day
        End_Day
        Inset_Chart_Has_Interventions
        Inset_Chart_Reporting_Include_30Day_Avg_Infection_Duration
        Node_IDs_Of_Interest
        Report_File_Name
        Sim_Types
        """
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = list()
        #params.description = "tbd"
        return params
    filtered_report = FilteredMalariaReport()
    filtered_report.config( fmr_config_builder, manifest )
    task.reporters.add_reporter(filtered_report) 


    print("Adding local assets (py scripts mainly)...")

    if ep4_scripts is not None:
        for asset in ep4_scripts:
            pathed_asset = Asset(pathlib.PurePath.joinpath(manifest.ep4_path, asset), relative_path="python")
            task.common_assets.add_asset(pathed_asset)

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition( update_sim_random_seed, range(params.nSims) )

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
