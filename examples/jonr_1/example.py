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
    config.parameters.Simulation_Duration = 365*5
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    config.parameters.Enable_Vector_Species_Report = 1
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
    import emodpy_malaria.interventions.irs as irs
    import emodpy_malaria.interventions.drug as drug

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file
    
    # print( f"Telling emod-api to use {manifest.schema_file} as schema." )
    camp.add( irs.IRSHousingModification( camp, start_day=100, coverage=0.5, killing_eff=0.5, blocking_eff=0.5 ) )
    camp.add( drug.AntiMalarialDrug( camp, start_day=300, coverage=0.5 ) )
    """
    add_IRS(cb, start=start,
            coverage_by_ages=[{'coverage': coverage}],
            killing_config=WaningEffectBoxExponential(
                Initial_Effect=0.5,
                Decay_Time_Constant=150,
                Box_Duration=90
            ),
            nodeIDs=nodes)
    add_drug_campaign(cb, campaign_type= 'MDA', drug_code=drug, start_days=start_days, repetitions=1, tsteps_btwn_repetitions=30,
                      coverage=coverage, target_group={'agemin': 0, 'agemax': agemax})
    """
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
    import emod_api.migration.Migration as Migration

    demog = Demographics.from_synth_pop( tot_pop=2e4, num_nodes=2, frac_rural=0.5, id_ref="jonr_dual_node_malaria" )
    mig = Migration.from_synth_pop( pop=2e4, num_nodes=2, frac_rural=0.5, id_ref="jonr_dual_node_malaria", migration_type=Migration.Migration.REGIONAL ) 

    return demog, mig


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
        # 'class', 'Duration_Days', 'Event_Trigger_List', 'Individual_Property_Filter', 'Infectiousness_Bins', 'Nodeset_Config', 'Pretty_Format'
        return params

    reporter.config( msr_config_builder, manifest )
    task.reporters.add_reporter(reporter)


    reporter = MalariaTransmissionReport()  # Create the reporter
    def mtr_config_builder( params ):
        report_start = 1
        years = 1
        params.Duration_Days = (years-report_start)*365
        params.Start_Day = (report_start)*365
        params.Report_Description = "Jon's Transmission Report"
        params.Event_Trigger_List.append("NewInfectionEvent")
        # 'class', '', 'Event_Trigger_List', 'Nodeset_Config', 'Pretty_Format'

        return params

    reporter.config( mtr_config_builder, manifest )
    task.reporters.add_reporter(reporter)


    reporter = ReportHumanMigrationTracking()  # Create the reporter
    def hmr_config_builder( params ):
        return params

    reporter.config( hmr_config_builder, manifest )
    task.reporters.add_reporter(reporter)


def general_sim( erad_path, ep4_scripts ):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    print_params()

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
