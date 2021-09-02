#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

import manifest

"""
    In this example we are adding a couple of drug campaigns - a scheduled and a triggered one

"""


def build_campaign():
    """
        Adding drug campaigns
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.drug_campaign as drug_campaign
    campaign.schema_path = manifest.schema_file

    # Please note: "add_MDA" and other specific campaigns cannot be added directly as there are
    # parameters configured for them inside the add_drug_campaign function

    # Please note: there is no campaign.add() in here unlike other interventions. This intervention adds itself
    # to the campaign (as it should be!)

    # straighforward mda that run on day 11 and then repeats 2 more times (3 total) every three days, distributing
    # to 0.3 of population
    drug_campaign.add_drug_campaign(camp=campaign, campaign_type="MDA", drug_code="DHA_PQ", start_days=[11],
                                    repetitions=3, tsteps_btwn_repetitions=3, coverage=0.3,
                                    receiving_drugs_event_name="MDA")

    # this is msat (mass screening and treatment) which is triggered by a birthday, but only listens for the
    # trigger for 60 time steps(days) with treatment delayed by one time step (a day)
    drug_campaign.add_drug_campaign(camp=campaign, campaign_type="MSAT", drug_code="SPP", start_days=[20],
                                    coverage=0.78, listening_duration=60,
                                    trigger_condition_list=["HappyBirthday"], treatment_delay=1,
                                    receiving_drugs_event_name="MSAT")

    return campaign


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # You have to set simulation type explicitly before you set other parameters for the simulation
    config.parameters.Simulation_Type = "MALARIA_SIM"
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["arabiensis"])

    config.parameters.Simulation_Duration = 100

    return config


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_template_node(lat=0, lon=0, pop=300, name=1, forced_id=1)
    return demographics


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores")

    experiment_name = "Drug Campaigns example"

    # create EMODTask
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,  # <--- WHERE THE INTERVENTION IS
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_config_parameters,
        demog_builder=build_demographics
    )

    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

    # Adding ReportEventCounter report
    from emodpy_malaria.reporters.builtin import ReportEventCounter

    def fmr_config_builder(params):
        params.Event_Trigger_List = ["HappyBirthday", "MDA", "MSAT"]
        return params

    report = ReportEventCounter()
    report.config(fmr_config_builder, manifest)
    task.reporters.add_reporter(report)


    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.")

    # Save experiment id to file
    with open("experiment.id", "w") as fd:
        fd.write(experiment.uid.hex)


if __name__ == "__main__":
    # Getting the latest LINUX version of eradicaiton app
    plan = EradicationBambooBuilds.MALARIA_LINUX
    print("Retrieving Eradication and schema.json from Bamboo...")
    get_model_files(plan, manifest)
    print("...done.")
    general_sim()
