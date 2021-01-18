import unittest
import os
import json
import schema_path_file

from emodpy_malaria.interventions.bednet import new_intervention_as_file as bednet_file
from emodpy_malaria.interventions.drug import new_intervention_as_file as drug_file
from emodpy_malaria.interventions.irs import new_intervention_as_file as irs_file
from emodpy_malaria.interventions.spacespraying import new_intervention_as_file as spacespray_file
from emodpy_malaria.interventions.sugartrap import new_intervention_as_file as sugartrap_file
from emodpy_malaria.interventions.udbednet import new_intervention_as_file as rei_bednet
import emod_api.campaign as camp
camp.schema_path = schema_path_file.schema_file

class MalariaInterventionFileTest(unittest.TestCase):

    def setUp(self) -> None:
        self.is_debugging = False
        self.file_path = f"DEBUG_{self._testMethodName}.json"
        self.campaign = None
        self.event = None
        self.intervention_class = None
        self.specific_start_day = 39
        self.method_under_test = None
        self.expected_intervention_class = None
        if self.file_is_there():
            os.unlink(self.file_path)
        return

    def load_event(self):
        self.assertTrue(self.file_is_there())
        with open (self.file_path, 'r') as infile:
            self.campaign = json.load(infile)
        self.assertEqual(len(self.campaign['Events']), 1) # should only be one
        self.event = self.campaign['Events'][0]
        self.start_day = self.event['Start_Day']
        self.intervention_class = self.event['Event_Coordinator_Config']['Intervention_Config']['class']
        return

    def file_is_there(self):
        file_to_check = None
        if self.file_path:
            file_to_check = self.file_path
        else:
            file_to_check = f"{self.expected_intervention_class}.json"
        if os.path.isfile(file_to_check):
            return True
        else:
            return False

    def tearDown(self) -> None:
        if not self.is_debugging:
            os.unlink(self.file_path)
        return

    def run_test(self):
        self.assertFalse(self.file_is_there())

        if self.file_path:
            self.method_under_test(camp
                                   , start_day=self.specific_start_day
                                   , filename=self.file_path)
        else:
            self.method_under_test(camp
                                   , start_day=self.specific_start_day)
        if not self.file_path:
            self.file_path = f"{self.expected_intervention_class}.json"
        self.load_event()
        self.assertEqual(self.start_day, self.specific_start_day)
        self.assertEqual(self.intervention_class, self.expected_intervention_class)
        return

    def test_bednet_file(self):
        self.method_under_test = bednet_file
        self.expected_intervention_class = "SimpleBednet"
        self.run_test()
        return

    def test_bednet_file_nofilename(self):
        self.method_under_test = bednet_file
        self.expected_intervention_class = "SimpleBednet"
        self.file_path = None
        self.run_test()
        return

    def test_drug_file(self):
        self.method_under_test = drug_file
        self.expected_intervention_class="AntimalarialDrug"
        self.run_test()
        return

    def test_drug_file_nofilename(self):
        self.method_under_test = drug_file
        self.expected_intervention_class="AntimalarialDrug"
        self.file_path = None
        self.run_test()
        return

    def test_irs_file(self):
        self.method_under_test = irs_file
        self.expected_intervention_class = "IRSHousingModification"
        self.run_test()
        return

    def test_irs_file_nofilename(self):
        self.method_under_test = irs_file
        self.expected_intervention_class = "IRSHousingModification"
        self.file_path = None
        self.run_test()
        return

    def test_spacespray_file(self):
        self.method_under_test = spacespray_file
        self.expected_intervention_class = "SpaceSpraying"
        self.run_test()
        return

    def test_spacespray_file_nofilename(self):
        self.method_under_test = spacespray_file
        self.expected_intervention_class = "SpaceSpraying"
        self.file_path = None
        self.run_test()
        return

    def test_sugartrap_file(self):
        self.method_under_test = sugartrap_file
        self.expected_intervention_class = "SugarTrap"
        self.run_test()
        return

    def test_sugartrap_file_nofilename(self):
        self.method_under_test = sugartrap_file
        self.expected_intervention_class = "SugarTrap"
        self.file_path = None
        self.run_test()
        return

    def test_udbednet_file(self):
        self.is_debugging = False
        self.method_under_test = rei_bednet
        self.expected_intervention_class = "UsageDependentBednet"
        self.run_test()

    def test_udbednet_file_nofilename(self):
        self.is_debugging = False
        self.method_under_test = rei_bednet
        self.expected_intervention_class = "UsageDependentBednet"
        self.file_path = None
        self.run_test()


if __name__ == '__main__':
    unittest.main()
