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


def set_mdp( config, manifest ):
    # Set malaria drug parameters
    """
    Use 
    dfs._set_defaults_for_schema_group(default,schema_json["config"]["MALARIA_SIM"]["Malaria_Drug_Params"]["<malaria_drug_name_goes_here>"])
    to get default malaria drug param dict. Convert to schema-backed version (that's an emod_api responsibility)
    dfs.load_config_as_rod

    Set params as desired.
    Do this for each malaria drug.
    Add to config (through emod_api if necessary, this might end up being an insertion which would normally be forbidden by schema-backed non-insertable dict)
    """
    # This initial code is just fumbling my way towards a solution; this code will be deeper down in a util function when done.
    # I'd rather these next two lines be under-the-hood
    mdp_default = { "parameters": { "schema": {} } }
    mdp = dfs.schema_to_config_subnode(manifest.schema_file, ["config","MALARIA_SIM","Malaria_Drug_Params","<malaria_drug_name_goes_here>"] )

    # Just demonstrating that we can set drug params. Values mean nothing at this time.
    mdp.parameters.Bodyweight_Exponent = 45
    mdp.parameters.Drug_Cmax = 100
    mdp.parameters.Drug_Decay_T1 = 1
    mdp.parameters.Drug_Decay_T2 = 1
    mdp.parameters.Drug_Dose_Interval = 1
    mdp.parameters.Drug_Fulltreatment_Doses = 1
    mdp.parameters.Drug_Gametocyte02_Killrate = 1
    mdp.parameters.Drug_Gametocyte34_Killrate = 1
    mdp.parameters.Drug_GametocyteM_Killrate = 1
    mdp.parameters.Drug_Hepatocyte_Killrate = 1
    mdp.parameters.Drug_PKPD_C50 = 1
    mdp.parameters.Drug_Vd = 1
    # This needs to be changed ASAP
    """
    mdp.parameters.Fractional_Dose_By_Upper_Age = [
                {
                    "Fraction_Of_Adult_Dose": 0.5,
                    "Upper_Age_In_Years": 5
                }
            ]
    """
    mdp.parameters.Max_Drug_IRBC_Kill = 1
 
    mdp_map = {}
    mdp.parameters.finalize()
    mdp_map["Chloroquine"] = mdp.parameters

    config.parameters.Malaria_Drug_Params = mdp_map
    return config


def set_vsp( config, manifest ):
    # Set vector species parameters
    vsp_default = { "parameters": { "schema": {} } } 

    vsp = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:VectorSpeciesParameters"] )

    # Add a Vector Species Params set. Opposite of MDP, go with defaults wherever possible
    # These are here, commented out, just to show what can be set. If we want some preset groups, we could have some functions
    # in the emodpy-malaria module.
    #vsp.parameters.Acquire_Modifier = 1
    #vsp.parameters.Adult_Life_Expectancy = 1
    #vsp.parameters.Anthropophily = 0.95
    #vsp.parameters.Aquatic_Arrhenius_1 = 1
    #vsp.parameters.Aquatic_Arrhenius_2 = 1
    #vsp.parameters.Aquatic_Mortality_Rate = 1
    ##vsp.parameters.Cycle_Arrhenius_1 = 1
    ##vsp.parameters.Cycle_Arrhenius_2 = 1
    ##vsp.parameters.Cycle_Arrhenius_Reduction_Factor = 1
    #vsp.parameters.Days_Between_Feeds = 1
    #vsp.parameters.Drivers = []
    #vsp.parameters.Immature_Duration = 1
    #vsp.parameters.Indoor_Feeding_Fraction = 1
    #vsp.parameters.Infected_Arrhenius_1 = 1
    #vsp.parameters.Infected_Arrhenius_2 = 1
    #vsp.parameters.Infected_Egg_Batch_Factor = 1
    #vsp.parameters.Infectious_Human_Feed_Mortality_Factor = 1
    #vsp.parameters.Male_Life_Expectancy = 1
    #vsp.parameters.Transmission_Rate = 1
    #vsp.parameters.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_NONE"

    # This needs to be changed once the schema for Larval_Habitat_Types is fixed. 
    # Keys-as-values means we have to do this
    vsp.parameters.Larval_Habitat_Types = {
        "TEMPORARY_RAINFALL": 11250000000
    }
    vsp.parameters.Name = "Gambiae"
    vsp.parameters.finalize()

    # config.parameters.Vector_Species_Params = list() # won't need this after schema is fixed.
    config.parameters.Vector_Species_Params.append( vsp.parameters )
    return config


def set_param_fn(config): 
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config = set_config.set_config( config )

    config.parameters.Base_Rainfall = 150
    config.parameters.Simulation_Duration = 365
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    #config.parameters.Serialization_Times = [ 365 ]
    config.parameters.Enable_Vector_Species_Report = 1
    #config["parameters"]["Insecticides"] = [] # emod_api gives a dict right now.
    config.parameters.pop( "Serialized_Population_Filenames" ) 

    # Set MalariaDrugParams
    config = set_mdp( config, manifest )

    # Vector Species Params
    config = set_vsp( config, manifest )
    return config


def build_camp():
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
    camp.add( bednet.Bednet( camp, start_day=100, coverage=0.5, killing_eff=0.5, blocking_eff=0.5, usage_eff=0.5 ) )
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

    demog = Demographics.fromBasicNode( lat=1, lon=2, pop=12345, name="Atlantic Base", forced_id=321 )
    return demog


def general_sim( erad_path, ep4_scripts ):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    print_params()

    platform = Platform("SLURM") 

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

    print("Adding asset dir...")
    task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)
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
