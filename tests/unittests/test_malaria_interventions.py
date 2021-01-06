import unittest
import json
import os, sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import schema_path_file

from emodpy_malaria.interventions.ivermectin import Ivermectin

class TestMalariaInterventions(unittest.TestCase):

    # region helper methods
    def setUp(self) -> None:
        self.is_debugging = False
        self.tmp_intervention = None
        self.nodeset = None
        self.start_day = None
        self.event_coordinator = None
        self.intervention_config = None
        self.killing_config = None # Used in ivermectin
        return

    def write_debug_files(self):
        with open(f'DEBUG_{self.id()}.json', 'w') as outfile:
            json.dump(self.tmp_intervention, outfile, indent=4, sort_keys=True)
        return

    def parse_intervention_parts(self):
        self.nodeset = self.tmp_intervention['Nodeset_Config']
        self.start_day = self.tmp_intervention['Start_Day']
        self.event_coordinator = self.tmp_intervention['Event_Coordinator_Config']
        self.intervention_config = self.event_coordinator['Intervention_Config']

    def tearDown(self) -> None:
        if self.is_debugging:
            self.write_debug_files()
        return
    # endregion

    # region Ivermectin

    def ivermectin_build(self
                         , start_day=0
                         , target_coverage=1.0
                         , target_num_individuals=None
                         , killing_effect=1.0
                         , killing_duration_box=0
                         , killing_exponential_rate=0):
        self.tmp_intervention = Ivermectin(
            schema_path_container=schema_path_file
            , start_day=start_day
            , target_coverage=target_coverage
            , target_num_individuals=target_num_individuals
            , killing_effect=killing_effect
            , killing_duration_box=killing_duration_box
            , killing_exponential_decay_rate=killing_exponential_rate
        )
        self.parse_intervention_parts()
        self.killing_config = self.intervention_config['Killing_Config']
        return

    def test_ivermectin_default_throws_exception(self):
        with self.assertRaises(TypeError) as context:
            Ivermectin(schema_path_container=schema_path_file)
        self.assertIn("killing_effect", str(context.exception))
        return

    def test_ivermectin_box_default(self):
        self.is_debugging = False
        self.assertIsNone(self.tmp_intervention)
        self.ivermectin_build(killing_duration_box=3)
        self.assertIsNotNone(self.tmp_intervention)
        self.assertEqual(self.start_day, 0)
        self.assertEqual(self.event_coordinator['Demographic_Coverage'],
                         1.0)
        self.assertEqual(self.killing_config['Initial_Effect'], 1.0)
        self.assertIn('Decay_Time_Constant', self.killing_config)
        self.assertEqual(self.killing_config['Decay_Time_Constant'], 0)
        self.assertEqual(self.killing_config['class'], 'WaningEffectBoxExponential')
        return

    def test_ivermectin_exponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_exponential_rate=0.1)
        self.assertEqual(self.killing_config['Initial_Effect'], 1.0)
        self.assertEqual(self.killing_config['Decay_Time_Constant'], 10)
        self.assertIn('Box_Duration', self.killing_config)
        self.assertEqual(self.killing_config['Box_Duration'], 0)
        self.assertEqual(self.killing_config['class'], 'WaningEffectBoxExponential')
        pass

    def test_ivermectin_boxexponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_exponential_rate=0.25,
                              killing_duration_box=3,
                              killing_effect=0.8)
        self.assertEqual(self.killing_config['Initial_Effect'], 0.8)
        self.assertEqual(self.killing_config['Decay_Time_Constant'], 4)
        self.assertEqual(self.killing_config['Box_Duration'], 3)
        self.assertEqual(self.killing_config['class'], 'WaningEffectBoxExponential')
        pass

    def test_ivermectin_custom_everything(self):
        self.ivermectin_build(
            start_day=123,
            target_coverage=0.87,
            killing_effect=0.76,
            killing_duration_box=12,
            killing_exponential_rate=0.2
        )
        self.assertEqual(self.start_day, 123)
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], 0.87)
        self.assertEqual(self.killing_config['Initial_Effect'], 0.76)
        self.assertEqual(self.killing_config['Box_Duration'], 12)
        self.assertEqual(self.killing_config['Decay_Time_Constant'], 5)
        self.assertEqual(self.killing_config['class'], 'WaningEffectBoxExponential')
        pass

    def test_ivermectin_num_individuals(self):
        self.is_debugging = True
        self.ivermectin_build(target_num_individuals=354,
                              killing_duration_box=3)
        self.assertEqual(self.event_coordinator['Target_Num_Individuals'], 354)
        self.assertIn('Individual_Selection_Type', self.event_coordinator)
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'], 'TARGET_NUM_INDIVIDUALS')
        # self.assertNotIn('Demographic_Coverage', self.event_coordinator)
        # TODO: uncomment that assertion later
        pass

    # endregion



if __name__ == '__main__':
    unittest.main()
