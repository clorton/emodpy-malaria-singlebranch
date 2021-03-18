#!/usr/bin/env python3

import pathlib # for a join
from functools import partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

import manifest
from set_config import set_param_fn

def update_sim_bic(simulation, value):
    simulation.task.config.parameters.Base_Infectivity_Constant  = value*0.1
    return {"Base_Infectivity": value}


def update_sim_random_seed(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp
    import emod_api.interventions.outbreak as ob
    import emodpy_malaria.interventions.ivermectin as ivermectin
    import emodpy_malaria.interventions.irs as irs
    import emodpy_malaria.interventions.drug as drug

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file

    camp.add(ivermectin.Ivermectin(
        schema_path_container=camp
        , start_day=10
        , target_coverage=0.34
        , killing_effect=0.8
        , killing_duration_box=3
    ))
    camp.add(ivermectin.Ivermectin(
        schema_path_container=camp
        , start_day=15
        , target_num_individuals=123
        , killing_effect=0.76
        , killing_exponential_decay_rate=0.2
    ))
    camp.add(ivermectin.Ivermectin(
        schema_path_container=camp
        , start_day=20
        , target_coverage=0.45
        , killing_effect=0.65
        , killing_duration_box=2
        , killing_exponential_decay_rate=0.25
    ))
    camp.add(ivermectin.Ivermectin(
        schema_path_container=camp
        , start_day=20
        , target_coverage=0.45
        , killing_effect=0.65
        , killing_duration_box=2
        , killing_exponential_decay_rate=0.25
    ))
    camp.add(ivermectin.Ivermectin(
        schema_path_container=camp
        , start_day=20
        , target_num_individuals=751
        , killing_effect=0.65
        , killing_duration_box=2
        , killing_exponential_decay_rate=0.25
    ))
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
    import emodpy_malaria.demographics.MalariaDemographics as Demographics

    demog = Demographics.from_params(tot_pop=2e4, num_nodes=1, frac_rural=0.5,
                                     id_ref="cwiswell_single_node_malaria")

    return demog


def add_reports( task, manifest ):
    """
    Inbox:
    """

    from emodpy_malaria.reporters.builtin import MalariaSummaryReport
    from emodpy_malaria.reporters.builtin import MalariaTransmissionReport
    from emodpy.reporters.builtin import ReportHumanMigrationTracking
    reporter = MalariaSummaryReport()  # Create the reporter
    def msr_config_builder( params ):
        params.Report_Description = "Annual Report"
        params.Start_Day = 2*365
        params.Reporting_Interval = 365
        params.Max_Number_Reports = 1
        params.Age_Bins = [2, 10, 125]
        params.Parasitemia_Bins = [0, 50, 200, 500, 2000000]
        params.Event_Trigger_List.append("NewInfectionEvent")
        return params

    reporter.config( msr_config_builder, manifest )
    task.reporters.add_reporter(reporter)


def general_sim( erad_path, ep4_scripts ):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """

    platform = Platform("Calculon") 

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

    add_reports( task, manifest )


    #print("Adding asset dir...")
    #task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)
    print("Adding local assets (py scripts mainly)...")

    if ep4_scripts is not None:
        for asset in ep4_scripts:
            pathed_asset = Asset(pathlib.PurePath.joinpath(manifest.ep4_path, asset), relative_path="python")
            task.common_assets.add_asset(pathed_asset)

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition( update_sim_random_seed, range(10) )

    # create experiment from builder
    print( f"Prompting for COMPS creds if necessary..." )
    experiment  = Experiment.from_builder(builder, task, name="Ivermectin sample experiment")

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
