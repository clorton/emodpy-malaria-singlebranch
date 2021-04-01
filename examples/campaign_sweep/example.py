#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

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
import emod_api.config.default_from_schema_no_validation as dfs


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

"""
    We create a simulation with a SpaceSpraying intervention that has an insecticide to which 
    our vectors have resistance 

"""


def build_campaign(start_day=1, coverage=1.0, killing_effectiveness=0):
    """
    Adds a SpaceSpraying intervention, using parameters passed in
    Args:
        start_day: the day the intervention goes in effect
        coverage: portion of each node covered by the intervention
        killing_effectiveness: portion of vectors killed by the intervention

    Returns:
        campaign object
    """
    # adds a SpaceSpraying intervention
    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.spacespraying as spray

    campaign.schema_path = manifest.schema_file

    # adding SpaceSpraying from emodpy_malaria.interventions.spacespraying
    campaign.add(spray.SpaceSpraying(campaign, start_day=start_day, coverage=coverage,
                                     killing_eff=killing_effectiveness, constant_duration=73),
                 first=True)
    return campaign


def update_campaign_start_day(simulation, value):
    # updates the start day of the campaign from build_campaign
    build_campaign_partial = partial(build_campaign, start_day=value)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"Start_Day": value}


def update_campaign_killing_effectiveness(simulation, value):
    build_campaign_partial = partial(build_campaign, killing_effectiveness=value)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"killing_effectiveness": value}


def update_campaign_coverage(simulation, value):
    build_campaign_partial = partial(build_campaign, coverage=value)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"spray_coverage": value}



def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "MALARIA_SIM"
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    # you have to explicitly set larval habitats for the species currently


    config.parameters.Simulation_Duration = 80

    return config


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_template_node(lat=0, lon=0, pop=10000, name=1, forced_id=1)
    return demographics


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    platform = Platform("SLURMStage")  # use "SLURM" or "CALCULON" to run on comps.idmod.org

    # create EMODTask 
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_config_parameters,
        demog_builder=build_demographics
    )


    # Create simulation sweep with builder
    # sweeping over start day AND killing effectiveness - this will be a cross product
    builder = SimulationBuilder()

    # builder.add_sweep_definition(update_campaign_start_day, [1, 30, 50])
    # builder.add_sweep_definition(update_campaign_coverage, [0.96, 0.85, 0.73])
    builder.add_sweep_definition(update_campaign_killing_effectiveness, [0.8, 0.85, 0.9, 0.95, 1.0])

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name="Campaign Sweep, SpaceSpraying")

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


if __name__ == "__main__":
    # TBD: user should be allowed to specify (override default) erad_path and input_path from command line
    plan = EradicationBambooBuilds.MALARIA_LINUX
    print("Retrieving Eradication and schema.json from Bamboo...")
    get_model_files(plan, manifest)
    print("...done.")
    general_sim()
