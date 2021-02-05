import coverage
import unittest
loader = unittest.TestLoader()
cov = coverage.Coverage(source=[
    "emodpy_malaria.demographics.MalariaDemographics"
    , "emodpy_malaria.config"
    , "emodpy_malaria.interventions.bednet"
    , "emodpy_malaria.interventions.drug"
    , "emodpy_malaria.interventions.irs"
    , "emodpy_malaria.interventions.ivermectin"
    , "emodpy_malaria.interventions.outdoorrestkill"
    , "emodpy_malaria.interventions.spacespraying"
    , "emodpy_malaria.interventions.sugartrap"
    , "emodpy_malaria.interventions.udbednet"
])
cov.start()

# First, load and run the unittest tests
from test_import import MalariaTestImports
from test_malaria_interventions import TestMalariaInterventions
from test_malaria_interventions_as_files import MalariaInterventionFileTest
from test_malaria_reporters import TestMalariaReport
from test_malaria_config import TestMalariaConfig

test_classes_to_run = [MalariaTestImports,
                       TestMalariaInterventions,
                       MalariaInterventionFileTest,
                       TestMalariaReport,
                       TestMalariaConfig]

suites_list = []
for tc in test_classes_to_run:
    suite = loader.loadTestsFromTestCase(tc)
    suites_list.append(suite)
    pass

big_suite = unittest.TestSuite(suites_list)
runner = unittest.TextTestRunner()
results = runner.run(big_suite)

cov.stop()
cov.save()
cov.html_report()