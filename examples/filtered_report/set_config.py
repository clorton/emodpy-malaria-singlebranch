def set_config(config):
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

    return config
