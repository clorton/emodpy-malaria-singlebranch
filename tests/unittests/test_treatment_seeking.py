#!/usr/bin/env python
import unittest
import sys
from pathlib import Path
import json
import shutil
from enum import Enum

import emod_api.campaign as camp
from emod_api.interventions.common import *
from emodpy_malaria.interventions.common import AntimalarialDrug
import emodpy_malaria.interventions.treatment_seeking as ts

parent = Path(__file__).resolve().parent
sys.path.append(parent)
import schema_path_file


class ResultType(Enum):
    EQUAL = 0
    NOT_EQUAL = 1
    NOT_PRESENT = 2


class TreatmentSeekingTest(unittest.TestCase):
    runInComps = False
    debug = False
    schema_path = schema_path_file.schema_path

    def __init__(self, *args, **kwargs):
        super(TreatmentSeekingTest, self).__init__(*args, **kwargs)

    # region unittest setup and teardown method
    @classmethod
    def setUpClass(cls):
        if cls.runInComps:
            # todo: setup comps connection
            pass
        camp.schema_path = cls.schema_path

    def setUp(self):
        print(f"running {self._testMethodName}:")
        pass

    def tearDown(self):
        print("end of test\n")
        pass
    # endregion

    # region class helper methods
    def is_subdict(self, small: dict, big: dict):
        """
        compare two dictionaries with nested structure, return if small is a sub dictionary of big
        Args:
            small:
            big:
        Returns:
        """
        if isinstance(small, dict) and isinstance(big, dict):
            for key in small:
                if key in big:
                    if (isinstance(small[key], dict) and isinstance(big[key], dict)) or \
                    (isinstance(small[key], list) and isinstance(big[key], list)):
                        if not self.is_subdict(small[key], big[key]):
                            return False
                    else:
                        if not small[key] == big[key]:
                            return False
                else:
                    return False
        elif isinstance(small, list) and isinstance(big, list):
            if len(small) != len(big):
                return False
            for i in range(len(small)):
                if not self.is_subdict(small[i], big[i]):
                    return False

        return True
        # this will not work for nested dictionaries
        # return dict(big, **small) == big

    def to_test_is_subdict(self):
        a = {"test": [{"a": 1}, {"b": 2}]}
        aa = {"test": [{"a": 1}, {"b": 2}], "test2": 3}
        self.assertTrue(self.is_subdict(a, aa))
        a = {"test": [[{"a": 1}], [{"b": 2}]]}
        aa = {"test": [[{"a": 1}], [{"b": 2}]], "test2": 3}
        self.assertTrue(self.is_subdict(a, aa))
        a = {"test": [[{"a": 1}], [{"b": 4}]]}
        aa = {"test": [[{"a": 1}], [{"b": 2}]], "test2": 3}
        self.assertFalse(self.is_subdict(a, aa))

    def is_valueequal(self, test_dict: dict, test_key: str, test_value):
        """
        return True if test_key is a key in test_dict and its value is equal to test_value
        Args:
            test_dict:
            test_key:
            test_value:
        Returns:
        """
        count = []
        if self.is_valueequal_internal(test_dict, test_key, test_value, count) == ResultType.EQUAL:
            return True
        else:
            return False

    def is_valueequal_internal(self, test_dict: dict, test_key: str, test_value, count: list = []):
        """
        Args:
            test_dict:
            test_key:
            test_value:
            count:
        Returns:
        """
        if test_key in test_dict:
            if test_value == test_dict[test_key]:
                count.append("Y")
                return ResultType.EQUAL
            else:
                return ResultType.NOT_EQUAL
        else:
            for key, value in test_dict.items():
                if isinstance(value, dict):
                    if self.is_valueequal_internal(value, test_key, test_value, count) == ResultType.NOT_EQUAL:
                        return ResultType.NOT_EQUAL

                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            if self.is_valueequal_internal(item, test_key, test_value, count) == ResultType.NOT_EQUAL:
                                return ResultType.NOT_EQUAL

        if not count:
            return ResultType.NOT_PRESENT
        else:
            return ResultType.EQUAL

    def to_test_is_valueequal(self):
        key = "test_key"
        value = "test_value"
        dict_1 = {"a lit": [{key: value}]}
        self.assertTrue(self.is_valueequal(dict_1, key, value))
        self.assertTrue(self.is_valueequal({key: value}, key, value))
        dict_2 = {"a lit": [{key: value}], "another list": [{'a': 1}, {key: value + "1"}]}
        self.assertFalse(self.is_valueequal(dict_2, key, value))

    def run_in_comps(self, campaign_buider, broadcast_event_name='Received_Treatment'):
        """
        Run simulation in Comps
        Args:
            campaign_buider: campaign builder
            broadcast_event_name:
        Returns:
        """
        print('NYI')
        pass

    @staticmethod
    def save_varaibles_to_json_files(variable_dict={}, path_to_save=Path('.')):
        if path_to_save.is_dir():
            shutil.rmtree(path_to_save)
        path_to_save.mkdir()
        for variable_name in variable_dict:
            file_p = path_to_save / f"{variable_name}.json"
            with file_p.open("w") as outfile:
                json.dump(variable_dict[variable_name], outfile, indent=4)

    @staticmethod
    def get_variable_name(locals, variable):
        variable_name = None
        for k, v in list(locals.items()):
            if v == variable:
                variable_name = k
        return variable_name

    def generate_variable_dict(self, locals, variables):
        variable_dict = {}
        for variable in variables:
            variable_name = self.get_variable_name(locals, variable)
            variable_dict[variable_name] = variable
        return variable_dict

    def save_json_files(self, locals, variables=[], path_to_save=""):
        """
        Save a list of variables as json files, named by the original variable name.
        Args:
            locals:
            variables:
            path_to_save:
        Returns:
        """
        variable_dict = self.generate_variable_dict(locals, variables)
        p = Path('health_seaking')
        if not p.is_dir():
            p.mkdir()
        path_to_save = p / path_to_save
        self.save_varaibles_to_json_files(variable_dict, path_to_save)
    # endregion

    # region unittests
    def test_non_default(self):
        """
        Asserts non default values with _get_events.
        """
        start_day = 10
        drug = ['drug_1', 'drug_2', 'drug_3', 'drug4']
        targets = [
            {'trigger': 'NewInfection', 'coverage': 0.7, 'seek': 0.9, 'rate': 0.9},
            {'trigger': 'Births', 'coverage': 0.3, 'seek': 0.2, 'rate': 1.6},
            {'trigger': 'NewClinicalCase', 'coverage': 0.3, 'agemin': 5, 'agemax': 55, 'seek': 0.2, 'rate': 0} # test rate == 0
        ]
        broadcast_event_name = 'Test_event'
        node_ids = [1, 2]
        ind_property_restrictions = [{"IndividualProperty1": "PropertyValue1"},
                                     {"IndividualProperty2": "PropertyValue2"}]
        drug_ineligibility_duration = 5
        duration = 15

        ret_events = ts._get_events(camp, start_day=start_day, drug=drug, targets=targets,
                                     node_ids=copy.deepcopy(node_ids),
                                     ind_property_restrictions=copy.deepcopy(ind_property_restrictions),
                                     drug_ineligibility_duration=drug_ineligibility_duration, duration=duration,
                                     broadcast_event_name=broadcast_event_name)
        first = True
        for ret_event in ret_events:
            camp.add(ret_event, first=first)
            if first:
                first = False
        campaign_file = Path(parent, "add_treatment_seeking_non_default_test.json")
        if campaign_file.is_file():
            campaign_file.unlink()

        camp.save(str(campaign_file))

        with campaign_file.open() as file:
            campaign = json.load(file)

        self.validate_campaign(broadcast_event_name, campaign, drug, targets, drug_ineligibility_duration, duration,
                               ind_property_restrictions, node_ids, start_day)

        if self.runInComps:
            self.run_in_comps(campaign_file)
        campaign_file.unlink()

    def test_default(self):
        """
        Asserts default values with _get_events.
        """
        ret_events = ts._get_events(camp)
        first = True
        for ret_event in ret_events:
            camp.add(ret_event, first=first)
            if first:
                first = False
        campaign_file = Path(parent, "add_treatment_seeking_default_test.json")
        if campaign_file.is_file():
            campaign_file.unlink()

        camp.save(str(campaign_file))

        with campaign_file.open() as file:
            campaign = json.load(file)

        drug = ['Artemether', 'Lumefantrine']
        targets = [
            {'trigger': 'NewClinicalCase', 'coverage': 0.1, 'agemin': 15, 'agemax': 70, 'seek': 0.4, 'rate': 0.3},
            {'trigger': 'NewSevereCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.5}]
        broadcast_event_name = 'ReceivedTreatment'

        self.validate_campaign(broadcast_event_name, campaign, drug, targets)

        if self.runInComps:
            self.run_in_comps(campaign_file)

        campaign_file.unlink()

    def test_add_health_seeking(self):
        """
        test for add_health_seeking
        Returns:

        """
        ts.add(camp)
        campaign_file = Path(parent, "add_treatment_seeking_test.json")
        if campaign_file.is_file():
            campaign_file.unlink()

        camp.save(str(campaign_file))

        with campaign_file.open() as file:
            campaign = json.load(file)

        drug = ['Artemether', 'Lumefantrine']
        targets = [
            {'trigger': 'NewClinicalCase', 'coverage': 0.1, 'agemin': 15, 'agemax': 70, 'seek': 0.4, 'rate': 0.3},
            {'trigger': 'NewSevereCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.5}]
        broadcast_event_name = 'ReceivedTreatment'

        campaign['Events'] = campaign['Events'][-len(targets):]  # get the last n events that get attacked to camp

        self.validate_campaign(broadcast_event_name, campaign, drug, targets)

        campaign_file.unlink()

    def validate_campaign(self, broadcast_event_name, campaign, drug, targets, drug_ineligibility_duration=0,
                          duration=-1, ind_property_restrictions=None, node_ids=None, start_day=1):
        events = campaign['Events']
        self.assertEqual(len(events), len(targets))

        intervention_list = [AntimalarialDrug(camp, Drug_Type=d) for d in drug]
        intervention_list.append(BroadcastEvent(camp, Event_Trigger=broadcast_event_name))
        for i in range(len(events)):
            event = events[i]
            # test start day
            self.assertEqual(start_day, event['Start_Day'])
            # test 3rd class == NodeLevelHealthTriggeredIV
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['class'],
                             'NodeLevelHealthTriggeredIV')
            # test 4th class == MultiInterventionDistributor
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['class'], 'MultiInterventionDistributor')

            # test rate
            if targets[i]['rate'] > 0:  # delayed intervention, code may be changed later
                delayed_intervention = event['Event_Coordinator_Config']['Intervention_Config'][
                    'Actual_IndividualIntervention_Config']['Intervention_List'][0]
                actual_config = delayed_intervention['Actual_IndividualIntervention_Configs']
                self.assertEqual(delayed_intervention['class'], 'DelayedIntervention')
                self.assertEqual(delayed_intervention['Delay_Period_Exponential'], 1/targets[i]['rate'])
            else:
                actual_config = event['Event_Coordinator_Config']['Intervention_Config'][
                    'Actual_IndividualIntervention_Config']['Intervention_List'][0][
                    'Intervention_List']
            # test actual intervention list
            self.assertEqual(len(actual_config), len(intervention_list))
            for actual_config_event, drug_event in zip(actual_config, intervention_list):
                self.assertTrue(self.is_subdict(small=actual_config_event, big=drug_event))

            # test drug:
            for j in range(len(drug)):
                self.assertTrue(self.is_valueequal(actual_config[j], "Drug_Type", drug[j]))

            # test broadcast_event_name
            self.assertTrue(self.is_valueequal(actual_config[-1], "Broadcast_Event", broadcast_event_name))

            # test trigger
            self.assertTrue(self.is_valueequal(event, "Trigger_Condition_List", [targets[i]['trigger']]))

            # test agemin and agemax
            if 'agemin' in targets[i]:
                self.assertTrue(self.is_valueequal(event, "Target_Age_Min", targets[i]['agemin']))
                self.assertTrue(self.is_valueequal(event, "Target_Age_Max", targets[i]['agemax']))
            else:
                self.assertTrue(self.is_valueequal(event, "Target_Age_Min", 0))
                self.assertTrue(self.is_valueequal(event, "Target_Age_Max", 125))

            # test coverage and seek
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['Demographic_Coverage'],
                             targets[i]['coverage'] * targets[i]['seek'])

            # test Nodeset_Config
            expected_nodeset_config = {
                "Node_List": node_ids,
                "class": "NodeSetNodeList"
            } if node_ids else {"class": "NodeSetAll"}
            self.assertEqual(expected_nodeset_config, event['Nodeset_Config'])

            # test ind_property_restrictions
            if not ind_property_restrictions:
                ind_property_restrictions = []
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']
                             ['Property_Restrictions_Within_Node'],  # Property_Restrictions_Within_Node
                             ind_property_restrictions)

            # test duration
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['Duration'],
                             duration)

            # todo: test drug_ineligibility_duration(not hooked up yet)
        if self.debug:
            self.save_json_files(locals(),
                                 [intervention_list, campaign],
                                 self._testMethodName)

    # endregion


if __name__ == '__main__':
    unittest.main()

