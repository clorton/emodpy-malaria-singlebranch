from dataclasses import dataclass, field

from emodpy.reporters.base import BuiltInReporter
from emod_api import schema_to_class as s2c


@dataclass
class ReportVectorGenetics(BuiltInReporter):
    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorGenetics" # OK to hardcode? config["class"]
        rvg_params = s2c.get_class_with_defaults( "ReportVectorGenetics", manifest.schema_file ) 
        rvg_params = config_builder( rvg_params )
        rvg_params.finalize()
        rvg_params.pop( "Sim_Types" )  #  maybe that should be in finalize
        self.parameters.update( dict( rvg_params ) )


@dataclass
class ReportVectorStats(BuiltInReporter):
    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorStats" # OK to hardcode? config["class"]
        rvg_params = s2c.get_class_with_defaults( "ReportVectorStats", manifest.schema_file )
        rvg_params = config_builder( rvg_params )
        rvg_params.finalize()
        rvg_params.pop( "Sim_Types" )  #  maybe that should be in finalize
        self.parameters.update( dict( rvg_params ) )
        

@dataclass
class MalariaSummaryReport(BuiltInReporter):
    def config(self, config_builder, manifest):
        self.class_name ="MalariaSummaryReport"
        report_params = s2c.get_class_with_defaults( "MalariaSummaryReport", manifest.schema_file ) 
        report_params = config_builder( report_params )
        report_params.finalize()
        report_params.pop( "Sim_Types" )  #  maybe that should be in finalize
        self.parameters.update( dict( report_params ) )


@dataclass
class MalariaPatientJSONReport(BuiltInReporter):
    def config(self, config_builder, manifest):
        self.class_name = "MalariaPatientJSONReport"
        report_params = s2c.get_class_with_defaults( "MalariaPatientJSONReport", manifest.schema_file ) 
        report_params = config_builder( report_params )
        report_params.finalize()
        report_params.pop( "Sim_Types" )  #  maybe that should be in finalize
        self.parameters.update( dict( report_params ) )


@dataclass
class MalariaTransmissionReport(BuiltInReporter):
    def config(self, config_builder, manifest):
        self.class_name = "MalariaTransmissionReport"
        report_params = s2c.get_class_with_defaults( "MalariaTransmissionReport", manifest.schema_file ) 
        report_params = config_builder( report_params )
        report_params.finalize()
        report_params.pop( "Sim_Types" )  #  maybe that should be in finalize
        self.parameters.update( dict( report_params ) )

@dataclass
class FilteredMalariaReport(BuiltInReporter):
    def config(self, config_builder, manifest):
        self.class_name = "ReportMalariaFiltered"
        report_params = s2c.get_class_with_defaults( "ReportMalariaFiltered", manifest.schema_file ) 
        report_params = config_builder( report_params )
        report_params.finalize()
        report_params.pop( "Sim_Types" )  #  maybe that should be in finalize
        self.parameters.update( dict( report_params ) )

