#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
    RequirementsToAssetCollection
from idmtools_models.templated_script_task import get_script_wrapper_unix_task

# emodpy
from emodpy.emod_task import EMODTask
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
from emodpy_malaria.reporters.builtin import ReportVectorGenetics
import emod_api.config.default_from_schema_no_validation as dfs

from emodpy_malaria import config as malaria_config
import manifest

"""
In this example, we add vector genetics to the vector population and insecticide resistance, 
adds a VectorGeneticsReporter.
The important bits are in set_param_fn, build_campaign


"""



def set_param_fn(config):
    """
        Sets configuration parameters from the malaria defaults and explicitly sets
        the vector genetics paramters and insecticide resistance parameters
    Args:
        config:

    Returns:
        completed config
    """
    config.parameters.Simulation_Type = "MALARIA_SIM"
    config = malaria_config.set_team_defaults(config, manifest)  # team defaults

    malaria_config.set_species(config, species_to_select=["gambiae"])

    # the following lines define alleles, mutations and traits and they need "set_genetics" to actually be added
    # Vector Genetics, the main purpose of this example.
    malaria_config.add_alleles(["a", "b", "c"], [0.5, 0.5, 0])
    malaria_config.add_mutation(from_allele="a", to_allele="b", rate=0.05)
    malaria_config.add_mutation(from_allele="b", to_allele="c", rate=0.1)
    malaria_config.add_mutation(from_allele="c", to_allele="a", rate=0.1)
    malaria_config.add_mutation(from_allele="a", to_allele="c", rate=0.03)

    # another set of alleles
    malaria_config.add_alleles(["one", "two", "three"], [0.9, 0.05, 0.05])
    malaria_config.add_mutation(from_allele="one", to_allele="three", rate=0.04)

    # these are the traits/benefits based on the alleles
    # protects vectors from infection
    malaria_config.add_trait(manifest, [["X", "X"], ["a", "*"]], "INFECTED_BY_HUMAN", 0)
    # vectors make more eggs
    malaria_config.add_trait(manifest, [["b", "b"], ["one", "two"]], "FECUNDITY", 10)

    # this actually sets all the parameters defined above to gambiae species
    malaria_config.set_genetics(malaria_config.get_species_params(config, "gambiae"), manifest)

    # adding insecticide resistance to "pyrenthroid"
    malaria_config.add_resistance(manifest, "pyrethroid", "gambiae", [["three", "three"]], blocking=0.0,
                                  killing=0.0)
    # this actually sets all the resistance parameters
    config = malaria_config.set_resistances(config)
    config.parameters.Simulation_Duration = 10

    return config


def build_campaign():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.bednet as bednet
    import emodpy_malaria.interventions.mosquitorelease as mr

    # This isn't desirable. Need to think about right way to provide schema (once)
    campaign.schema_path = manifest.schema_file

    # print( f"Telling emod-api to use {manifest.schema_file} as schema." )
    campaign.add(bednet.Bednet(campaign, start_day=1, coverage=0.5, killing_eff=0.7, blocking_eff=0.5, usage_eff=0.5,
                               insecticide="pyrethroid"))

    campaign.add(
        mr.MosquitoRelease(campaign, start_day=1, by_number=True, number=20000, infectious=0.2, species="gambiae",
                           genome=[["X", "X"], ["a", "b"], ["three", "three"]]))

    return campaign


def build_demog():
    """
        Builds demographics
    Returns:
        complete demographics
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    demog = Demographics.from_template_node(lat=0, lon=0, pop=100, name=1, forced_id=1)

    return demog


def general_sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
    experiment_name = "Vector Genetics and Insecticide Resistance example"

    # create EMODTask 
    print("Creating EMODTask (from files)...")
    task = EMODTask.from_default2(
        config_path="my_config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_custom_cb=None,
        demog_builder=build_demog,
        plugin_report=None  # report
    )

    def rvg_config_builder(params):
        params.Include_Vector_State_Columns = False
        params.Allele_Combinations_For_Stratification = [
            ["a"],
            ["b"]
        ]

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
    reporter.config(rvg_config_builder, manifest)  # Config the reporter
    task.reporters.add_reporter(reporter)  # Add the reporter

    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

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
    print()
    print(experiment.uid.hex)



if __name__ == "__main__":
    # TBD: user should be allowed to specify (override default) erad_path and input_path from command line 
    plan = EradicationBambooBuilds.MALARIA_LINUX
    print("Retrieving Eradication and schema.json from Bamboo...")
    get_model_files(plan, manifest)
    print("...done.")
    general_sim()
