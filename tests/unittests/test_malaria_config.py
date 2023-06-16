import unittest
from copy import deepcopy
import json
import os
import sys

from emod_api.config import default_from_schema_no_validation as dfs
import schema_path_file
from emodpy_malaria.malaria_vector_species_params import species_params
from emodpy_malaria.malaria_config import set_team_defaults, add_species, set_max_larval_capacity, \
    configure_linear_spline, set_species_param, add_microsporidia, add_insecticide_resistance, add_drug_resistance,\
    set_drug_param, set_team_drug_params, set_parasite_genetics_params, get_drug_params
from emodpy_malaria.vector_config import \
    add_genes_and_alleles, \
    add_mutation, \
    add_insecticide_resistance, \
    add_trait, add_species_drivers

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

default_config = None  # is set in setUpClass()


class TestMalariaConfig(unittest.TestCase):
    default_config = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.default_config = dfs.write_default_from_schema(schema_path_file.schema_file)  # default_config.json

    def setUp(self) -> None:
        self.is_debugging = False
        self.config = dfs.get_config_from_default_and_params(
            config_path='default_config.json',
            set_fn=self.set_malaria_config
        )
        self.config = set_team_defaults(self.config, schema_path_file)

    def set_malaria_config(self, config):
        config.parameters.Simulation_Type = "MALARIA_SIM"
        config.parameters.Enable_Demographics_Birth = 1
        config.parameters.Enable_Demographics_Reporting = 0
        config.parameters.Run_Number = 99
        config.parameters.Simulation_Duration = 60
        config.parameters.Enable_Demographics_Risk = 1

        return config

    def add_insecticide_resistance(self, schema_path_file, insecticide_name, species, combo,
                                   blocking=1.0, killing=1.0, larval_killing=1.0, repelling=1.0):
        add_insecticide_resistance(
            self.config,
            manifest=schema_path_file,
            insecticide_name=insecticide_name,
            species=species,
            allele_combo=combo,
            blocking=blocking,
            killing=killing,
            larval_killing=larval_killing,
            repelling=repelling
        )

    def tearDown(self) -> None:
        if self.is_debugging:
            with open(f'DEBUG_{self._testMethodName}.json', 'w') as outfile:
                debug_object = {}
                debug_object['config'] = self.config
                json.dump(debug_object, outfile, indent=4, sort_keys=True)

    def test_team_defaults(self):

        self.assertEqual(self.config.parameters.Vector_Species_Params, [])

        found_drug_names = []
        for mdp in self.config.parameters.Malaria_Drug_Params:
            found_drug_names.append(mdp['Name'])
        self.assertIn('Chloroquine', found_drug_names)
        self.assertIn('Artemether', found_drug_names)
        self.assertIn('Lumefantrine', found_drug_names)

    def test_add_resistance_new_insecticide(self):
        add_insecticide_resistance(self.config,
                                   schema_path_file,
                                   insecticide_name='Honey',
                                   species='arabiensis',
                                   allele_combo=[['X', '*']],
                                   killing=0.17,
                                   blocking=0.22,
                                   larval_killing=0.7,
                                   repelling=0.33)
        add_insecticide_resistance(self.config,
                                   schema_path_file,
                                   insecticide_name='Honey',
                                   species='funestus',
                                   allele_combo=[['X', 'Y']],
                                   killing=0.15,
                                   blocking=0.2,
                                   larval_killing=0.55,
                                   repelling=0.33)
        add_insecticide_resistance(self.config,
                                   schema_path_file,
                                   insecticide_name='Vinegar',
                                   species='arabiensis',
                                   allele_combo=[['X', 'Y']],
                                   killing=0.5,
                                   blocking=0.2,
                                   larval_killing=0.7,
                                   repelling=0.44)
        self.assertEqual(len(self.config.parameters.Insecticides), 2)
        for insecticide in self.config.parameters.Insecticides:
            if insecticide.Name == "Honey":
                self.assertEqual(len(insecticide.Resistances), 2)
                for resistance in insecticide.Resistances:
                    if resistance.Species == "arabiensis":
                        self.assertEqual(resistance.Allele_Combinations, [['X', '*']])
                        self.assertEqual(resistance.Larval_Killing_Modifier, 0.7)
                        self.assertEqual(resistance.Killing_Modifier, 0.17)
                        self.assertEqual(resistance.Blocking_Modifier, 0.22)
                    elif resistance.Species == "funestus":
                        if resistance.Species == "arabiensis":
                            self.assertEqual(resistance.Larval_Killing_Modifier, 0.55)
                            self.assertEqual(resistance.Killing_Modifier, 0.15)
                            self.assertEqual(resistance.Blocking_Modifier, 0.2)
            elif insecticide.Name == "Vinegar":
                self.assertEqual(len(insecticide.Resistances), 1)
                self.assertEqual(insecticide.Resistances[0].Species, "arabiensis")
                self.assertEqual(insecticide.Resistances[0].Repelling_Modifier, 0.44)

            else:
                raise ValueError(f"We should not be here, shouldn't have insecticide with name {insecticide.Name}.\n")

    def test_add_genes_and_alleles(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="funestus",
                              alleles=[("a0", 0.5), ("a1", 0.35), ("a2", 0.15)])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="funestus",
                              alleles=[("b0", 0.90), ("b1", 0.1)])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="arabiensis",
                              alleles=[("c0", 0.66), ("c1", 0.1), ("c2", 0.24)])
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                self.assertEqual(len(species.Genes), 2)
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "a2":
                            self.assertEqual(allele.Initial_Allele_Frequency, 0.15)
            elif species.Name == "arabiensis":
                self.assertEqual(len(species.Genes), 1)
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "c0":
                            self.assertEqual(allele.Initial_Allele_Frequency, 0.66)

    def test_add_genes_and_alleles_gender_gene(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="funestus",
                              alleles=[("a0", 0.5, 1), ("a1", 0.35, 1), ("a2", 0.15)])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="funestus",
                              alleles=[("b0", 0.90), ("b1", 0.1)])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="arabiensis",
                              alleles=[("c0", 0.66), ("c1", 0.1), ("c2", 0.24)])
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                self.assertEqual(len(species.Genes), 2)
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "a2":
                            self.assertEqual(gene.Is_Gender_Gene, 1)
                            self.assertEqual(allele.Initial_Allele_Frequency, 0.15)
            elif species.Name == "arabiensis":
                self.assertEqual(len(species.Genes), 1)
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "c0":
                            self.assertEqual(gene.Is_Gender_Gene, 0)
                            self.assertEqual(allele.Initial_Allele_Frequency, 0.66)

    def test_add_trait(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="funestus",
                              alleles=[("a0", 0.5, 1), ("a1", 0.35, 1), ("a2", 0.15)])
        add_trait(self.config, schema_path_file, species="funestus", allele_combo=[["X", "X"], ["a0", "a1"]],
                  trait_modifiers=[("ADJUST_FERTILE_EGGS", 0.80)])
        for species in self.config.parameters.Vector_Species_Params:  # should only be one
            for gene_to_trait_modifier in species.Gene_To_Trait_Modifiers:  # should only be one
                self.assertEqual(gene_to_trait_modifier.Trait_Modifiers[0]["Trait"], "ADJUST_FERTILE_EGGS")
                self.assertEqual(gene_to_trait_modifier.Trait_Modifiers[0]["Modifier"], 0.80)
                self.assertEqual(gene_to_trait_modifier.Allele_Combinations, [["X", "X"], ["a0", "a1"]])

    def test_add_mutation(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="funestus",
                              alleles=[("a0", 0.5), ("a1", 0.35), ("a2", 0.15)])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="funestus",
                              alleles=[("b0", 0.90), ("b1", 0.1)])
        add_genes_and_alleles(self.config,
                              schema_path_file,
                              species="arabiensis",
                              alleles=[("c0", 0.66), ("c1", 0.1), ("c2", 0.24)])
        add_mutation(self.config, schema_path_file, "arabiensis", mutate_from="c1", mutate_to="c2",
                     probability=0.04)
        add_mutation(self.config, schema_path_file, "arabiensis", mutate_from="c0", mutate_to="c1",
                     probability=0.02)
        add_mutation(self.config, schema_path_file, "funestus", mutate_from="a0", mutate_to="a1",
                     probability=0.023)
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "a2":
                            self.assertEqual(gene.Mutations[0].Mutate_From, "a0")
                            self.assertEqual(gene.Mutations[0].Mutate_To, "a1")
                            self.assertEqual(gene.Mutations[0].Probability_Of_Mutation, 0.023)
            elif species.Name == "arabiensis":
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "c0":
                            self.assertEqual(len(gene.Mutations), 2)
                            for mutation in gene.Mutations:
                                if mutation.Mutate_From == "c0":
                                    self.assertEqual(mutation.Mutate_To, "c1")
                                    self.assertEqual(mutation.Probability_Of_Mutation, 0.02)
                                elif mutation.Mutate_From == "c1":
                                    self.assertEqual(mutation.Mutate_To, "c2")
                                    self.assertEqual(mutation.Probability_Of_Mutation, 0.04)

    def test_set_max_larval_capacity(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        set_max_larval_capacity(self.config, "funestus", "TEMPORARY_RAINFALL", 123000)
        set_max_larval_capacity(self.config, "arabiensis", "TEMPORARY_RAINFALL", 654000)
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                self.assertEqual(species.Habitats[0]["Habitat_Type"], "TEMPORARY_RAINFALL")
                self.assertEqual(species.Habitats[0]["Max_Larval_Capacity"], 123000)
            elif species.Name == "arabiensis":
                self.assertEqual(species.Habitats[0]["Habitat_Type"], "TEMPORARY_RAINFALL")
                self.assertEqual(species.Habitats[0]["Max_Larval_Capacity"], 654000)

    def test_configure_linear_spline(self):
        add_species(self.config, schema_path_file, "funestus")
        times = [1, 60, 180, 300, 500, 720]
        values = [0.5, 1, 3, 2, 1, 0.1]
        spline = configure_linear_spline(schema_path_file, max_larval_capacity=123456,
                                         capacity_distribution_number_of_years=2,
                                         capacity_distribution_over_time={"Times": times,
                                                                          "Values": values})
        self.assertEqual(spline.Max_Larval_Capacity, 123456)
        self.assertEqual(spline.Habitat_Type, "LINEAR_SPLINE")
        self.assertEqual(spline.Capacity_Distribution_Over_Time.Times, times)
        self.assertEqual(spline.Capacity_Distribution_Over_Time.Values, values)
        self.assertEqual(spline.Capacity_Distribution_Number_Of_Years, 2)

    def test_set_species_param(self):
        add_species(self.config, schema_path_file, ["funestus", "gambiae"])
        set_species_param(self.config, species="funestus", parameter="Immature_Duration", value=3)
        set_species_param(self.config, species="gambiae", parameter="Days_Between_Feeds", value=5)
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                self.assertEqual(species.Immature_Duration, 3)
            elif species.Name == "gambiae":
                self.assertEqual(species.Days_Between_Feeds, 5)

    def test_add_species_drivers(self):
        add_species(self.config, schema_path_file, ["gambiae"])
        add_genes_and_alleles(self.config, schema_path_file, "gambiae", [("one", 0.9), ("two", 0.05), ("three", 0.05)])
        add_genes_and_alleles(self.config, schema_path_file, "gambiae",
                              [("a", 0.9, 0), ("b", 0.05, 1), ("c", 0.05, 0), ("d", 0, 1)])
        add_species_drivers(self.config, schema_path_file, "gambiae", driving_allele="c",
                            driver_type="INTEGRAL_AUTONOMOUS", to_copy="two", to_replace="one",
                            likelihood_list=[("one", 0.15), ("two", 0.85)])
        add_species_drivers(self.config, schema_path_file, "gambiae", driving_allele="one",
                            driver_type="X_SHRED", to_copy="one", to_replace="one",
                            likelihood_list=[("one", 0.15), ("two", 0.85)], shredding_allele_required="b",
                            allele_shredding_fraction=0.3, allele_to_shred="a",
                            allele_to_shred_to_surviving_fraction=0.1, allele_to_shred_to='c')
        add_species_drivers(self.config, schema_path_file, "gambiae", driving_allele="two",
                            driver_type="Y_SHRED", to_copy="two", to_replace="one",
                            likelihood_list=[("one", 0.15), ("two", 0.85)], shredding_allele_required="a",
                            allele_shredding_fraction=0.4, allele_to_shred="d",
                            allele_to_shred_to_surviving_fraction=0.5, allele_to_shred_to='b')
        all_found = 0
        for species in self.config.parameters.Vector_Species_Params:  # should only be one
            for driver in species.Drivers:
                if driver.Driver_Type == "INTEGRAL_AUTONOMOUS":
                    all_found += 1
                    self.assertEqual(driver.Driving_Allele, "c")
                    for allele_driven in driver.Alleles_Driven:  # should only be one
                        self.assertEqual(allele_driven.Allele_To_Copy, "two")
                        self.assertEqual(allele_driven.Allele_To_Replace, "one")
                        for likelihood in allele_driven.Copy_To_Likelihood:
                            if likelihood.Copy_To_Allele == "one":
                                all_found += 1
                                self.assertEqual(likelihood.Likelihood, 0.15)
                            elif likelihood.Copy_To_Allele == "two":
                                all_found += 1
                                self.assertEqual(likelihood.Likelihood, 0.85)
                elif driver.Driver_Type == "X_SHRED":
                    all_found += 1
                    self.assertEqual(driver.Driving_Allele, "one")
                    self.assertEqual(driver.Driving_Allele_Params.Allele_To_Copy, "one")
                    self.assertEqual(driver.Driving_Allele_Params.Allele_To_Replace, "one")
                    for likelihood in driver.Driving_Allele_Params.Copy_To_Likelihood:
                        if likelihood.Copy_To_Allele == "one":
                            all_found += 1
                            self.assertEqual(likelihood.Likelihood, 0.15)
                        elif likelihood.Copy_To_Allele == "two":
                            all_found += 1
                            self.assertEqual(likelihood.Likelihood, 0.85)
                    self.assertEqual(driver.Shredding_Alleles.Allele_Required, "b")
                    self.assertEqual(driver.Shredding_Alleles.Allele_To_Shred, "a")
                    self.assertEqual(driver.Shredding_Alleles.Allele_To_Shred_To, "c")
                    self.assertEqual(driver.Shredding_Alleles.Allele_Shredding_Fraction, 0.3)
                    self.assertEqual(driver.Shredding_Alleles.Allele_To_Shred_To_Surviving_Fraction, 0.1)
                elif driver.Driver_Type == "Y_SHRED":
                    all_found += 1
                    self.assertEqual(driver.Driving_Allele, "two")
                    self.assertEqual(driver.Driving_Allele_Params.Allele_To_Copy, "two")
                    self.assertEqual(driver.Driving_Allele_Params.Allele_To_Replace, "one")
                    for likelihood in driver.Driving_Allele_Params.Copy_To_Likelihood:
                        if likelihood.Copy_To_Allele == "one":
                            all_found += 1
                            self.assertEqual(likelihood.Likelihood, 0.15)
                        elif likelihood.Copy_To_Allele == "two":
                            all_found += 1
                            self.assertEqual(likelihood.Likelihood, 0.85)
                    self.assertEqual(driver.Shredding_Alleles.Allele_Required, "a")
                    self.assertEqual(driver.Shredding_Alleles.Allele_To_Shred, "d")
                    self.assertEqual(driver.Shredding_Alleles.Allele_To_Shred_To, "b")
                    self.assertEqual(driver.Shredding_Alleles.Allele_Shredding_Fraction, 0.4)
                    self.assertEqual(driver.Shredding_Alleles.Allele_To_Shred_To_Surviving_Fraction, 0.5)

        self.assertEqual(all_found, 9)

    def test_add_microsporidia(self):
        add_species(self.config, schema_path_file, ["gambiae"])
        transmission_modification = {"Times": [0, 6], "Values": [1, 0.5]}
        add_microsporidia(self.config, schema_path_file, species_name="gambiae",
                          strain_name="Strain_B",
                          male_to_egg_probability=0.9,
                          female_to_male_probability=0.2,
                          male_to_female_probability=0.33, female_to_egg_probability=0.7,
                          duration_to_disease_acquisition_modification=None,
                          duration_to_disease_transmission_modification=transmission_modification,
                          larval_growth_modifier=0.56,
                          female_mortality_modifier=0.87, male_mortality_modifier=0.96)
        for species in self.config.parameters.Vector_Species_Params:  # should only be one
            for strain in species.Microsporidia:  # should only be one
                self.assertEqual(strain.Strain_Name, "Strain_B")
                self.assertEqual(strain.Male_To_Female_Transmission_Probability, 0.33)
                self.assertEqual(strain.Male_To_Egg_Transmission_Probability, 0.9)
                self.assertEqual(strain.Male_Mortality_Modifier, 0.96)
                self.assertEqual(strain.Larval_Growth_Modifier, 0.56)
                self.assertEqual(strain.Female_To_Male_Transmission_Probability, 0.2)
                self.assertEqual(strain.Female_To_Egg_Transmission_Probability, 0.7)
                self.assertEqual(strain.Female_Mortality_Modifier, 0.87)
                self.assertEqual(strain.Duration_To_Disease_Transmission_Modification.Times, [0, 6])
                self.assertEqual(strain.Duration_To_Disease_Transmission_Modification.Values, [1, 0.5])
                self.assertEqual(strain.Duration_To_Disease_Acquisition_Modification.Times,  [0, 3, 6, 9])
                self.assertEqual(strain.Duration_To_Disease_Acquisition_Modification.Values,  [1, 1, 0.5, 0])

    def test_set_parasite_genetics_params(self):
        self.config = dfs.get_config_from_default_and_params(
            config_path='default_config.json',
            set_fn=self.set_malaria_config
        )
        set_parasite_genetics_params(self.config, schema_path_file)
        self.assertEqual(self.config.parameters.Parasite_Genetics.Crossover_Gamma_Theta, 0.38)
        self.assertEqual(self.config.parameters.Parasite_Genetics.Drug_Resistant_Genome_Locations, [])
        self.assertEqual(self.config.parameters.Parasite_Genetics.Num_Oocyst_From_Bite_Fail, 3)
        self.assertEqual(self.config.parameters.Parasite_Genetics.Var_Gene_Randomness_Type, "ALL_RANDOM")
        for species in self.config.parameters.Vector_Species_Params:  # should only be one
            self.assertEqual(species.Habitats[0]["Habitat_Type"], "LINEAR_SPLINE")
            self.assertEqual(species.Habitats[0]["Max_Larval_Capacity"], 316227766.01683795)

    def test_add_drug_resistance(self):
        add_drug_resistance(self.config, schema_path_file, drugname="Artemether", drug_resistant_string="AAA",
                            pkpd_c50_modifier=0.4, max_irbc_kill_modifier=0.01)
        set_drug_param(self.config, drug_name="Artemether", parameter="Drug_Cmax", value=239487)
        drug_params = get_drug_params(self.config, drug_name="Artemether")
        self.assertEqual(drug_params.Resistances[0]["Drug_Resistant_String"], "AAA")
        self.assertEqual(drug_params.Resistances[0]["Max_IRBC_Kill_Modifier"], 0.01)
        self.assertEqual(drug_params.Resistances[0]["PKPD_C50_Modifier"], 0.4)
        self.assertEqual(drug_params.Drug_Cmax, 239487)

    def test_species_params(self):
        species_list = ["gambiae", "arabiensis", "funestus", "fpg_gambiae", "minimus", "dirus", "MYSTERIO"]
        for species in species_list:
            configuration_to_check = species_params(schema_path_file, species=species)
            if species == "MYSTERIO":
                self.assertEqual(configuration_to_check,
                                 ["gambiae", "arabiensis", "funestus", "fpg_gambiae", "minimus", "dirus"])
            elif species == "gambiae":
                self.assertEqual(configuration_to_check.Name, species)
                self.assertEqual(configuration_to_check.Indoor_Feeding_Fraction, 0.95)
                self.assertEqual(configuration_to_check.Transmission_Rate, 0.9)
            elif species == "arabiensis":
                self.assertEqual(configuration_to_check.Name, species)
                self.assertEqual(configuration_to_check.Indoor_Feeding_Fraction, 0.5)
                self.assertEqual(configuration_to_check.Transmission_Rate, 0.9)
            elif species == "funestus":
                self.assertEqual(configuration_to_check.Name, species)
                self.assertEqual(configuration_to_check.Indoor_Feeding_Fraction, 0.95)
                self.assertEqual(configuration_to_check.Transmission_Rate, 0.9)
            elif species == "fpg_gambiae":
                self.assertEqual(configuration_to_check.Name, "gambiae")
                self.assertEqual(configuration_to_check.Indoor_Feeding_Fraction, 0.5)
                self.assertEqual(configuration_to_check.Transmission_Rate, 0.9)
            elif species == "minimus":
                self.assertEqual(configuration_to_check.Name, species)
                self.assertEqual(configuration_to_check.Indoor_Feeding_Fraction, 0.6)
                self.assertEqual(configuration_to_check.Transmission_Rate, 0.8)
            elif species == "dirus":
                self.assertEqual(configuration_to_check.Name, species)
                self.assertEqual(configuration_to_check.Indoor_Feeding_Fraction, 0.01)
                self.assertEqual(configuration_to_check.Transmission_Rate, 0.8)


if __name__ == '__main__':
    unittest.main()
