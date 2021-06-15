import unittest
import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from emodpy_malaria.reporters.builtin import \
    ReportVectorGenetics, ReportVectorStats, MalariaPatientJSONReport, MalariaSummaryReport, FilteredMalariaReport, ReportEventCounter


class TestMalariaReport(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_reporter = None
        self.p_dict = None

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
        self.p_dict = self.tmp_reporter.parameters
        return

    def test_vector_stats_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.rvs_build_vector_stats_reporter()
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Stratify_By_Species'], 0)
        self.assertEqual(self.p_dict['Species_List'], [])
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'],0)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], 0)
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
        self.assertEqual(self.p_dict['Stratify_By_Species'], 1)
        self.assertEqual(self.p_dict['Species_List'], ["gambiae", "SillySkeeter"])
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], 1)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], 1)
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
            if combine_similar_genomes is not None:
                params.Combine_Similar_Genomes = combine_similar_genomes
            if specific_genome_combinations_for_stratification is not None:
                params.Specific_Genome_Combinations_For_Stratification = specific_genome_combinations_for_stratification
            return params
        import schema_path_file
        self.tmp_reporter = ReportVectorGenetics()
        self.tmp_reporter.config(rvg_config_builder, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        return

    def test_vg_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.rvg_build_vector_genetics_reporter()
        self.assertIsNotNone(self.tmp_reporter)
        self.assertGreater(self.p_dict['Duration_Days'], 100_000)
        self.assertEqual(self.p_dict['File_Name_Suffix'], "")
        self.assertEqual(self.p_dict['Gender'], "VECTOR_FEMALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 1)
        self.assertEqual(self.p_dict['Report_Description'], "")
        self.assertEqual(self.p_dict['Start_Day'], 0)
        self.assertEqual(self.p_dict['Combine_Similar_Genomes'], 0)
        self.assertEqual(self.p_dict['Stratify_By'], "GENOME")

    def test_vg_custom_genome_stratification(self):
        self.assertIsNone(self.tmp_reporter)
        self.rvg_build_vector_genetics_reporter(
            combine_similar_genomes=1
        )
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Combine_Similar_Genomes'], 1)
        self.assertEqual(self.p_dict['Stratify_By'], "GENOME")

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
        self.assertEqual(self.p_dict['Duration_Days'], 12_345)
        self.assertEqual(self.p_dict['File_Name_Suffix'], "_silly")
        self.assertEqual(self.p_dict['Gender'], "VECTOR_MALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 0)
        self.assertEqual(self.p_dict['Report_Description'], "Does some stuff")
        self.assertEqual(self.p_dict['Species'], "Silly_Skeeter")
        self.assertEqual(self.p_dict['Combine_Similar_Genomes'], 1)
        self.assertEqual(self.p_dict['Specific_Genome_Combinations_For_Stratification'],
                         [["X"],["*"]])
        self.assertEqual(self.p_dict['Stratify_By'], "SPECIFIC_GENOME") # because of previous

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
        self.assertEqual(self.p_dict['Duration_Days'], 12_345)
        self.assertEqual(self.p_dict['File_Name_Suffix'], "_silly")
        self.assertEqual(self.p_dict['Gender'], "VECTOR_MALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 0)
        self.assertEqual(self.p_dict['Report_Description'], "Does some stuff")
        self.assertEqual(self.p_dict['Species'], "Silly_Skeeter")
        self.assertEqual(self.p_dict['Combine_Similar_Genomes'], 0)
        self.assertEqual(self.p_dict['Specific_Genome_Combinations_For_Stratification'],
                         [["X"],["*"]])
        self.assertEqual(self.p_dict['Stratify_By'], "SPECIFIC_GENOME") # because of previous

    def test_vg_custom_allele_stratification(self):
        self.rvg_build_vector_genetics_reporter(
            gender="VECTOR_BOTH_GENDERS",
            allele_combinations_for_stratification=[["X"],["Y"]]
        )
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Gender'],"VECTOR_BOTH_GENDERS")
        self.assertEqual(self.p_dict['Allele_Combinations_For_Stratification'], [["X"],["Y"]])
        self.assertEqual(self.p_dict["Stratify_By"], "ALLELE")
        pass

    def test_vg_custom_allele_frequency_stratification(self):
        self.rvg_build_vector_genetics_reporter(
            alleles_for_stratification=[]
        )
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Alleles_For_Stratification'], [])
        self.assertEqual(self.p_dict['Stratify_By'], "ALLELE_FREQ")
        pass

    # endregion

    # region malaria patient json report
    def mpj_build_malaria_patient_json_reporter(
            self
    ):
        def mpj_config_builder(params):
            return params
        import schema_path_file
        self.tmp_reporter = MalariaPatientJSONReport()
        self.tmp_reporter.config(mpj_config_builder, schema_path_file)
        return

    def test_malaria_patient_json_report_default(self):
        self.mpj_build_malaria_patient_json_reporter()
        self.assertIsNotNone(self.tmp_reporter)
        pass
    # endregion

    # region malaria summary report
    def msr_build_malaria_summary_report(
            self
            ,age_bins=None
            ,duration_days=None
            ,individual_property_filter=None
            ,infectiousness_bins=None
            ,max_number_reports=None
            ,parasitemia_bins=None
            ,pretty_format=None
            ,report_description=None
            ,reporting_interval=None
            ,start_day=None
            ,nodeset_nodelist=None
    ):
        def msr_config_builder(params):
            if age_bins is not None:
                params.Age_Bins = age_bins
            if duration_days is not None:
                params.Duration_Days = duration_days
            if individual_property_filter is not None:
                params.Individual_Property_Filter = individual_property_filter
            if infectiousness_bins is not None:
                params.Infectiousness_Bins = infectiousness_bins
            if max_number_reports is not None:
                params.Max_Number_Reports = max_number_reports
            if parasitemia_bins is not None:
                params.Parasitemia_Bins = parasitemia_bins
            if pretty_format is not None:
                params.Pretty_Format = pretty_format
            if report_description is not None:
                params.Report_Description = report_description
            if reporting_interval is not None:
                params.Reporting_Interval = reporting_interval
            if start_day is not None:
                params.Start_Day = start_day
            if nodeset_nodelist is not None:
                params.Nodeset_Config.NodeSetNodeList = nodeset_nodelist
            return params
        import schema_path_file
        self.tmp_reporter = MalariaSummaryReport()
        self.tmp_reporter.config(msr_config_builder, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        return

    def test_malaria_summary_report_default(self):
        self.msr_build_malaria_summary_report()
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'],
                         "NodeSetAll")
        self.assertGreater(self.p_dict['Duration_Days'], 100_000)
        self.assertEqual(self.p_dict['Age_Bins'], [])
        self.assertEqual(self.p_dict['Individual_Property_Filter'], "")
        self.assertEqual(self.p_dict['Infectiousness_Bins'], [])
        self.assertEqual(self.p_dict['Max_Number_Reports'],1)
        self.assertEqual(self.p_dict['Parasitemia_Bins'], [])
        self.assertEqual(self.p_dict['Pretty_Format'], 0)
        self.assertEqual(self.p_dict['Report_Description'], "")
        self.assertEqual(self.p_dict['Reporting_Interval'], 1_000_000)
        self.assertEqual(self.p_dict['Start_Day'],0)
        pass

    def test_malaria_summary_report_nodeset_all(self):
        self.msr_build_malaria_summary_report()
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'],
                         "NodeSetAll")
        pass

    @unittest.skip("See GH #43")
    def test_malaria_summary_report_nodelist(self):
        fib_ids = [1,2,3,5,8,13]
        self.msr_build_malaria_summary_report(
            nodeset_nodelist=fib_ids
        )
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Nodeset_Config']['Node_List'],
                         fib_ids)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'],
                         "NodeSetNodeList")

    def test_malaria_summary_report_custom1(self):
        self.msr_build_malaria_summary_report(
            age_bins=[1,2,5,15,25,45,65]
            ,duration_days=1234
        )
        self.assertEqual(self.p_dict['Age_Bins'],
                         [1,2,5,15,25,45,65])
        self.assertEqual(self.p_dict['Duration_Days'],
                         1234)

    def test_malaria_summary_report_custom2(self):
        self.msr_build_malaria_summary_report(
            individual_property_filter="FavoriteCola:RC"
            ,infectiousness_bins=[-15, -5, 0, 3, 5, 8]
            ,max_number_reports=63
            ,parasitemia_bins=[100, 500, 1500, 2345]
        )
        self.assertEqual(self.p_dict['Individual_Property_Filter'],
                         "FavoriteCola:RC")
        self.assertEqual(self.p_dict['Infectiousness_Bins'],
                         [-15, -5, 0, 3, 5, 8])
        self.assertEqual(self.p_dict['Max_Number_Reports'],
                         63)
        self.assertEqual(self.p_dict['Parasitemia_Bins'],
                         [100, 500, 1500, 2345])
        pass

    def test_malaria_summary_report_custom3(self):
        self.msr_build_malaria_summary_report(
            pretty_format=1
            ,report_description="A pretty good report for pretty good people"
            ,reporting_interval=15.5
            ,start_day=12
        )
        self.assertEqual(self.p_dict['Pretty_Format'],
                         1)
        self.assertEqual(self.p_dict['Report_Description'],
                         "A pretty good report for pretty good people")
        self.assertEqual(self.p_dict['Reporting_Interval'],
                         15.5)
        self.assertEqual(self.p_dict['Start_Day'],
                         12)
        pass

    # endregion

    # region filtered report 
    def build_filtered_report(
            self
            ,end_day = None
            ,has_interventions = None
            ,include_30_day_average = None
            ,node_ids_of_interest = None
            ,report_file_name = None
            ,start_day = None
    ):
        def filtered_config_builder(params):
            if end_day is not None:
                params.End_Day = end_day
            if has_interventions is not None:
                params.Has_Interventions = has_interventions
            if include_30_day_average is not None:
                params.Include_30Day_Avg_Infection_Duration = include_30_day_average
            if node_ids_of_interest is not None:
                params.Node_IDs_Of_Interest = node_ids_of_interest
            if report_file_name is not None:
                params.Report_File_Name = report_file_name
            if start_day is not None:
                params.Start_Day = start_day
            return params
        
        import schema_path_file
        self.tmp_reporter = FilteredMalariaReport()
        self.tmp_reporter.config(filtered_config_builder, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        return

    def test_filtered_report_default(self):
        self.build_filtered_report()
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['End_Day'], 3.40282e+38)
        self.assertEqual(self.p_dict['Has_Interventions'], [])
        self.assertEqual(self.p_dict['Include_30Day_Avg_Infection_Duration'], 1)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], []) # Report_File_Name
        self.assertEqual(self.p_dict['Report_File_Name'], 'ReportMalariaFiltered.json')
        self.assertEqual(self.p_dict['Start_Day'], 0)

    def test_filtered_report_custom(self):
        end_day = 10
        include_30_day = 0
        ids_of_interest = [1, 2]
        file_name = "FilteredStuff.json"
        start_day = 5

        self.build_filtered_report(
            end_day = end_day
            ,include_30_day_average = include_30_day
            ,node_ids_of_interest = ids_of_interest
            ,report_file_name = file_name
            ,start_day = start_day
        )

        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['End_Day'], end_day)
        self.assertEqual(self.p_dict['Include_30Day_Avg_Infection_Duration'], include_30_day)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], ids_of_interest) # Report_File_Name
        self.assertEqual(self.p_dict['Report_File_Name'], file_name)
        self.assertEqual(self.p_dict['Start_Day'], start_day)

    # end region

    # start region ReportEventCounter

    def build_report_event_counter(self = None,
                                    duration = None,
                                    trigger_list = None,
                                    start_day = None,
                                    nodeset_list = None):
        def report_counter_config_builder(params):
            if duration is not None:
                params.Duration_Days = duration
            if trigger_list is not None:
                params.Event_Trigger_List = trigger_list
            if start_day is not None:
                params.Start_Day = start_day
            if nodeset_list is not None:
                params.Nodeset_Config.NodeSetNodeList = nodeset_list
            return params
        
        import schema_path_file
        self.tmp_reporter = ReportEventCounter()
        self.tmp_reporter.config(report_counter_config_builder, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        return

    def test_report_counter_default(self):
        self.build_report_event_counter()
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'],
                         "NodeSetAll")
        self.assertEqual(self.p_dict['Duration_Days'], 3.40282e+38)
        self.assertEqual(self.p_dict['Event_Trigger_List'], [])
        self.assertEqual(self.p_dict['Start_Day'], 0)

    def test_report_counter_custom(self):
        duration = 17
        trigger_list = ["STINewInfection", "ExitedRelationship"]
        start_day = 5

        self.build_report_event_counter(
            start_day = start_day
            ,duration = duration
            ,trigger_list = trigger_list
        )

        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['Duration_Days'], duration)
        self.assertEqual(self.p_dict['Event_Trigger_List'], trigger_list)

    # end region
    
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
