#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files


import manifest


"""
This example downloads serialized files from the burnin/example
The important bits are in set_param_fn function and general_sim function
"""


def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # config = set_config.set_config( config )

    import emodpy_malaria.config as conf
    config = conf.set_team_defaults(config, manifest)

    config.parameters.Serialized_Population_Reading_Type = "READ"
    config.parameters.Serialization_Mask_Node_Read = 0
    config.parameters.Serialized_Population_Path = manifest.assets_input_dir # <--we uploaded files to here
    config.parameters.Serialized_Population_Filenames = ["state-00020-000.dtk", "state-00020-001.dtk"]

    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp

    import emodpy_malaria.interventions.bednet as bednet

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file

    # print( f"Telling emod-api to use {manifest.schema_file} as schema." ) 
    camp.add(bednet.Bednet(camp, start_day=100, coverage=1.0, killing_eff=1.0, blocking_eff=1.0, usage_eff=1.0,
                           node_ids=[]))
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
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demog = Demographics.from_params(tot_pop=100, num_nodes=4)
    return demog


def general_sim(erad_path, ep4_scripts):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", num_cores=2, node_group="idm_48cores", priority="Highest")
    experiment_name = "Create simulation from serialized files"

    # important bit
    # WE ARE GOING TO USE SERIALIZATION FILES GENERATED IN burnin_create
    from idmtools_platform_comps.utils.download.download import DownloadWorkItem, CompressType
    # navigating to the experiment.id file to retrieve experiment id
    with open("../burnin_create/experiment.id") as f:
        experiment_id = f.readline()

    dl_wi = DownloadWorkItem(
                             related_experiments=[experiment_id],
                             file_patterns=["output/*.dtk"],
                             simulation_prefix_format_str='serialization_files',
                             verbose=True,
                             output_path="",
                             delete_after_download=False,
                             include_assets=True,
                             compress_type=CompressType.deflate)

    dl_wi.run(wait_on_done=True, platform=platform)
    print("SHOULD BE DOWNLOADED")
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
        plugin_report=None  # report
    )

    print("Adding local assets (py scripts mainly)...")


    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

    print("Adding asset dir...")
    task.common_assets.add_directory(assets_directory=manifest.serialization_files)

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


def run_test(erad_path):
    general_sim(erad_path, manifest.my_ep4_assets)


if __name__ == "__main__":
    # TBD: user should be allowed to specify (override default) erad_path and input_path from command line 
    plan = EradicationBambooBuilds.MALARIA_LINUX
    print("Retrieving Eradication and schema.json from Bamboo...")
    get_model_files(plan, manifest)
    print("...done.")
    run_test(manifest.eradication_path)
