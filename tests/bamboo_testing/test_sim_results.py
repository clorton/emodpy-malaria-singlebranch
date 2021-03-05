import pathlib 
from functools import partial  
import unittest
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

from emodpy_malaria import config as malconf
import vector_report_support as vrs
import os
import sys
import pandas as pd

class TestSimResults(unittest.TestCase):

    def setUp(self):
        file_dir = os.path.dirname(__file__)
        sys.path.append(file_dir)
        self.plan = EradicationBambooBuilds.MALARIA_LINUX
        self.schema_path = os.path.join(file_dir , "./inputs/bin/schema.json")
        self.eradication = os.path.join(file_dir , "./inputs/bin/Eradication")
        self.manifest = self.dotdict({"schema_file": self.schema_path, "eradication_file": self.eradication})

    def update_sim_bic(self, simulation, value):
        simulation.task.config.parameters.Base_Infectivity_Constant  = value*0.1
        return {"Base_Infectivity": value}

    def update_sim_random_seed(self, simulation, value):
        simulation.task.config.parameters.Run_Number = value
        return {"Run_Number": value}

    def update_camp_start_day(self, simulation, value):
        #simulation.task.config.parameters.Run_Number = value
        build_camp_partial = partial( self.build_camp, actual_start_day=80+value*10 )
        simulation.task.create_campaign_from_callback( build_camp_partial )
        return {"Start_Day": 80+value*10}

    def set_config( self, config, tmp_loc = [], rate= 1.0, infectivity = 1.0 ):
        config.parameters.Acquisition_Blocking_Immunity_Decay_Rate = 0
        config.parameters.Acquisition_Blocking_Immunity_Duration_Before_Decay = 0
        config.parameters.Infectious_Period_Constant = 0
        config.parameters.Enable_Birth = 1
        #config.parameters.Enable_Coinfection = 1
        config.parameters.Enable_Demographics_Birth = 1
        config.parameters.Enable_Demographics_Reporting = 0
        config.parameters.Enable_Immune_Decay = 0
        config.parameters.Migration_Model = "NO_MIGRATION"
        config.parameters.Mortality_Blocking_Immunity_Decay_Rate = 0
        config.parameters.Mortality_Blocking_Immunity_Duration_Before_Decay = 270
        config.parameters.Run_Number = 99 
        config.parameters.Simulation_Duration = 60
        config.parameters.Enable_Demographics_Risk = 1
        config.parameters.Enable_Maternal_Infection_Transmission = 0
        config.parameters.Enable_Natural_Mortality = 0
        # Must make sure mosquitos are not dying from anything but vaccine
        config.parameters.Human_Feeding_Mortality = 0
        #config.parameters.Report_Vector_Genetics = 1

        return config

    def set_param_fn(self, config, whokill="Male"): 
        """
        This function is a callback that is passed to emod-api.config to set parameters The Right Way.
        """
        config.parameters.Simulation_Type = "MALARIA_SIM"
        import emodpy_malaria.config as conf
        config = conf.set_team_defaults( config, self.manifest )
        conf.set_species( config, [ "gambiae" ] )
        config = self.set_config( config )

        lhm = dfs.schema_to_config_subnode( self.manifest.schema_file, ["idmTypes","idmType:VectorHabitat"] )
        lhm.parameters.Max_Larval_Capacity = 0 # no egs allowed
        lhm.parameters.Vector_Habitat_Type = "TEMPORARY_RAINFALL"
        conf.get_species_params( config, "gambiae" ).Larval_Habitat_Types.append( lhm.parameters )

        # Important for a "clean" test
        species_params = config.parameters.Vector_Species_Params[0]
        species_params.Adult_Life_Expectancy = 730
        species_params.Egg_Batch_Size = 0


        config.parameters.Base_Rainfall = 150
        config.parameters.Simulation_Duration = 365
        config.parameters.Climate_Model = "CLIMATE_CONSTANT"
        config.parameters.Enable_Disease_Mortality = 0
        config.parameters.Egg_Saturation_At_Oviposition = "SATURATION_AT_OVIPOSITION"
        config.parameters.Enable_Vector_Species_Report = 1
        config.parameters.pop( "Serialized_Population_Filenames" ) 

        # Vector Genetics
        if whokill == "Male":
            malconf.add_resistance( self.manifest, "everybody_wants_some", "gambiae", [["X", "X"]])
            malconf.add_resistance( self.manifest, "everybody_wants_some", "gambiae", combo=[["X", "Y"]],
                                killing=0.0)
        elif whokill == "Female":
            malconf.add_resistance( self.manifest, "everybody_wants_some", "gambiae", [["X", "Y"]])
            malconf.add_resistance( self.manifest, "everybody_wants_some", "gambiae", combo=[["X", "X"]],
                                killing=0.0)

        elif whokill == "All":
            malconf.add_resistance( self.manifest, "everybody_wants_some", "gambiae", [["X", "Y"]], killing=0.0)
            malconf.add_resistance( self.manifest, "everybody_wants_some", "gambiae", combo=[["X", "X"]],
                                killing=0.0)

        elif whokill == "Mixed":
             malconf.add_resistance( self.manifest, "everybody_wants_some", "gambiae", [["X", "Y"]], killing=1.0)
             malconf.add_resistance( self.manifest, "everybody_wants_some", "gambiae", [["X", "X"]], killing=0.6)
    
        # malconf.add_resistance( self.manifest, "nokill_males", "gambiae", combo=[["X", "Y"]],
        #                         killing=0.0)
        config = malconf.set_resistances( config )

        return config

    def build_demog(self):
        """
        Build a demographics input file for the DTK using emod_api.
        Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
        Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
        TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.
        """
        import emodpy_malaria.demographics.MalariaDemographics as Demographics # OK to call into emod-api
        import emod_api.demographics.DemographicsTemplates as DT

        demog = Demographics.fromBasicNode( lat=0, lon=0, pop=10000, name=1, forced_id=1 )
        return demog


    # Space spraying intervention
    def build_camp(self, actual_start_day=1, current_insecticide="everybody_wants_some",
                coverage=1.0, killing_effectiveness=1.0 ):
        import emod_api.campaign as camp
        import emodpy_malaria.interventions.spacespraying as spray

        camp.schema_path = self.schema_path

        camp.add(spray.SpaceSpraying(camp, start_day=1, coverage=coverage,
                                    killing_eff=killing_effectiveness, constant_duration=730,
                                    insecticide=current_insecticide),
                first=True)
        return camp

    # I really don't want to set up a manifest
    class dotdict(dict):
        # Allows dot notation to attributes
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__
        
    def test_default_space_spraying_male(self):
        platform = Platform("SLURM") 

        task = emod_task.EMODTask.from_default2(
            config_path="default_config.json",
            eradication_path=self.eradication,
            campaign_builder=self.build_camp,
            schema_path=self.schema_path,
            param_custom_cb=self.set_param_fn,
            ep4_custom_cb=None,
            demog_builder=self.build_demog,
            plugin_report=None # report
        )


        reporter_female = vrs.get_report_vector_genetics(self.manifest, sex=vrs.VectorGender.Female)
        reporter_male = vrs.get_report_vector_genetics(self.manifest, sex=vrs.VectorGender.Male)
        
        task.reporters.add_reporter(reporter_male)
        task.reporters.add_reporter(reporter_female)

        builder = SimulationBuilder()
        # Can add to this for when I want a sweep test
        builder.add_sweep_definition( self.update_sim_random_seed, range(1))

        print( f"Prompting for COMPS creds if necessary..." )
        experiment  = Experiment.from_builder(builder, task, name="Space Spraying Default Test")

        experiment.run(wait_until_done=True, platform=platform)
        if not experiment.succeeded:
            print(f"Experiment {experiment.uid} failed.\n")
            exit()

        print(f"Experiment {experiment.uid} succeeded.")
        files = platform.get_files(experiment, ["output/ReportVectorGenetics_Female_GENOME.csv", "output/ReportVectorGenetics_Male_GENOME.csv"])
        for key, value in files.items():
            with open("./inputs/Females.csv", "w+") as file:
                file.write(files[key]["output/ReportVectorGenetics_Female_GENOME.csv"].decode('utf-8').strip())
            with open("./inputs/Males.csv", "w+") as file:
                file.write(files[key]["output/ReportVectorGenetics_Male_GENOME.csv"].decode('utf-8').strip())
        males = pd.read_csv("./inputs/Males.csv")['STATE_MALE']
        females = pd.read_csv("./inputs/Females.csv")['VectorPopulation'] # Why are these different? Hmm
        # Params set to killing only males by default
        self.assertTrue(all([num == 0 for num in males[90:]]), msg= f"There should be 0 males after day 90 but there are not")
        self.assertTrue(all([num != 0 for num in females[90:]]), msg=f"Should be more than 0 females after day 90 but there are not") # will add more info

    def test_default_space_spraying_all(self):
        platform = Platform("SLURM") 

        task = emod_task.EMODTask.from_default2(
            config_path="default_config.json",
            eradication_path=self.eradication,
            campaign_builder=self.build_camp,
            schema_path=self.schema_path,
            param_custom_cb=partial(self.set_param_fn, whokill="All"),
            ep4_custom_cb=None,
            demog_builder=self.build_demog,
            plugin_report=None # report
        )

        reporter_female = vrs.get_report_vector_genetics(self.manifest, sex=vrs.VectorGender.Female)
        reporter_male = vrs.get_report_vector_genetics(self.manifest, sex=vrs.VectorGender.Male)
        
        task.reporters.add_reporter(reporter_male)
        task.reporters.add_reporter(reporter_female)

        builder = SimulationBuilder()
        # Can add to this for when I want a sweep test
        builder.add_sweep_definition( self.update_sim_random_seed, range(1) )

        print( f"Prompting for COMPS creds if necessary..." )
        experiment  = Experiment.from_builder(builder, task, name="Space Spraying Default Test")

        experiment.run(wait_until_done=True, platform=platform)
        if not experiment.succeeded:
            print(f"Experiment {experiment.uid} failed.\n")
            exit()

        print(f"Experiment {experiment.uid} succeeded.")
        files = platform.get_files(experiment, ["output/ReportVectorGenetics_Female_GENOME.csv", "output/ReportVectorGenetics_Male_GENOME.csv"])
        for key, value in files.items():
            with open("./inputs/Females.csv", "w+") as file:
                file.write(files[key]["output/ReportVectorGenetics_Female_GENOME.csv"].decode('utf-8').strip())
            with open("./inputs/Males.csv", "w+") as file:
                file.write(files[key]["output/ReportVectorGenetics_Male_GENOME.csv"].decode('utf-8').strip())
        males = pd.read_csv("./inputs/Males.csv")['STATE_MALE']
        females = pd.read_csv("./inputs/Females.csv")['VectorPopulation'] # Why are these different? Hmm
        # Params set to killing only males by default
        self.assertTrue(all([num == 0 for num in males[90:]]), msg= f"There should be 0 males after day 90 but there are not")
        self.assertTrue(all([num == 0 for num in females[90:]]), msg=f"Should be more than 0 females after day 90 but there are not") # will add more info

    # Testing that coverage cooperates with different resistances
    def test_mixed_space_spray(self):
        platform = Platform("SLURM") 

        task = emod_task.EMODTask.from_default2(
            config_path="default_config.json",
            eradication_path=self.eradication,
            campaign_builder=partial(self.build_camp, killing_effectiveness=.05),
            schema_path=self.schema_path,
            param_custom_cb=partial(self.set_param_fn, whokill="Mixed"),
            ep4_custom_cb=None,
            demog_builder=self.build_demog,
            plugin_report=None # report
        )

        reporter_female = vrs.get_report_vector_genetics(self.manifest, sex=vrs.VectorGender.Female)
        reporter_male = vrs.get_report_vector_genetics(self.manifest, sex=vrs.VectorGender.Male)
        
        task.reporters.add_reporter(reporter_male)
        task.reporters.add_reporter(reporter_female)

        builder = SimulationBuilder()
        # Can add to this for when I want a sweep test
        builder.add_sweep_definition( self.update_sim_random_seed, range(1) )

        print( f"Prompting for COMPS creds if necessary..." )
        experiment  = Experiment.from_builder(builder, task, name="Space Spraying Default Test")

        experiment.run(wait_until_done=True, platform=platform)
        if not experiment.succeeded:
            print(f"Experiment {experiment.uid} failed.\n")
            exit()

        print(f"Experiment {experiment.uid} succeeded.")
        files = platform.get_files(experiment, ["output/ReportVectorGenetics_Female_GENOME.csv", "output/ReportVectorGenetics_Male_GENOME.csv"])
        for key, value in files.items():
            with open("./inputs/Females.csv", "w+") as file:
                file.write(files[key]["output/ReportVectorGenetics_Female_GENOME.csv"].decode('utf-8').strip())
            with open("./inputs/Males.csv", "w+") as file:
                file.write(files[key]["output/ReportVectorGenetics_Male_GENOME.csv"].decode('utf-8').strip())
        males = pd.read_csv("./inputs/Males.csv")['STATE_MALE']
        females = pd.read_csv("./inputs/Females.csv")['VectorPopulation'] # Why are these different? Hmm
        # Params set to killing only males by default
        for index, male in enumerate(males):
            self.assertGreater(male, females[index], msg=f"On day {index} there are more females than males")

