import unittest
import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from emodpy_malaria.reporters.builtin import \
    ReportVectorGenetics, ReportVectorStats, MalariaPatientJSONReport, MalariaSummaryReport


class TestMalariaReport(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_reporter = None

    # region vector stats
    def rvs_build_vector_stats_reporter(
            self,
            include_gestation_columns=None,
            include_wolbachia_columns=None,
            species_list=None,
            stratify_by_species=None
    ):
        def rvs_config_builder(params):
            if include_gestation_columns is not None:
                params.Include_Gestation_Columns = include_gestation_columns
            if include_wolbachia_columns is not None:
                params.Include_Wolbachia_Columns = include_wolbachia_columns
            if species_list is not None:
                params.Species_List = species_list
            if stratify_by_species is not None:
                params.Stratify_By_Species = stratify_by_species
            return params
        import schema_path_file
        self.tmp_reporter = ReportVectorStats()
        self.tmp_reporter.config(rvs_config_builder, schema_path_file)
        return self.tmp_reporter

    def test_vector_stats_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.rvs_build_vector_stats_reporter()
        self.assertIsNotNone(self.tmp_reporter)
        p_dict = self.tmp_reporter.parameters
        self.assertEqual(p_dict['Stratify_By_Species'], 0)
        self.assertEqual(p_dict['Species_List'], [])
        self.assertEqual(p_dict['Include_Wolbachia_Columns'],0)
        self.assertEqual(p_dict['Include_Gestation_Columns'], 0)
        pass

    def test_vector_stats_custom(self):
        self.assertIsNone(self.tmp_reporter)
        self.rvs_build_vector_stats_reporter(
            include_gestation_columns=1,
            include_wolbachia_columns=1,
            species_list=["gambiae", "SillySkeeter"],
            stratify_by_species=1
        )
        self.assertIsNotNone(self.tmp_reporter)
        p_dict = self.tmp_reporter.parameters
        self.assertEqual(p_dict['Stratify_By_Species'], 1)
        self.assertEqual(p_dict['Species_List'], ["gambiae", "SillySkeeter"])
        self.assertEqual(p_dict['Include_Wolbachia_Columns'], 1)
        self.assertEqual(p_dict['Include_Gestation_Columns'], 1)
        pass
    # endregion

    # region vector stats malaria
    @unittest.skip("Report NYI")
    def test_vector_stats_malaria_default(self):
        pass

    @unittest.skip("Report NYI")
    def test_vector_stats_malaria_custom(self):
        pass

    # endregion

    # region vector genetics

    def rvg_build_vector_genetics_reporter(
            self,
            duration_days=None,
            file_name_suffix=None,
            gender=None,
            include_vector_state_columns=None,
            report_description=None,
            species=None,
            start_day=None,
            allele_combinations_for_stratification=None,
            alleles_for_stratification=None,
            combine_similar_genomes=None,
            specific_genome_combinations_for_stratification=None
    ):
        def rvg_config_builder(params):
            if duration_days is not None:
                params.Duration_Days = duration_days
            if file_name_suffix is not None:
                params.File_Name_Suffix = file_name_suffix
            if gender is not None:
                params.Gender = gender
            if include_vector_state_columns is not None:
                params.Include_Vector_State_Columns = include_vector_state_columns
            if report_description is not None:
                params.Report_Description = report_description
            if species is not None:
                params.Species = species
            if start_day is not None:
                params.Start_Day = start_day
            if allele_combinations_for_stratification is not None:
                params.Allele_Combinations_For_Stratification = allele_combinations_for_stratification
            if alleles_for_stratification is not None:
                params.Alleles_For_Stratification = alleles_for_stratification
            if specific_genome_combinations_for_stratification is not None:
                params.Specific_Genome_Combinations_For_Stratification = specific_genome_combinations_for_stratification
            if combine_similar_genomes is not None:
                params.Combine_Similar_Genomes = combine_similar_genomes
            return params
        import schema_path_file
        self.tmp_reporter = ReportVectorGenetics()
        self.tmp_reporter.config(rvg_config_builder, schema_path_file)
        return self.tmp_reporter

    def test_vg_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.rvg_build_vector_genetics_reporter()
        self.assertIsNotNone(self.tmp_reporter)
        p_dict = self.tmp_reporter.parameters
        self.assertGreater(p_dict['Duration_Days'], 100_000)
        self.assertEqual(p_dict['File_Name_Suffix'], "")
        self.assertEqual(p_dict['Gender'], "VECTOR_FEMALE")
        self.assertEqual(p_dict['Include_Vector_State_Columns'], 1)
        self.assertEqual(p_dict['Report_Description'], "")
        self.assertEqual(p_dict['Start_Day'], 0)
        self.assertEqual(p_dict['Combine_Similar_Genomes'], 0)
        self.assertEqual(p_dict['Stratify_By'], "GENOME")

    def test_vg_custom_genome_stratification(self):
        self.assertIsNone(self.tmp_reporter)
        self.rvg_build_vector_genetics_reporter(
            combine_similar_genomes=1
        )
        self.assertIsNotNone(self.tmp_reporter)
        p_dict = self.tmp_reporter.parameters
        self.assertEqual(p_dict['Combine_Similar_Genomes'], 1)
        self.assertEqual(p_dict['Stratify_By'], "GENOME")

    @unittest.skip("See GH #42")
    def test_vg_custom_specific_genome_stratification(self):
        self.rvg_build_vector_genetics_reporter(
            duration_days=12_345,
            file_name_suffix="_silly",
            gender="VECTOR_MALE",
            include_vector_state_columns=0,
            report_description="Does some stuff",
            species="Silly_Skeeter",
            start_day=1234,
            combine_similar_genomes=1,
            specific_genome_combinations_for_stratification=[["X"],["*"]]
        )
        self.assertIsNotNone(self.tmp_reporter)
        p_dict = self.tmp_reporter.parameters
        self.assertEqual(p_dict['Duration_Days'], 12_345)
        self.assertEqual(p_dict['File_Name_Suffix'], "_silly")
        self.assertEqual(p_dict['Gender'], "VECTOR_MALE")
        self.assertEqual(p_dict['Include_Vector_State_Columns'], 0)
        self.assertEqual(p_dict['Report_Description'], "Does some stuff")
        self.assertEqual(p_dict['Species'], "Silly_Skeeter")
        self.assertEqual(p_dict['Combine_Similar_Genomes'], 1)
        self.assertEqual(p_dict['Specific_Genome_Combinations_For_Stratification'],
                         [["X"],["*"]])
        self.assertEqual(p_dict['Stratify_By'], "SPECIFIC_GENOME") # because of previous

    def test_vg_custom_specific_genome_stratification_no_combination(self):
        self.rvg_build_vector_genetics_reporter(
            duration_days=12_345,
            file_name_suffix="_silly",
            gender="VECTOR_MALE",
            include_vector_state_columns=0,
            report_description="Does some stuff",
            species="Silly_Skeeter",
            start_day=1234,
            specific_genome_combinations_for_stratification=[["X"],["*"]]
        )
        self.assertIsNotNone(self.tmp_reporter)
        p_dict = self.tmp_reporter.parameters
        self.assertEqual(p_dict['Duration_Days'], 12_345)
        self.assertEqual(p_dict['File_Name_Suffix'], "_silly")
        self.assertEqual(p_dict['Gender'], "VECTOR_MALE")
        self.assertEqual(p_dict['Include_Vector_State_Columns'], 0)
        self.assertEqual(p_dict['Report_Description'], "Does some stuff")
        self.assertEqual(p_dict['Species'], "Silly_Skeeter")
        self.assertEqual(p_dict['Combine_Similar_Genomes'], 0)
        self.assertEqual(p_dict['Specific_Genome_Combinations_For_Stratification'],
                         [["X"],["*"]])
        self.assertEqual(p_dict['Stratify_By'], "SPECIFIC_GENOME") # because of previous

    def test_vg_custom_allele_stratification(self):
        self.rvg_build_vector_genetics_reporter(
            gender="VECTOR_BOTH_GENDERS",
            allele_combinations_for_stratification=[["X"],["Y"]]
        )
        self.assertIsNotNone(self.tmp_reporter)
        p_dict = self.tmp_reporter.parameters
        self.assertEqual(p_dict['Gender'],"VECTOR_BOTH_GENDERS")
        self.assertEqual(p_dict['Allele_Combinations_For_Stratification'], [["X"],["Y"]])
        self.assertEqual(p_dict["Stratify_By"], "ALLELE")
        pass

    def test_vg_custom_allele_frequency_stratification(self):
        self.rvg_build_vector_genetics_reporter(
            alleles_for_stratification=[]
        )
        self.assertIsNotNone(self.tmp_reporter)
        p_dict = self.tmp_reporter.parameters
        self.assertEqual(p_dict['Alleles_For_Stratification'], [])
        self.assertEqual(p_dict['Stratify_By'], "ALLELE_FREQ")
        pass

    # endregion

    # region malaria patient json report
    @unittest.skip("Test NYI")
    def test_malaria_patient_json_report_default(self):
        pass

    @unittest.skip("Test NYI")
    def test_malaria_patient_json_report_custom(self):
        pass
    # endregion

    # region malaria summary report

    @unittest.skip("Test NYI")
    def test_malaria_summary_report_default(self):
        pass

    @unittest.skip("Test NYI")
    def test_malaria_summary_report_custom(self):
        pass

    # endregion

    # region vector migration report

    @unittest.skip("Report NYI")
    def test_vector_migration_report_default(self):
        pass

    @unittest.skip("Report NYI")
    def test_vector_migration_report_custom(self):
        pass

    # endregion

    # region vector habitat report

    @unittest.skip("Report NYI")
    def test_vector_habitat_report(self):
        pass

    # endregion



if __name__ == '__main__':
    unittest.main()
