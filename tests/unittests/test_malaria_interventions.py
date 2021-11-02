import unittest
import json
import os, sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import schema_path_file
import random

from emodpy_malaria.interventions.ivermectin import Ivermectin
from emodpy_malaria.interventions.bednet import Bednet
from emodpy_malaria.interventions.outdoorrestkill import add_OutdoorRestKill
from emodpy_malaria.interventions.udbednet import UDBednet
from emodpy_malaria.interventions import drug_campaign
from emodpy_malaria.interventions import diag_survey
from emodpy_malaria.interventions import common
from emodpy_malaria.interventions.mosquitorelease import MosquitoRelease
from emodpy_malaria.interventions.inputeir import InputEIR
from emodpy_malaria.interventions.outbreak import *
from emodpy_malaria.interventions.irs import add_irs_housing_modification

import emod_api.campaign as camp

drug_codes = ["ALP", "AL", "ASA", "DP", "DPP", "PPQ", "DHA_PQ", "DHA", "PMQ", "DA", "CQ", "SP", "SPP", "SPA"]


class WaningEffects:
    Box = "WaningEffectBox"
    Constant = "WaningEffectConstant"
    Exp = "WaningEffectExponential"
    BoxExp = "WaningEffectBoxExponential"


class WaningParams:
    Box_Duration = "Box_Duration"
    Decay_Time = "Decay_Time_Constant"
    Initial = "Initial_Effect"
    Class = "class"


class NodesetParams:
    Class = "class"
    SetAll = "NodeSetAll"
    SetList = "NodeSetNodeList"
    Node_List = "Node_List"


# Uncomment below to also run through tests with 10 Jan schema (default is latest)
# class schema_17Dec20:
#     schema_path = schema_path_file.schema_file_17Dec20

# Uncomment below to also run through tests with 10 Jan schema (default is latest)
# class schema_10Jan21:
#     schema_path = schema_path_file.schema_file_10Jan21


class TestMalariaInterventions(unittest.TestCase):
    # region helper methods
    def setUp(self) -> None:
        self.is_debugging = False
        self.tmp_intervention = None
        self.nodeset = None
        self.start_day = None
        self.event_coordinator = None
        self.intervention_config = None
        self.killing_config = None
        self.blocking_config = None
        self.repelling_config = None
        self.usage_config = None
        self.schema_file = schema_path_file
        camp.schema_path = schema_path_file.schema_path
        return

    def write_debug_files(self):
        with open(f'DEBUG_{self._testMethodName}.json', 'w') as outfile:
            json.dump(self.tmp_intervention, outfile, indent=4, sort_keys=True)
        return

    def parse_intervention_parts(self):
        self.nodeset = self.tmp_intervention['Nodeset_Config']
        self.start_day = self.tmp_intervention['Start_Day']
        self.event_coordinator = self.tmp_intervention['Event_Coordinator_Config']
        self.intervention_config = self.event_coordinator['Intervention_Config']
        if "Intervention_List" in self.intervention_config:
            self.intervention_config = self.intervention_config["Intervention_List"][0]
        if "Killing_Config" in self.intervention_config:
            self.killing_config = self.intervention_config["Killing_Config"]
        if "Blocking_Config" in self.intervention_config:
            self.blocking_config = self.intervention_config["Blocking_Config"]
        if "Repelling_Config" in self.intervention_config:
            self.repelling_config = self.intervention_config["Repelling_Config"]
        if "Usage_Config" in self.intervention_config:
            self.usage_config = self.intervention_config["Usage_Config"]

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
                         , killing_exponential_rate=0.0):
        self.tmp_intervention = Ivermectin(
            schema_path_container=self.schema_file
            , start_day=start_day
            , demographic_coverage=target_coverage
            , target_num_individuals=target_num_individuals
            , killing_initial_effect=killing_effect
            , killing_box_duration=killing_duration_box
            , killing_exponential_decay_rate=killing_exponential_rate
        )
        self.parse_intervention_parts()
        self.killing_config = self.intervention_config['Killing_Config']
        return

    @unittest.skip("FIXED")
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
        self.assertEqual(self.killing_config[WaningParams.Initial], 1.0)
        self.assertIn(WaningParams.Decay_Time, self.killing_config)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 0)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        return

    def test_ivermectin_exponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_exponential_rate=0.1)
        self.assertEqual(self.killing_config[WaningParams.Initial], 1.0)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 10)
        self.assertIn('Box_Duration', self.killing_config)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.killing_config['class'], WaningEffects.BoxExp)
        pass

    def test_ivermectin_boxexponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_exponential_rate=0.25,
                              killing_duration_box=3,
                              killing_effect=0.8)
        self.assertEqual(self.killing_config[WaningParams.Initial], 0.8)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 4)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 3)
        self.assertEqual(self.killing_config['class'], WaningEffects.BoxExp)
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
        self.assertEqual(self.killing_config[WaningParams.Initial], 0.76)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 12)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 5)
        self.assertEqual(self.killing_config['class'], WaningEffects.BoxExp)
        pass

    def test_ivermectin_num_individuals(self):
        self.is_debugging = False
        self.ivermectin_build(target_num_individuals=354,
                              killing_duration_box=3)
        self.assertEqual(self.event_coordinator['Target_Num_Individuals'], 354)
        self.assertIn('Individual_Selection_Type', self.event_coordinator)
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'], 'TARGET_NUM_INDIVIDUALS')
        # self.assertNotIn('Demographic_Coverage', self.event_coordinator)
        # TODO: uncomment that assertion later
        pass

    # endregion

    # region drug_campaign

    def test_drug_campaign_MDA(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "MDA"
        coverage = 0.78
        # self.test_drug_campaign(campaign_type)
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
                                            drug_code=drug_code, repetitions=3, tsteps_btwn_repetitions=100,
                                            coverage=coverage)
        # camp.save("campaign_mda.json") # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Number_Repetitions'], 3)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Timesteps_Between_Repetitions'],
                         100)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Demographic_Coverage'], coverage)
        self.assertEqual(
            camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][0][
                'Intervention_Name'],
            "AntimalarialDrug")

    def test_drug_campaign_MSAT(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "MSAT"
        # self.test_drug_campaign(campaign_type)
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
                                            drug_code=drug_code, repetitions=3, tsteps_btwn_repetitions=100,
                                            coverage=coverage)

        # camp.save("campaign_msat.json") # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 2)
        for event in camp.campaign_dict['Events']:
            if event['Event_Coordinator_Config']['Intervention_Config']['Intervention_Name'] == "MalariaDiagnostic":
                self.assertEqual(event['Event_Coordinator_Config']['Number_Repetitions'], 3)
                self.assertEqual(event['Event_Coordinator_Config']['Timesteps_Between_Repetitions'], 100)
                self.assertEqual(event['Event_Coordinator_Config']['Demographic_Coverage'], coverage)
            elif event['Event_Coordinator_Config']['Intervention_Config'][
                'Intervention_Name'] == "NodeLevelHealthTriggeredIV":
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_Name'], "AntimalarialDrug")
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    def test_drug_campaign_fMDA(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "fMDA"
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
                                            drug_code=drug_code,
                                            coverage=coverage)

        # camp.save("campaign_fmda.json")  # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 3)
        for event in camp.campaign_dict['Events']:
            if event['Event_Coordinator_Config']['Intervention_Config']['Intervention_Name'] == "MalariaDiagnostic":
                self.assertEqual(len(event['Event_Coordinator_Config']['Intervention_Config']['Intervention_List']), 2)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "BroadcastEventToOtherNodes":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 2)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "AntimalarialDrug":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 3)
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    def test_drug_campaign_rfMDA(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "rfMDA"
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
                                            drug_code=drug_code, fmda_radius=6,
                                            coverage=coverage)

        camp.save("campaign_rfmda.json")  # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 2)
        for event in camp.campaign_dict['Events']:
            if 'Actual_IndividualIntervention_Configs' in event['Event_Coordinator_Config']['Intervention_Config'][
                'Actual_IndividualIntervention_Config']:
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Actual_IndividualIntervention_Configs'][0]['class'], "BroadcastEventToOtherNodes")
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Actual_IndividualIntervention_Configs'][0]['Max_Distance_To_Other_Nodes_Km'], 6)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "AntimalarialDrug":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 3)
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    def test_drug_campaign_rfMSAT(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "rfMSAT"
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
                                            drug_code=drug_code, fmda_radius=6,
                                            coverage=coverage)

        camp.save("campaign_rfmsat.json")  # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 3)
        for event in camp.campaign_dict['Events']:
            if 'Actual_IndividualIntervention_Configs' in event['Event_Coordinator_Config']['Intervention_Config'][
                'Actual_IndividualIntervention_Config']:
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Actual_IndividualIntervention_Configs'][0]['class'], "BroadcastEventToOtherNodes")
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Actual_IndividualIntervention_Configs'][0]['Max_Distance_To_Other_Nodes_Km'], 6)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "AntimalarialDrug":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 3)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "MalariaDiagnostic":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 2)
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    # end region

    # region bednet
    def bednet_build(self
                     , start_day=1
                     , coverage=1.0
                     , blocking_eff=1.0
                     , killing_eff=1.0
                     , repelling_eff=1.0
                     , usage_eff=1.0
                     , blocking_decay_rate=0.0
                     , blocking_predecay_duration=365
                     , killing_decay_rate=0.0
                     , killing_predecay_duration=365
                     , repelling_decay_rate=0.0
                     , repelling_predecay_duration=365
                     , usage_decay_rate=0.0
                     , usage_predecay_duration=365
                     , node_ids=None
                     , insecticide=None
                     ):
        if not self.tmp_intervention:
            self.tmp_intervention = Bednet(
                campaign=self.schema_file
                , start_day=start_day
                , coverage=coverage
                , blocking_eff=blocking_eff
                , killing_eff=killing_eff
                , repelling_eff=repelling_eff
                , usage_eff=usage_eff
                , blocking_decay_rate=blocking_decay_rate
                , blocking_predecay_duration=blocking_predecay_duration
                , killing_decay_rate=killing_decay_rate
                , killing_predecay_duration=killing_predecay_duration
                , repelling_decay_rate=repelling_decay_rate
                , repelling_predecay_duration=repelling_predecay_duration
                , usage_decay_rate=usage_decay_rate
                , usage_predecay_duration=usage_predecay_duration
                , node_ids=node_ids
                , insecticide=insecticide
            )
        self.parse_intervention_parts()
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.usage_config = self.intervention_config['Usage_Config']
        self.all_configs = [
            self.killing_config
            , self.blocking_config
            , self.repelling_config
            , self.usage_config
        ]
        return

    # def test_bednet_default_throws_exception(self):
    #     with self.assertRaises(TypeError) as context:
    #         Bednet(campaign=schema_path_file)
    #     self.assertIn("start_day", str(context.exception))
    #     return

    def test_bednet_needs_only_start_day(self):
        self.is_debugging = False
        specific_day = 39

        # call emodpy-malaria code directly
        self.tmp_intervention = Bednet(campaign=schema_path_file,
                                       start_day=specific_day)

        self.bednet_build()  # tmp_intervention already set
        # self.bednet_build(start_day=specific_day)

        self.assertEqual(self.event_coordinator['Demographic_Coverage'], 1.0)
        self.assertEqual(self.start_day, specific_day)
        for wc in self.all_configs:
            self.assertEqual(wc[WaningParams.Initial], 1)
            self.assertEqual(wc[WaningParams.Box_Duration], 365)
            self.assertEqual(wc[WaningParams.Decay_Time], 0)
            self.assertEqual(wc[WaningParams.Class], WaningEffects.BoxExp)

        self.assertEqual(self.event_coordinator['Individual_Selection_Type']
                         , "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        return

    def test_bednet_all_constant_waning(self):

        self.bednet_build(start_day=13
                          , blocking_predecay_duration=-1
                          , killing_predecay_duration=-1
                          , repelling_predecay_duration=-1
                          , usage_predecay_duration=-1)
        for wc in self.all_configs:
            self.assertEqual(
                wc[WaningParams.Class]
                , WaningEffects.Constant)  # class is WaningEffectConstant
        return

    def test_bednet_all_waning_effectiveness(self):
        self.is_debugging = False
        block_effect = 0.9
        kill_effect = 0.8
        repell_effect = 0.7
        usage_effect = 0.6

        self.bednet_build(blocking_eff=block_effect
                          , killing_eff=kill_effect
                          , repelling_eff=repell_effect
                          , usage_eff=usage_effect)

        self.assertEqual(self.killing_config[WaningParams.Initial], kill_effect)
        self.assertEqual(self.blocking_config[WaningParams.Initial], block_effect)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repell_effect)
        self.assertEqual(self.usage_config[WaningParams.Initial], usage_effect)
        return

    def test_bednet_all_exponential_waning(self):
        self.bednet_build(blocking_decay_rate=0.2
                          , blocking_predecay_duration=0
                          , killing_decay_rate=0.1
                          , killing_predecay_duration=0
                          , usage_decay_rate=0.01
                          , usage_predecay_duration=0
                          , repelling_decay_rate=0.5
                          , repelling_predecay_duration=0)

        # All of these should have no box duration
        # All of these should be box exponential
        for wc in self.all_configs:
            self.assertEqual(wc[WaningParams.Box_Duration], 0)
            self.assertEqual(wc[WaningParams.Class], WaningEffects.BoxExp)

        # Each of the Delay_Time_Constants is the reciprocal of the decay rate
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], 5.0)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 10.0)
        self.assertEqual(self.usage_config[WaningParams.Decay_Time], 100.0)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], 2.0)
        return

    def test_bednet_nodeset_custom(self):
        specific_ids = [1, 12, 123, 1234]
        self.bednet_build(node_ids=specific_ids
                          , blocking_eff=0.3
                          , killing_predecay_duration=730
                          , repelling_predecay_duration=0
                          , repelling_decay_rate=0.02
                          , usage_decay_rate=0.01
                          , usage_predecay_duration=50
                          )

        self.assertEqual(self.nodeset[NodesetParams.Class],
                         NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List],
                         specific_ids)
        self.assertEqual(self.blocking_config[WaningParams.Initial], 0.3)

        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 730)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 0)

        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], 50)

        self.assertEqual(self.usage_config[WaningParams.Decay_Time], 100)
        self.assertEqual(self.usage_config[WaningParams.Box_Duration], 50)
        return

    def test_bednet_coverage_custom(self):
        specific_coverage = 0.365
        self.bednet_build(coverage=specific_coverage

                          , killing_eff=0.3

                          , repelling_predecay_duration=730

                          , usage_predecay_duration=0
                          , usage_decay_rate=0.02

                          , blocking_decay_rate=0.01
                          , blocking_predecay_duration=50
                          )

        self.assertEqual(self.nodeset[NodesetParams.Class],
                         NodesetParams.SetAll)
        self.assertEqual(self.event_coordinator['Demographic_Coverage'],
                         specific_coverage)
        self.assertEqual(self.killing_config[WaningParams.Initial], 0.3)

        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], 730)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], 0)

        self.assertEqual(self.usage_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.usage_config[WaningParams.Decay_Time], 50)

        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], 100)
        self.assertEqual(self.blocking_config[WaningParams.Box_Duration], 50)
        return

    # endregion

    # region OutdoorRestKill
    def test_outdoorrestkill_default(self):
        # correct setting for WaningParams are tested elsewhere here
        camp.campaign_dict["Events"] = []  # resetting
        add_OutdoorRestKill(camp)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator["Demographic_Coverage"], 1)
        self.assertEqual(self.start_day, 1)
        self.assertEqual(self.intervention_config["class"], "OutdoorRestKill")
        self.assertEqual(self.killing_config["class"], WaningEffects.BoxExp)
        return

    def test_outdoorrestkill_all_custom(self):
        camp.campaign_dict["Events"] = []  # resetting
        specific_start_day = 123
        specific_insecticide_name = "Vinegar"
        specific_killing_effect = 0.15
        specific_box_duration = 100
        specific_decay_rate = 0.05
        specific_nodes = [1, 2, 3, 5, 8, 13, 21, 34]
        add_OutdoorRestKill(camp,
                            start_day=specific_start_day,
                            insecticide_name=specific_insecticide_name,
                            killing_initial_effect=specific_killing_effect,
                            killing_box_duration=specific_box_duration,
                            killing_exponential_decay_rate=specific_decay_rate,
                            node_ids=specific_nodes)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config['Insecticide_Name'], specific_insecticide_name)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 1 / specific_decay_rate)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], specific_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], specific_killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], specific_nodes)
        return

    # endregion

    # region UsageDependentBednet
    def usagebednet_build(self
                          , start_day=1
                          , coverage=1.0
                          , discard_config=None
                          , property_restrictions=None
                          , blocking_eff=1.0
                          , blocking_decay_rate=0.0
                          , blocking_predecay_duration=365
                          , killing_eff=0.6
                          , killing_decay_rate=0.0
                          , killing_predecay_duration=0
                          , repelling_eff=1.0
                          , repelling_decay_rate=0.0
                          , repelling_predecay_duration=365
                          , intervention_name=None
                          , age_dependence: dict = None
                          , seasonal_dependence: dict = None
                          , insecticide: str = None
                          , node_ids: list = None
                          , triggered_campaign_delay: dict = None
                          , triggers: list = None
                          , duration: int = -1
                          , check_eligibility_at_trigger: bool = False
                          ):
        if not self.tmp_intervention:
            if intervention_name is None:
                self._testMethodName
            self.tmp_intervention = UDBednet(
                camp=camp
                , iv_name=intervention_name
                , start_day=start_day
                , coverage=coverage
                , discard_config=discard_config
                , ind_property_restrictions=property_restrictions
                , blocking_eff=blocking_eff
                , blocking_decay_rate=blocking_decay_rate
                , blocking_constant_duration=blocking_predecay_duration
                , killing_eff=killing_eff
                , killing_decay_rate=killing_decay_rate
                , killing_constant_duration=killing_predecay_duration
                , repelling_eff=repelling_eff
                , repelling_decay_rate=repelling_decay_rate
                , repelling_constant_duration=repelling_predecay_duration
                , age_dependence=age_dependence
                , seasonal_dependence=seasonal_dependence
                , insecticide=insecticide
                , node_ids=node_ids
                , triggered_campaign_delay=triggered_campaign_delay
                , triggers=triggers
                , duration=duration
                , check_eligibility_at_trigger=check_eligibility_at_trigger
            )
        self.parse_intervention_parts()
        if triggers:
            self.delay_intervention = self.intervention_config['Actual_IndividualIntervention_Config']
            self.delay_intervention_distro = self.delay_intervention['Delay_Period_Distribution']
            self.intervention_config = \
                self.delay_intervention['Actual_IndividualIntervention_Configs'][0]
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.usage_config = self.intervention_config['Usage_Config_List']
        self.all_configs = [
            self.killing_config
            , self.blocking_config
            , self.repelling_config
            , self.usage_config
        ]
        return

    def test_usagebednet_only_needs_start_day(self):
        specific_start_day = 131415
        self.tmp_intervention = UDBednet(camp=camp,
                                         start_day=specific_start_day)
        self.usagebednet_build()
        self.assertEqual(self.start_day, specific_start_day)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'],
                         "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(self.event_coordinator['Demographic_Coverage'],
                         1.0)
        self.assertEqual(self.intervention_config['Discard_Event'],
                         'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Expiration_Period_Distribution'],
                         'EXPONENTIAL_DISTRIBUTION')

        # checking that this is finalized appropriately
        camp.add(self.tmp_intervention)
        camp.save("test_campaign.json")
        with open('test_campaign.json') as file:
            campaign = json.load(file)
        self.assertTrue('schema' not in campaign, msg="UDBednet contains bits of schema in it")
        os.remove("test_campaign.json")

        return

    def test_usagebednet_trigger_distribution(self):
        self.is_debugging = False
        specific_triggers = ["ColdOutside", "HeavyMosquitoPresence"]
        self.usagebednet_build(triggers=specific_triggers)
        nlhtiv_config = self.event_coordinator['Intervention_Config']

        for trigger_condition in specific_triggers:
            self.assertIn(trigger_condition, nlhtiv_config['Trigger_Condition_List'])
        return

    def test_usagebednet_trigger_delay_constant(self):
        specific_triggers = ["WetOutside", "ReceivesBednet"]
        specific_delay_param = 'Delay_Period_Constant'
        specific_delay_value = 9
        specific_delay_dict = {specific_delay_param: specific_delay_value}
        specific_distribution = "CONSTANT_DISTRIBUTION"
        self.usagebednet_build(triggers=specific_triggers,
                               triggered_campaign_delay=specific_delay_dict)
        nlhtiv_config = self.event_coordinator['Intervention_Config']
        for trigger_condition in specific_triggers:
            self.assertIn(trigger_condition, nlhtiv_config['Trigger_Condition_List'])

        self.assertEqual(self.delay_intervention_distro, specific_distribution)
        self.assertEqual(self.delay_intervention[specific_delay_param],
                         specific_delay_value)
        return

    def test_usagebednet_seasonal_dependence_timesvalues(self):
        self.is_debugging = False
        specific_times = [0, 90, 180, 270]
        specific_values = [10, 50, 15, 75]
        specific_seasonality = {
            'Times': specific_times,
            'Values': specific_values
        }
        self.usagebednet_build(seasonal_dependence=specific_seasonality)
        usage_configs = self.intervention_config['Usage_Config_List']
        found_seasonal = False
        for durability in usage_configs:
            if durability['class'] == 'WaningEffectMapLinearSeasonal':
                found_seasonal = True
                map = durability['Durability_Map']
                self.assertEqual(map['Times'], specific_times)
                self.assertEqual(map['Values'], specific_values)
        self.assertTrue(found_seasonal)
        pass

    def test_usagebednet_seasonal_dependence_minmax_coverage(self):
        self.is_debugging = False
        specific_min_val = 0.1
        specific_max_day = 73  # March 14 in non leap years
        specific_seasonality = {
            'min_cov': specific_min_val,
            'max_day': specific_max_day
        }
        self.usagebednet_build(seasonal_dependence=specific_seasonality)
        usage_configs = self.intervention_config['Usage_Config_List']
        found_seasonal = False
        for durability in usage_configs:
            if durability['class'] == 'WaningEffectMapLinearSeasonal':
                found_seasonal = True
                map = durability['Durability_Map']
                actual_min = min(map['Values'])
                actual_min_diff = abs(actual_min - specific_min_val)
                self.assertLessEqual(actual_min_diff, 0.02)

                target_index = -1
                next_index = target_index + 1  # Find out the index that contains the max_day
                while map['Times'][next_index] < specific_max_day:  # So until the next index is too high...
                    target_index += 1
                    next_index += 1
                actual_max_index = map['Values'].index(max(map['Values']))  # Get the index of the actually highest day
                self.assertEqual(target_index, actual_max_index,
                                 msg=f"Expected value in bucket {target_index}"
                                     f": {map['Values'][target_index]} to be max, "
                                     f"but index {actual_max_index}: {map['Values'][actual_max_index]} "
                                     f"was higher.")

        self.assertTrue(found_seasonal)
        pass

    @unittest.skip("NYI")
    def test_usagebednet_seasonal_dependence_minzero_coverage(self):
        specific_seasonality = {
            'min_cov': 0.0,
            'max_day': 185  # July 4 in non leap years
        }
        self.usagebednet_build(seasonal_dependence=specific_seasonality)
        pass

    @unittest.skip("NYI")
    def test_usagebednet_age_dependence_one(self):
        pass

    @unittest.skip("NYI")
    def test_usagebednet_age_dependence_two(self):
        pass

    @unittest.skip("NYI")
    def test_usagebednet_age_dependence_three(self):
        pass

    # endregion

    def test_diagnostic_survey(self):
        camp.campaign_dict["Events"] = []
        self.is_debugging = False
        diag_survey.add_diagnostic_survey(camp)
        camp.save()
        with open("campaign.json") as file:
            campaign = json.load(file)
        event = campaign['Events'][0]
        coord_config = event['Event_Coordinator_Config']
        coverage = coord_config['Demographic_Coverage']
        intervention_config = coord_config['Intervention_Config']['Intervention_List'][0]
        name = intervention_config['Intervention_Name']
        self.assertEqual(name, "MalariaDiagnostic")
        self.assertEqual(coverage, 1)

    def test_common(self):
        self.is_debugging = False
        malaria_diagnostic = common.MalariaDiagnostic(camp, 1, 1, "BLOOD_SMEAR_PARASITES")
        measures = [malaria_diagnostic.Measurement_Sensitivity, malaria_diagnostic.Detection_Threshold]

        self.assertFalse(any(item != 1 for item in measures), msg="Not all values are 1 when set to 1")
        self.assertEqual("BLOOD_SMEAR_PARASITES", malaria_diagnostic.Diagnostic_Type)

        AntimalarialDrug = common.AntimalarialDrug(camp, "Malaria")
        self.assertEqual(AntimalarialDrug.Drug_Type, "Malaria")
        self.assertEqual(AntimalarialDrug.Cost_To_Consumer, 1.0)

    def mosquitorelease_build(self
                              , start_day=1
                              , number=10_000
                              , fraction=None
                              , infectious=0.0
                              , species='arabiensis'
                              , genome=None
                              , node_ids=None):
        camp.schema_path = os.path.join(file_dir, "./old_schemas/latest_schema.json")
        if not genome:
            genome = [['X', 'X']]
        if not self.tmp_intervention:
            self.tmp_intervention = MosquitoRelease(
                campaign=self.schema_file
                , start_day=start_day
                , released_fraction=fraction
                , released_number=number
                , released_infectious=infectious
                , released_species=species
                , released_genome=genome
                , node_ids=node_ids
            )
        self.parse_intervention_parts()
        return

    # def test_mosquitorelease_only_needs_startday(self):
    #     specific_start_day = 125
    #     self.tmp_intervention = MosquitoRelease(
    #         campaign=schema_path_file
    #         , released_number=100
    #         , start_day=specific_start_day)
    #     self.mosquitorelease_build() # parse intervention parts
    #
    #     self.assertIsNotNone(self.tmp_intervention)
    #     self.assertEqual(self.start_day, specific_start_day)
    #     self.assertEqual(self.intervention_config['class'], 'MosquitoRelease')
    #     return

    def test_mosquitorelease_default(self):
        self.mosquitorelease_build()

        self.assertEqual(self.start_day, 1)
        self.assertEqual(self.nodeset[NodesetParams.Class]
                         , NodesetParams.SetAll)  # default is nodesetall
        self.assertEqual(self.intervention_config['Released_Type'],
                         'FIXED_NUMBER')
        self.assertEqual(self.intervention_config['Released_Number'],
                         10_000)
        self.assertEqual(self.intervention_config['Released_Infectious'],
                         0)
        self.assertEqual(self.intervention_config['Released_Species'],
                         'arabiensis')
        self.assertEqual(self.intervention_config['Released_Genome'],
                         [['X', 'X']])
        return

    def test_mosquitorelease_custom(self):
        specific_start_day = 13
        specific_genome = [['X', 'Y']]
        specific_fraction = 0.14
        specific_infectious_fraction = 0.28
        specific_species = 'SillySkeeter'
        specific_nodes = [3, 5, 8, 13, 21]
        self.mosquitorelease_build(
            start_day=specific_start_day
            , number=None
            , fraction=specific_fraction
            , infectious=specific_infectious_fraction
        )

    def test_inputeir_default(self):
        eir = [random.randint(0, 50) for x in range(12)]
        self.tmp_intervention = InputEIR(camp, eir)
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Monthly_EIR, eir)
        self.assertEqual(self.intervention_config.Age_Dependence, "OFF")
        self.assertEqual(self.start_day, 1)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_inputeir(self):
        eir = [random.randint(0, 50) for x in range(12)]
        self.tmp_intervention = InputEIR(camp, monthly_eir=eir, start_day=2, node_ids=[2, 3], age_dependence='LINEAR')
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Monthly_EIR, eir)
        self.assertEqual(self.intervention_config.Age_Dependence, "LINEAR")
        self.assertEqual(self.start_day, 2)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], [2, 3])

        pass

    def test_daily_inputeir(self):
        daily_eir = [random.randint(0, 50) for x in range(365)]
        self.tmp_intervention = InputEIR(camp, daily_eir=daily_eir, start_day=2, node_ids=[2, 3],
                                         age_dependence='SURFACE_AREA_DEPENDENT')
        self.parse_intervention_parts()

        self.assertEqual(self.intervention_config.Daily_EIR, daily_eir)
        self.assertEqual(self.intervention_config.EIR_Type, "DAILY")
        self.assertEqual(self.intervention_config.Age_Dependence, "SURFACE_AREA_DEPENDENT")
        self.assertEqual(self.start_day, 2)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], [2, 3])

        pass

    def test_default_add_outbreak_individual(self):
        # resetting campaign
        camp.campaign_dict["Events"] = []
        add_outbreak_individual(camp)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Number_Repetitions'], 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Timesteps_Between_Repetitions'],
                         365)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Demographic_Coverage'], 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Individual_Selection_Type'],
                         "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Target_Gender'], "All")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Property_Restrictions'], [])
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['class'],
                         "OutbreakIndividual")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Antigen'],
                         0)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Genome'],
                         0)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Ignore_Immunity'], 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Incubation_Period_Override'], -1)

        pass

    def test_custom_add_outbreak_individual(self):
        camp.campaign_dict["Events"] = []
        add_outbreak_individual(camp, start_day=3, target_num_individuals=7, repetitions=5,
                                timesteps_between_repetitions=9, node_ids=[45, 89], target_gender="Female",
                                target_age_min=23, target_age_max=34,
                                antigen=2, genome=4, ignore_immunity=False, incubation_period_override=2,
                                ind_property_restrictions=[{"Risk": "High"}], broadcast_event="Testing!")
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], 3)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Number_Repetitions'], 5)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Timesteps_Between_Repetitions'],
                         9)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Target_Num_Individuals'], 7)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Individual_Selection_Type'],
                         "TARGET_NUM_INDIVIDUALS")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Target_Gender'], "Female")
        self.assertEqual(
            camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Property_Restrictions_Within_Node'],
            [{"Risk": "High"}])
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Target_Age_Min'], 23)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Target_Age_Max'], 34)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Target_Demographic'],
                         "ExplicitAgeRangesAndGender")
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['Node_List'], [45, 89])
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['class'],
                         "MultiInterventionDistributor")
        self.assertEqual(len(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List']),
                         2)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][0]['class'],
                         "OutbreakIndividual")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][0]['Antigen'],
                         2)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][0]['Genome'],
                         4)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][0]
                         ['Ignore_Immunity'], 0)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][0]
                         ['Incubation_Period_Override'], 2)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][0]
                         ['Incubation_Period_Override'], 2)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][1]
                         ['class'], "BroadcastEvent")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][1]
                         ['Broadcast_Event'], "Testing!")

        pass

    def test_1_custom_add_outbreak_malaria_genetics(self):
        camp.campaign_dict["Events"] = []
        allele_frequencies = [[1.00, 0.00, 0.00, 0.00], [0.00, 1.00, 0.00, 0.00], [0.00, 0.00, 1.00, 0.00],
                              [0.00, 0.00, 0.00, 1.00], [0.50, 0.50, 0.00, 0.00], [0.00, 0.50, 0.50, 0.00],
                              [0.00, 0.00, 0.50, 0.50], [0.25, 0.25, 0.25, 0.25], [0.10, 0.20, 0.30, 0.40],
                              [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00], [0.00, 1.00, 0.00, 0.00],
                              [0.00, 0.00, 1.00, 0.00], [0.00, 0.00, 0.00, 1.00], [0.50, 0.50, 0.00, 0.00],
                              [0.00, 0.50, 0.50, 0.00], [0.00, 0.00, 0.50, 0.50], [0.25, 0.25, 0.25, 0.25],
                              [0.10, 0.20, 0.30, 0.40], [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00],
                              [0.10, 0.20, 0.30, 0.40], [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00]
                              ]

        start_day = 4
        target_num_individuals = 25
        create_nucleotide_sequence_from = "ALLELE_FREQUENCIES"
        drug_resistant_allele_frequencies_per_genome_location = [[0.7, 0.3, 0, 0]]
        node_ids = [83, 235]

        add_outbreak_malaria_genetics(camp, start_day=start_day,
                                      target_num_individuals=target_num_individuals,
                                      create_nucleotide_sequence_from=create_nucleotide_sequence_from,
                                      barcode_allele_frequencies_per_genome_location=allele_frequencies,
                                      drug_resistant_allele_frequencies_per_genome_location=drug_resistant_allele_frequencies_per_genome_location,
                                      node_ids=node_ids)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], start_day)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Target_Num_Individuals'],
                         target_num_individuals)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Individual_Selection_Type'],
                         "TARGET_NUM_INDIVIDUALS")
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['Node_List'], node_ids)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['class'],
                         "OutbreakIndividualMalariaGenetics")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Barcode_Allele_Frequencies_Per_Genome_Location'], allele_frequencies)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Drug_Resistant_Allele_Frequencies_Per_Genome_Location'],
                         drug_resistant_allele_frequencies_per_genome_location)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Create_Nucleotide_Sequence_From'], create_nucleotide_sequence_from)

        pass

    def test_2_custom_add_outbreak_malaria_genetics(self):
        camp.campaign_dict["Events"] = []
        barcode_string = "AAAAAAAAAAAAAAAAAAAA"
        create_nucleotide_sequence_from = "BARCODE_STRING"
        drug_resistant_string = "CC"

        add_outbreak_malaria_genetics(camp,
                                      barcode_string=barcode_string,
                                      drug_resistant_string=drug_resistant_string)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Demographic_Coverage'],
                         1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Individual_Selection_Type'],
                         "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['class'],
                         "OutbreakIndividualMalariaGenetics")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Barcode_String'], barcode_string)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Drug_Resistant_String'], drug_resistant_string)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Create_Nucleotide_Sequence_From'], create_nucleotide_sequence_from)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Incubation_Period_Override'], -1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Ignore_Immunity'], 1)

        pass

    def test_3_custom_add_outbreak_malaria_genetics(self):
        camp.campaign_dict["Events"] = []
        barcode_string = "AAAAAAAAAAAAAAAAAAAA"
        start_day = 8
        demographic_coverage = 0.25
        create_nucleotide_sequence_from = "NUCLEOTIDE_SEQUENCE"
        drug_resistant_string = "CC"
        msp_variant_value = 460
        pfemp1_variants_values = [x for x in range(200, 250)]

        add_outbreak_malaria_genetics(camp, start_day=start_day,
                                      demographic_coverage=demographic_coverage,
                                      create_nucleotide_sequence_from=create_nucleotide_sequence_from,
                                      drug_resistant_string=drug_resistant_string,
                                      msp_variant_value=msp_variant_value,
                                      pfemp1_variants_values=pfemp1_variants_values)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], start_day)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Demographic_Coverage'],
                         demographic_coverage)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Individual_Selection_Type'],
                         "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['class'],
                         "OutbreakIndividualMalariaGenetics")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Drug_Resistant_String'], drug_resistant_string)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Create_Nucleotide_Sequence_From'], create_nucleotide_sequence_from)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['PfEMP1_Variants_Values'], pfemp1_variants_values)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['MSP_Variant_Value'], msp_variant_value)

        pass

    def test_1_custom_add_outbreak_malaria_var_genes(self):
        camp.campaign_dict["Events"] = []
        start_day = 8
        demographic_coverage = 0.25
        msp_type = 2
        irbc_type = [
            2, 75, 148, 221, 294, 367, 440, 513, 586, 659, 732, 805, 878, 951, 24, 97, 170,
            243, 316, 389, 462, 535, 608, 681, 754, 827, 900, 973, 46, 119, 192, 265, 338,
            411, 484, 557, 630, 703, 776, 849, 922, 995, 68, 141, 214, 287, 360, 433, 506, 579
        ]
        minor_epitope_type = [
            2, 0, 3, 3, 1, 2, 3, 3, 0, 1, 3, 2, 1, 3, 0, 1, 1, 2, 4, 0, 1, 1, 0, 4, 0, 1, 1, 4, 4, 0, 2, 0, 4, 1, 2, 1,
            1, 0, 1, 3, 3, 1, 2, 4, 2, 4, 4, 3, 2, 4
        ]

        add_outbreak_malaria_var_genes(camp, start_day=start_day,
                                       demographic_coverage=demographic_coverage,
                                       msp_type=msp_type, irbc_type=irbc_type, minor_epitope_type=minor_epitope_type)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], start_day)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Demographic_Coverage'],
                         demographic_coverage)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Individual_Selection_Type'],
                         "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['class'],
                         "OutbreakIndividualMalariaVarGenes")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['IRBC_Type'], irbc_type)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Minor_Epitope_Type'], minor_epitope_type)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['MSP_Type'], msp_type)

        pass

    def test_2_custom_add_outbreak_malaria_var_genes(self):
        camp.campaign_dict["Events"] = []
        start_day = 8
        target_num_individuals = 17
        node_ids = [90, 33]
        msp_type = 2
        irbc_type = [
            2, 75, 148, 221, 294, 367, 440, 513, 586, 659, 732, 805, 878, 951, 24, 97, 170,
            243, 316, 389, 462, 535, 608, 681, 754, 827, 900, 973, 46, 119, 192, 265, 338,
            411, 484, 557, 630, 703, 776, 849, 922, 995, 68, 141, 214, 287, 360, 433, 506, 579
        ]
        minor_epitope_type = [
            2, 0, 3, 3, 1, 2, 3, 3, 0, 1, 3, 2, 1, 3, 0, 1, 1, 2, 4, 0, 1, 1, 0, 4, 0, 1, 1, 4, 4, 0, 2, 0, 4, 1, 2, 1,
            1, 0, 1, 3, 3, 1, 2, 4, 2, 4, 4, 3, 2, 4
        ]

        add_outbreak_malaria_var_genes(camp, start_day=start_day,
                                       target_num_individuals=target_num_individuals,
                                       node_ids=node_ids,
                                       msp_type=msp_type, irbc_type=irbc_type, minor_epitope_type=minor_epitope_type)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], start_day)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Target_Num_Individuals'],
                         target_num_individuals)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Individual_Selection_Type'],
                         "TARGET_NUM_INDIVIDUALS")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['class'],
                         "OutbreakIndividualMalariaVarGenes")
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['IRBC_Type'], irbc_type)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['Minor_Epitope_Type'], minor_epitope_type)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
                         ['MSP_Type'], msp_type)
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['Node_List'], node_ids)

        pass

    # test IRSHousindModification
    def test_add_irs_housing_modification_custom(self):
        camp.campaign_dict["Events"] = []  # resetting
        specific_start_day = 123
        specific_insecticide_name = "Vinegar"
        specific_killing_effect = 0.15
        specific_repelling_effect = 0.93
        specific_killing_box_duration = 100
        specific_killing_exponential_decay_time = 35
        specific_repelling_box_duration = 5
        specific_repelling_exponential_decay_time = 41
        specific_nodes = [1, 2, 3, 5, 8, 13, 21, 34]
        specific_coverage = 0.78

        add_irs_housing_modification(camp,
                                     start_day=specific_start_day,
                                     coverage=specific_coverage,
                                     insecticide=specific_insecticide_name,
                                     killing_initial_effect=specific_killing_effect,
                                     repelling_initial_effect=specific_repelling_effect,
                                     killing_box_duration_days=specific_killing_box_duration,
                                     killing_exponential_decay_constant_days=specific_killing_exponential_decay_time,
                                     repelling_box_duration_days=specific_repelling_box_duration,
                                     repelling_exponential_decay_constant_days=specific_repelling_exponential_decay_time,
                                     node_ids=specific_nodes)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], specific_coverage)
        self.assertEqual(self.intervention_config['Insecticide_Name'], specific_insecticide_name)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], specific_killing_exponential_decay_time)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], specific_killing_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], specific_killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], specific_repelling_exponential_decay_time)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], specific_repelling_box_duration)
        self.assertEqual(self.repelling_config[WaningParams.Initial], specific_repelling_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], specific_nodes)
        return

    def test_add_irs_housing_modification_default(self):
        camp.campaign_dict["Events"] = []  # resetting
        add_irs_housing_modification(camp)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], 1)
        self.assertNotIn("Insecticide_Name", self.intervention_config)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 90)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.killing_config[WaningParams.Initial], 1)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], 90)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.repelling_config[WaningParams.Initial], 0)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)

        return


# Uncomment below if you would like to run test suite with different schema
# class TestMalariaInterventions_17Dec20(TestMalariaInterventions):

#     def setUp(self):
#         super(TestMalariaInterventions_17Dec20, self).setUp()
#         self.schema_file = schema_17Dec20

# class TestMalariaInterventions_10Jan21(TestMalariaInterventions):

#     def setUp(self):
#         super(TestMalariaInterventions_10Jan21, self).setUp()
#         self.schema_file = schema_10Jan21


if __name__ == '__main__':
    unittest.main()
