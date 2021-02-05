def set_config( config ):
    config.parameters.Acquisition_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Acquisition_Blocking_Immunity_Duration_Before_Decay = 0
    config.parameters.Infectious_Period_Constant = 0
    config.parameters.Enable_Demographics_Birth = 1
    config.parameters.Enable_Demographics_Reporting = 0
    config.parameters.Enable_Immune_Decay = 0
    config.parameters.Migration_Model = "NO_MIGRATION"
    config.parameters.Mortality_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Mortality_Blocking_Immunity_Duration_Before_Decay = 270
    config.parameters.Enable_Demographics_Risk = 1
    config.parameters.Enable_Maternal_Infection_Transmission = 0
    config.parameters.Enable_Natural_Mortality = 1
    
    config.parameters.x_Base_Population =0.5
    config.parameters.Enable_Disease_Mortality =0
    config.parameters.Max_Individual_Infections = 10
    config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION" # implicit

    # MIGRATION
    #config.parameters.Migration_Model = "FIXED_RATE_MIGRATION"
    config.parameters.Migration_Pattern = "SINGLE_ROUND_TRIPS"

    """
    config.parameters.x_Local_Migration = 0.03
    config.parameters.Local_Migration_Roundtrip_Duration = 2  # mean of exponential days-at-destination distribution
    config.parameters.Local_Migration_Roundtrip_Probability = 1  # fraction that return
    """
    #config.parameters.Enable_Regional_Migration = 0
    config.parameters.x_Regional_Migration = 0.03
    config.parameters.Regional_Migration_Roundtrip_Duration = 2
    #config.parameters.Regional_Migration_Roundtrip_Probability = 1
    config.parameters.Enable_Migration_Heterogeneity = 1

    return config
