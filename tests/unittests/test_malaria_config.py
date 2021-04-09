import unittest
from copy import deepcopy
import json
import os, sys

from emod_api.config import default_from_schema_no_validation as dfs

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

default_config = None # is set in setUpClass()

import schema_path_file

from emodpy_malaria.config import \
    set_team_defaults, \
    add_alleles, \
    add_mutation , \
    add_resistance

from emodpy_malaria.config import alleles as conf_alleles
from emodpy_malaria.config import mutations as conf_mutations
from emodpy_malaria.config import insecticides as conf_insecticides


class TestMalariaConfig(unittest.TestCase):
    default_config = None
    @classmethod
    def setUpClass(cls) -> None:
        cls.default_config = dfs.write_default_from_schema(schema_path_file.schema_path) # default_config.json


    def setUp(self) -> None:
        self.is_debugging = False

        self.config = None
        default_config_name = \
            dfs.write_default_from_schema(schema_path_file.schema_path)
        self.config = dfs.get_config_from_default_and_params(
            config_path='default_config.json',
            set_fn=self.set_malaria_config
        )
        self.insecticides = None
        # Unused yet
        self.alleles = None
        self.mutations = None

    def set_malaria_config(self, config):
        config.parameters.Simulation_Type = "MALARIA_SIM"
        config.parameters.Infectious_Period_Constant = 0
        config.parameters.Enable_Demographics_Birth = 1
        config.parameters.Enable_Demographics_Reporting = 0
        config.parameters.Enable_Immune_Decay = 0
        config.parameters.Mortality_Blocking_Immunity_Decay_Rate = 0
        config.parameters.Mortality_Blocking_Immunity_Duration_Before_Decay = 270
        config.parameters.Run_Number = 99
        config.parameters.Simulation_Duration = 60
        config.parameters.Enable_Demographics_Risk = 1

        return config

    def add_alleles(self, allele_names_in, allele_values_in):
        add_alleles(allele_names_in=allele_names_in,
                         allele_inits_in=allele_values_in)
        self.alleles = conf_alleles
        raise NotImplemented("The method under test is not used anywhere")

    def add_mutation(self, from_allele, to_allele, rate):
        add_mutation(
            from_allele=from_allele,
            to_allele=to_allele,
            rate=rate)
        self.mutations = conf_mutations
        raise NotImplemented("The method under test is not used anywhere")

    def add_resistance(self, insecticide_name, species, combo,
                       blocking=1.0, killing=1.0):
        add_resistance(
            manifest=schema_path_file,
            insecticide_name=insecticide_name,
            species=species,
            combo=combo,
            blocking=blocking,
            killing=killing
        )
        self.insecticides = conf_insecticides

    def tearDown(self) -> None:
        if self.is_debugging:
            with open(f'DEBUG_{self._testMethodName}.json', 'w') as outfile:
                debug_object = {}
                debug_object['config'] = self.config
                json.dump(debug_object, outfile, indent=4, sort_keys=True)

    @unittest.skip("NYI")
    def test_alleles(self):
        self.assertIsNone(self.alleles)
        # self.add_alleles() # Don't know how to add one
        self.assertGreater(len(self.alleles), 0) # list should have an allele or two

    def test_team_defaults(self):
        self.is_debugging = False
        # with open('DEBUG_a_config.json','w') as outfile:
        #     json.dump(self.config, outfile, indent=4, sort_keys=True)
        raw_config_parameters = deepcopy(self.config['parameters'])
        raw_vsp = raw_config_parameters['Vector_Species_Params']
        raw_mdp = raw_config_parameters['Malaria_Drug_Params']
        self.assertEqual(len(raw_vsp), 0,
                         msg=f"Vector Species Params should start empty. got:"
                             f" {raw_vsp}")
        self.assertEqual(len(raw_vsp), 0,
                         msg=f"Malaria_Drug_Params should start empty. got:"
                             f" {raw_mdp}")
        self.config = set_team_defaults(config=self.config,
                                        mani=schema_path_file)
        updated_config_parameters = self.config['parameters']
        updated_vsp = updated_config_parameters['Vector_Species_Params']
        updated_mdp = updated_config_parameters['Malaria_Drug_Params']
        self.assertGreater(len(updated_vsp),
                           len(raw_vsp))
        self.assertGreater(len(updated_mdp),
                           len(raw_mdp))
        found_species_names = []
        for vsp in updated_vsp:
            found_species_names.append(vsp['Name'])
        self.assertIn('gambiae', found_species_names)
        self.assertIn('funestus', found_species_names)
        self.assertIn('arabiensis', found_species_names)

        found_drug_names = []
        for mdp in updated_mdp:
            found_drug_names.append(mdp['Name'])
        self.assertIn('Chloroquine', found_drug_names)
        self.assertIn('Artemether', found_drug_names)
        self.assertIn('Lumefantrine', found_drug_names)

    def test_add_resistance_new_insecticide(self):
        self.add_resistance(insecticide_name='Honey'
                            , species='arabiensis'
                            , combo=[['X', '*']]
                            , killing=0.0
                            , blocking=0.2)
        self.add_resistance(insecticide_name='Honey'
                            , species='funestus'
                            , combo=[['X', 'Y']]
                            , killing=0.0
                            , blocking=0.2)
        self.add_resistance(insecticide_name='Vinegar'
                            , species='arabiensis'
                            , combo=[['X', 'Y']]
                            , killing=0.0)
        self.assertEqual(len(self.insecticides), 2)
        self.assertEqual(len(self.insecticides['Honey']['parameters']['Resistances']), 2)
        self.assertEqual(len(self.insecticides['Honey']['parameters']['Resistances']), 2)
        self.assertEqual(len(self.insecticides['Vinegar']['parameters']['Resistances']), 1)


if __name__ == '__main__':
    unittest.main()
