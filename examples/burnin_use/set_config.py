import manifest

def set_config(config):
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
    config.parameters.Enable_Natural_Mortality = 1
    config.parameters.Serialized_Population_Reading_Type = "READ"
    config.parameters.Serialized_Population_Path = manifest.assets_input_dir
    config.parameters.Serialized_Population_Filenames = [ "state-00365.dtk" ]

    return config
