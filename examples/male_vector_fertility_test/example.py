#!/usr/bin/env python3

import pathlib # for a join
from functools import partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
from emodpy_malaria.reporters.builtin import ReportVectorGenetics, ReportVectorStats
import emodpy_malaria.config as conf
import emod_api.config.default_from_schema_no_validation as dfs

from emodpy_malaria import config as malconf
import manifest
import vector_report_support as vrs

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

# region sweep partials
def update_sim_bic(simulation, value):
    simulation.task.config.parameters.Base_Infectivity_Constant  = value*0.1
    return {"Base_Infectivity": value}


def update_sim_random_seed(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def update_camp_start_day(simulation, value):
    #simulation.task.config.parameters.Run_Number = value
    build_camp_partial = partial( build_camp, actual_start_day=80+value*10 )
    simulation.task.create_campaign_from_callback( build_camp_partial )
    return {"Start_Day": 80+value*10}


def update_killing_config_effectiveness(simulation, value):
    #simulation.task.config.parameters.Run_Number = value
    build_camp_partial = partial( build_camp, current_insecticide="only_kill_male_silly",
                                  killing_effectiveness=value )
    simulation.task.create_campaign_from_callback( build_camp_partial )
    return {"killing_effectiveness": value}
# endregion

def set_malaria_config(config):
    config.parameters.Simulation_Type = "MALARIA_SIM"
    config.parameters.Infectious_Period_Constant = 0
    config.parameters.Enable_Demographics_Birth = 1
    config.parameters.Enable_Demographics_Reporting = 0
    config.parameters.Enable_Immune_Decay = 0
    config.parameters.Mortality_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Mortality_Blocking_Immunity_Duration_Before_Decay = 270
    config.parameters.Run_Number = 99
    config.parameters.Simulation_Duration = 60
    config.parameters.Enable_Demographics_Risk = 1
    config.parameters.Enable_Natural_Mortality = 1

    return config

def set_vsp( config, manifest ):
    # Add a Vector Species Params set. Opposite of MDP, go with defaults wherever possible
    # These are here, commented out, just to show what can be set. If we want some preset groups, we could have some functions
    # in the emodpy-malaria module.

    # This needs to be changed once the schema for Larval_Habitat_Types is fixed. 
    # Keys-as-values means we have to do this
    lhm = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
    lhm.parameters.Max_Larval_Capacity = 225000000
    lhm.parameters.Vector_Habitat_Type = "TEMPORARY_RAINFALL"
    vsp = conf.get_species_params( config, "gambiae" )
    vsp.Larval_Habitat_Types.append( lhm.parameters )
    vsp.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_EVERY_FEED"
    malconf.set_genetics( vsp, manifest ) # , alleles, allele_inits ) 

    vsp2 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:VectorSpeciesParameters"] )
    vsp2.parameters.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_EVERY_FEED"
    vsp2 = malconf.set_genetics(vsp2, manifest)  # , alleles, allele_inits )
    vsp2.parameters.Name = "SillySkeeter"
    lhm = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
    lhm.parameters.Max_Larval_Capacity = 225000000
    lhm.parameters.Vector_Habitat_Type = "TEMPORARY_RAINFALL"
    vsp2.parameters.Larval_Habitat_Types.append( lhm.parameters )

    vsp3 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes","idmType:VectorSpeciesParameters"] )
    vsp3.parameters.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_EVERY_FEED"
    vsp3 = malconf.set_genetics(vsp3, manifest)  # , alleles, allele_inits )
    vsp3.parameters.Name = "SuperSkeeter"
    lhm = dfs.schema_to_config_subnode( manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
    lhm.parameters.Max_Larval_Capacity = 225000000
    lhm.parameters.Vector_Habitat_Type = "TEMPORARY_RAINFALL"
    vsp3.parameters.Larval_Habitat_Types.append( lhm.parameters )

    #config.parameters.Vector_Species_Params.append(vsp.parameters)
    config.parameters.Vector_Species_Params.append(vsp2.parameters)
    config.parameters.Vector_Species_Params.append(vsp3.parameters)
    return config


def set_param_fn(config): 
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "MALARIA_SIM"
    config = conf.set_team_defaults(config, manifest)
    conf.set_species(config, ["gambiae"])
    config = set_malaria_config(config)

    config.parameters.Base_Rainfall = 150
    config.parameters.Simulation_Duration = 365
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    config.parameters.Egg_Saturation_At_Oviposition = "SATURATION_AT_OVIPOSITION"
    config.parameters.Enable_Vector_Species_Report = 1
    config.parameters.pop( "Serialized_Population_Filenames" ) 


    # Vector Genetics
    malconf.add_resistance(manifest,
                           insecticide_name="only_kill_male_silly",
                           species="gambiae",
                           combo=[["X", "*"]],
                           killing=0.0)
    malconf.add_resistance(manifest,
                           insecticide_name="only_kill_male_silly",
                           species="SillySkeeter",
                           combo=[["X", "X"]],
                           killing=0.0)

    config = malconf.set_resistances( config )

    # Vector Species Params
    config = set_vsp( config, manifest )
    return config


def build_camp( actual_start_day=90, current_insecticide="kill_male_silly",
                coverage=1.0, killing_effectiveness=0.5 ):
    import emod_api.campaign as camp
    import emodpy_malaria.interventions.spacespraying as spray

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file

    # print( f"Telling emod-api to use {manifest.schema_file} as schema." )
    camp.add(spray.SpaceSpraying(camp, start_day=actual_start_day, coverage=coverage,
                                 killing_eff=killing_effectiveness, constant_duration=730,
                                 insecticide=current_insecticide),
             first=True)
    return camp


def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics # OK to call into emod-api

    demog = Demographics.from_template_node( lat=0, lon=0, pop=10000, name=1, forced_id=1 )
    return demog


def ep4_fn(task):
    task = emod_task.add_ep4_from_path(task, manifest.ep4_path)
    return task


def general_sim( erad_path, ep4_scripts ):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """

    platform = Platform("Calculon") 

    # create EMODTask 
    print("Creating EMODTask (from files)...")
    
    task = emod_task.EMODTask.from_default2(
            config_path="my_config.json",
            eradication_path=manifest.eradication_path,
            campaign_builder=build_camp,
            schema_path=manifest.schema_file,
            param_custom_cb=set_param_fn,
            ep4_custom_cb=None,
            demog_builder=build_demog,
            plugin_report=None # report
        )

    #print("Adding asset dir...")
    #task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)

    reporter_female = vrs.get_report_vector_genetics(manifest, sex=vrs.VectorGender.Female)
    task.reporters.add_reporter(reporter_female)  # Add the reporter

    reporter_male = vrs.get_report_vector_genetics(manifest, sex=vrs.VectorGender.Male)
    task.reporters.add_reporter(reporter_male)  # Add the reporter

    reporter_vstats = vrs.get_report_vector_stats(manifest, species_list=["gambiae","SillySkeeter"])
    task.reporters.add_reporter(reporter_vstats)

    # Set task.campaign to None to not send any campaign to comps since we are going to override it later with
    # dtk-pre-process.
    print("Adding local assets (py scripts mainly)...")

    seeds = 1
    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition( update_sim_random_seed, range(seeds))
    builder.add_sweep_definition( update_killing_config_effectiveness, [0.0, 0.2, 0.4, 0.8, 1.0] )

    # create experiment from builder
    print( f"Prompting for COMPS creds if necessary..." )
    experiment  = Experiment.from_builder(builder, task, name="Malaria SpaceSpraying kill male silly_skeeter")

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
    general_sim( erad_path, ["dtk_post_process.py"] )

if __name__ == "__main__":
    # TBD: user should be allowed to specify (override default) erad_path and input_path from command line 
    plan = EradicationBambooBuilds.MALARIA_LINUX
    print("Retrieving Eradication and schema.json from Bamboo...")
    get_model_files( plan, manifest )
    print("...done.") 
    run_test( manifest.eradication_path )
