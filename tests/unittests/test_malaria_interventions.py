import unittest
import json
import os, sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import schema_path_file

from emodpy_malaria.interventions.ivermectin import Ivermectin
from emodpy_malaria.interventions.bednet import Bednet
from emodpy_malaria.interventions.outdoorrestkill import OutdoorRestKill
from emodpy_malaria.interventions.udbednet import REIBednet


class WaningEffects:
    B = "WaningEffectBox"
    C = "WaningEffectConstant"
    X = "WaningEffectExponential"
    BEX = "WaningEffectBoxExponential"


class WaningParams:
    BD = "Box_Duration"
    DTC = "Decay_Time_Constant"
    IE = "Initial_Effect"
    C = "class"


class NodesetParams:
    C = "class"
    CNSA = "NodeSetAll"
    CNSNL ="NodeSetNodeList"
    NL = "Node_List"



class schema_17Dec20:
    schema_path = schema_path_file.schema_file_17Dec20


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
        self.schema_file = schema_path_file
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
                         , killing_exponential_rate=0.0):
        self.tmp_intervention = Ivermectin(
            schema_path_container=self.schema_file
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
        self.assertEqual(self.killing_config[WaningParams.IE], 1.0)
        self.assertIn(WaningParams.DTC, self.killing_config)
        self.assertEqual(self.killing_config[WaningParams.DTC], 0)
        self.assertEqual(self.killing_config[WaningParams.C], WaningEffects.BEX)
        return

    def test_ivermectin_exponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_exponential_rate=0.1)
        self.assertEqual(self.killing_config[WaningParams.IE], 1.0)
        self.assertEqual(self.killing_config[WaningParams.DTC], 10)
        self.assertIn('Box_Duration', self.killing_config)
        self.assertEqual(self.killing_config[WaningParams.BD], 0)
        self.assertEqual(self.killing_config['class'], WaningEffects.BEX)
        pass

    def test_ivermectin_boxexponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_exponential_rate=0.25,
                              killing_duration_box=3,
                              killing_effect=0.8)
        self.assertEqual(self.killing_config[WaningParams.IE], 0.8)
        self.assertEqual(self.killing_config[WaningParams.DTC], 4)
        self.assertEqual(self.killing_config[WaningParams.BD], 3)
        self.assertEqual(self.killing_config['class'], WaningEffects.BEX)
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
        self.assertEqual(self.killing_config[WaningParams.IE], 0.76)
        self.assertEqual(self.killing_config[WaningParams.BD], 12)
        self.assertEqual(self.killing_config[WaningParams.DTC], 5)
        self.assertEqual(self.killing_config['class'], WaningEffects.BEX)
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
                camp=self.schema_file
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

    def test_bednet_default_throws_exception(self):
        with self.assertRaises(TypeError) as context:
            Bednet(camp=schema_path_file)
        self.assertIn("start_day", str(context.exception))
        return

    def test_bednet_needs_only_start_day(self):
        self.is_debugging = False
        specific_day = 39

        # call emodpy-malaria code directly
        self.tmp_intervention = Bednet(camp=schema_path_file,
                                       start_day=specific_day)

        self.bednet_build() # tmp_intervention already set
        # self.bednet_build(start_day=specific_day)

        self.assertEqual(self.event_coordinator['Demographic_Coverage'], 1.0)
        self.assertEqual(self.start_day, specific_day)
        for wc in self.all_configs:
            self.assertEqual(wc[WaningParams.IE], 1)
            self.assertEqual(wc[WaningParams.BD], 365)
            self.assertEqual(wc[WaningParams.DTC], 0)
            self.assertEqual(wc[WaningParams.C], WaningEffects.BEX)

        self.assertEqual(self.event_coordinator['Individual_Selection_Type']
                         , "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(self.nodeset[NodesetParams.C],NodesetParams.CNSA)
        return

    def test_bednet_all_constant_waning(self):

        self.bednet_build(start_day=13
                          , blocking_predecay_duration=-1
                          , killing_predecay_duration=-1
                          , repelling_predecay_duration=-1
                          , usage_predecay_duration=-1)
        for wc in self.all_configs:
            self.assertEqual(
                wc[WaningParams.C]
                , WaningEffects.C) # class is WaningEffectConstant
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

        self.assertEqual(self.killing_config[WaningParams.IE], kill_effect)
        self.assertEqual(self.blocking_config[WaningParams.IE], block_effect)
        self.assertEqual(self.repelling_config[WaningParams.IE], repell_effect)
        self.assertEqual(self.usage_config[WaningParams.IE], usage_effect)
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
            self.assertEqual(wc[WaningParams.BD], 0)
            self.assertEqual(wc[WaningParams.C], WaningEffects.BEX)

        # Each of the Delay_Time_Constants is the reciprocal of the decay rate
        self.assertEqual(self.blocking_config[WaningParams.DTC], 5.0)
        self.assertEqual(self.killing_config[WaningParams.DTC], 10.0)
        self.assertEqual(self.usage_config[WaningParams.DTC], 100.0)
        self.assertEqual(self.repelling_config[WaningParams.DTC], 2.0)
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

        self.assertEqual(self.nodeset[NodesetParams.C],
                         NodesetParams.CNSNL)
        self.assertEqual(self.nodeset[NodesetParams.NL],
                         specific_ids)
        self.assertEqual(self.blocking_config[WaningParams.IE], 0.3)

        self.assertEqual(self.killing_config[WaningParams.BD], 730)
        self.assertEqual(self.killing_config[WaningParams.DTC], 0)

        self.assertEqual(self.repelling_config[WaningParams.BD], 0)
        self.assertEqual(self.repelling_config[WaningParams.DTC], 50)

        self.assertEqual(self.usage_config[WaningParams.DTC], 100)
        self.assertEqual(self.usage_config[WaningParams.BD], 50)
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

        self.assertEqual(self.nodeset[NodesetParams.C],
                         NodesetParams.CNSA)
        self.assertEqual(self.event_coordinator['Demographic_Coverage'],
                         specific_coverage)
        self.assertEqual(self.killing_config[WaningParams.IE], 0.3)

        self.assertEqual(self.repelling_config[WaningParams.BD], 730)
        self.assertEqual(self.repelling_config[WaningParams.DTC], 0)

        self.assertEqual(self.usage_config[WaningParams.BD], 0)
        self.assertEqual(self.usage_config[WaningParams.DTC], 50)

        self.assertEqual(self.blocking_config[WaningParams.DTC], 100)
        self.assertEqual(self.blocking_config[WaningParams.BD], 50)
        return

    # endregion

    # region OutdoorRestKill
    def outdoorrestkill_build(self
                              , killing_effect=0.02
                              , start_day=1
                              , coverage=1.0
                              , insecticide_name=None
                              , killing_predecay_duration=0
                              , killing_decay_rate=0.0
                              , node_ids=None):
        if not self.tmp_intervention:
            self.tmp_intervention = OutdoorRestKill(
                schema_path_container=self.schema_file
                , killing_effect=killing_effect
                , insecticide_name=insecticide_name
                , start_day=start_day
                , target_coverage=coverage
                , killing_predecay_duration=killing_predecay_duration
                , killing_decay_rate=killing_decay_rate
                , node_ids=node_ids
            )
        self.parse_intervention_parts()
        self.killing_config = self.intervention_config['Killing_Config']
        return

    def test_outdoorrestkill_default_throws_exception(self):
        with self.assertRaises(TypeError) as context:
            OutdoorRestKill(schema_path_container=self.schema_file)
        self.assertIn("killing_effect", str(context.exception))
        return


    def test_outdoorrestkill_only_needs_killing_effect(self):
        specific_effect=0.311
        self.tmp_intervention = OutdoorRestKill(
            schema_path_container=self.schema_file
        , killing_effect=specific_effect
        )

        self.outdoorrestkill_build() # tmp_intervention already built
        self.assertEqual(self.killing_config[WaningParams.IE], specific_effect)
        self.assertEqual(self.nodeset[NodesetParams.C], NodesetParams.CNSA)
        return

    def test_outdoorrestkill_all_custom(self):
        specific_start_day = 123
        specific_insecticide_name = "Vinegar"
        specific_coverage = 0.63
        specific_killing_effect = 0.15
        specific_box_duration = 100
        specific_decay_rate = 0.05
        specific_nodes = [1, 2, 3, 5, 8, 13, 21, 34]

        self.outdoorrestkill_build(
            killing_effect=specific_killing_effect
            , start_day=specific_start_day
            , insecticide_name = specific_insecticide_name 
            , coverage=specific_coverage
            , killing_predecay_duration=specific_box_duration
            , killing_decay_rate=specific_decay_rate
            , node_ids=specific_nodes
        )

        self.assertEqual(self.start_day, specific_start_day)
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], specific_coverage)
        self.assertEqual(self.intervention_config['Insecticide_Name'], specific_insecticide_name)
        self.assertEqual(self.killing_config[WaningParams.DTC], 1/specific_decay_rate)
        self.assertEqual(self.killing_config[WaningParams.BD], specific_box_duration)
        self.assertEqual(self.killing_config[WaningParams.IE], specific_killing_effect)
        self.assertEqual(self.killing_config[WaningParams.C], WaningEffects.BEX)
        self.assertEqual(self.nodeset[NodesetParams.C], NodesetParams.CNSNL)
        self.assertEqual(self.nodeset[NodesetParams.NL], specific_nodes)
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
                          , age_dependence:dict=None
                          , seasonal_dependence:dict=None
                          , insecticide:str=None
                          , cost:int=5
                          , node_ids:list=None
                          , triggered_campaign_delay:int=0
                          , triggers:list=None
                          , duration:int=-1
                          , check_eligibility_at_trigger:bool=False
                          ):
        if not self.tmp_intervention:
            if intervention_name is None:
                self._testMethodName
            self.tmp_intervention = REIBednet(
                camp=self.schema_file
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
                , cost=cost
                , node_ids=node_ids
                , triggered_campaign_delay=triggered_campaign_delay
                , triggers=triggers
                , duration=duration
                , check_eligibility_at_trigger=check_eligibility_at_trigger
            )
        self.parse_intervention_parts()
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
        specific_start_day=131415
        self.tmp_intervention = REIBednet(camp=self.schema_file,
                                          start_day=specific_start_day)
        self.usagebednet_build()
        self.assertEqual(self.start_day, specific_start_day)
        self.assertEqual(self.nodeset[NodesetParams.C], NodesetParams.CNSA)
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'],
                         "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(self.event_coordinator['Demographic_Coverage'],
                         1.0)
        self.assertEqual(self.intervention_config['Discard_Event'],
                         'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Expiration_Period_Distribution'],
                         'EXPONENTIAL_DISTRIBUTION')
        return

    def test_usagebednet_trigger_distribution(self):
        self.is_debugging = True
        specific_triggers = ["ColdOutside","HeavyMosquitoPresence"]
        self.usagebednet_build(triggers=specific_triggers)

        for trigger_condition in specific_triggers:
            self.assertIn(trigger_condition, self.intervention_config['Trigger_Conditions'])
        return

    @unittest.skip("Trigger Delay is NYI yet")
    def test_usagebednet_trigger_delay(self):
        self.is_debugging = True
        specific_triggers = ["WetOutside","ReceivesBednet"]
        specific_delay = 13
        self.usagebednet_build(triggers=specific_triggers,
                               triggered_campaign_delay=specific_delay)

        for trigger_condition in specific_triggers:
            self.assertIn(trigger_condition, self.intervention_config['Trigger_Conditions'])
        self.assertEqual(specific_delay, self.intervention_config['Trigger_Condition_Delay'])
        return



    # endregion

class TestMalariaInterventions_17Dec20(TestMalariaInterventions):

    def setUp(self):
        super(TestMalariaInterventions_17Dec20, self).setUp()
        self.schema_file = schema_17Dec20


if __name__ == '__main__':
    unittest.main()
