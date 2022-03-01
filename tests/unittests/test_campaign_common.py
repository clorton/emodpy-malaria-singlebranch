#!/usr/bin/env python
import unittest
from emod_api.interventions.common import *
from emodpy_malaria.interventions.common import ScheduledCampaignEvent, TriggeredCampaignEvent
import emod_api.campaign as camp

from pathlib import Path
import sys
parent = Path(__file__).resolve().parent
sys.path.append(str(parent))
import schema_path_file

camp.schema_path = schema_path_file.schema_path
schema_path = schema_path_file.schema_path


class CommonInterventionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_scheduled_campaign_event(self):
        target_num_individuals = 123
        camp.schema_path = schema_path_file.schema_file
        event = ScheduledCampaignEvent(camp,
                                       Start_Day=30,
                                       Node_Ids=[1, 2],
                                       Target_Num_Individuals=target_num_individuals,
                                       Intervention_List=["some_intervention"]
                                       )

        self.assertEqual(event.Event_Coordinator_Config.Target_Num_Individuals, target_num_individuals)

    def test_triggered_campaign_event(self):
        target_num_individuals = 123
        camp.schema_path = schema_path_file.schema_file
        event = TriggeredCampaignEvent(camp,
                                       Start_Day=30,
                                       Node_Ids=[1, 2],
                                       Event_Name="some_name",
                                       Triggers=["trigger"],
                                       Target_Num_Individuals=target_num_individuals,
                                       Intervention_List=["some_intervention"]
                                       )

        self.assertEqual(event.Event_Coordinator_Config.Target_Num_Individuals, target_num_individuals)



