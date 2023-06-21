import coverage
import unittest
from pathlib import Path
import os

loader = unittest.TestLoader()
cov = coverage.Coverage(source=[
    "emodpy_malaria.interventions.adherentdrug",
    "emodpy_malaria.interventions.bednet",
    "emodpy_malaria.interventions.common",
    "emodpy_malaria.interventions.community_health_worker",
    "emodpy_malaria.interventions.diag_survey",
    "emodpy_malaria.interventions.drug",
    "emodpy_malaria.interventions.drug_campaign",
    "emodpy_malaria.interventions.inputeir",
    "emodpy_malaria.interventions.irs",
    "emodpy_malaria.interventions.ivermectin",
    "emodpy_malaria.interventions.larvicide",
    "emodpy_malaria.interventions.mosquitorelease",
    "emodpy_malaria.interventions.outbreak",
    "emodpy_malaria.interventions.outdoorrestkill",
    "emodpy_malaria.interventions.scale_larval_habitats",
    "emodpy_malaria.interventions.spacespraying",
    "emodpy_malaria.interventions.sugartrap",
    "emodpy_malaria.interventions.treatment_seeking",
    "emodpy_malaria.interventions.usage_dependent_bednet",
    "emodpy_malaria.interventions.vaccine",
    "emodpy_malaria.demographics.MalariaDemographics",
    "emodpy_malaria.malaria_config",
    "emodpy_malaria.vector_config",
    "emodpy_malaria.reporters.builtin",
    "emodpy_malaria.weather.weather_data",
    "emodpy_malaria.weather.weather_metadata",
    "emodpy_malaria.weather.weather_request",
    "emodpy_malaria.weather.weather_set",
    "emodpy_malaria.weather.weather_utils",
    "emodpy_malaria.weather.weather_variable",
])
cov.start()

# First, load and run the unittest tests
from test_import import MalariaTestImports
from test_malaria_interventions import TestMalariaInterventions
from test_malaria_interventions_as_files import MalariaInterventionFileTest
from test_malaria_reporters import TestMalariaReport
from test_malaria_config import TestMalariaConfig
from test_treatment_seeking import TreatmentSeekingTest
from test_demog import DemoTest
from weather.test_e2e import WeatherE2ETests
from weather.test_e2e_comps import WeatherE2ECompsTests
from weather.test_weather_data import WeatherDataTests
from weather.test_weather_metadata import WeatherMetadataTests
from weather.test_weather_request import WeatherRequestTests
from weather.test_weather_scenarios import WeatherScenariosTests
from weather.test_weather_set import WeatherSetTests

test_classes_to_run = [MalariaTestImports,
                       TestMalariaInterventions,
                       MalariaInterventionFileTest,
                       TestMalariaReport,
                       TestMalariaConfig,
                       TreatmentSeekingTest,
                       DemoTest,
                       WeatherE2ETests,
                       WeatherE2ECompsTests,
                       WeatherDataTests,
                       WeatherMetadataTests,
                       WeatherRequestTests,
                       WeatherScenariosTests,
                       WeatherSetTests]

suites_list = []
for tc in test_classes_to_run:
    suite = loader.loadTestsFromTestCase(tc)
    suites_list.append(suite)
    pass

big_suite = unittest.TestSuite(suites_list)
runner = unittest.TextTestRunner()
results = runner.run(big_suite)

# Add examples to test coverage (comment out if you don't want to include examples)
examples_dir = Path.cwd().parent.parent.joinpath('examples')
examples_to_run = [
    "add_reports",
    "burnin_create",
    "burnin_create_and_use_sweep_larval_habitat",
    "burnin_create_infections",
    "burnin_create_parasite_genetics",
    "burnin_use",
    "campaign_sweep",
    "create_demographics",
    "demographics_sweep",
    "diagnostic_survey",
    "download_files",
    "drug_campaign",
    "embedded_python_post_processing",
    "fpg_example",
    "inputEIR",
    "irs",
    "ivermectin",
    "jonr_1",
    "male_vector_fertility_test",
    "microsporidia",
    "migration_spatial_malaria_sim",
    "migration_spatial_vector_sim",
    "outdoor_rest_kill_male_mosquitoes",
    "rcd_elimination_emodpy",
    "run_with_unobserved_importation",
    "scale_larval_habitats",
    "serialization_remove_infections",
    "serialization_replace_genomes",
    "start_here",
    "vector_basic",
    "vector_genetics_insecticide_resistance",
    "vector_genetics_vector_sim",
    "weather"
]

def run_example(name):
    exec_path = examples_dir.joinpath(name, "example.py")
    os.system(f'python {exec_path}')

for example in examples_to_run:
    run_example(example)

cov.stop()
cov.save()
cov.html_report()
