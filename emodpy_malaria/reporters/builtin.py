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
    class_name: str = field(default="MalariaSummaryReport")


@dataclass
class MalariaPatientJSONReport(BuiltInReporter):
    class_name: str = field(default="MalariaPatientJSONReport")
