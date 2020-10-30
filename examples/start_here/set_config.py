def set_config( config, tmp_loc = [], rate= 1.0, infectivity = 1.0 ):
    config.parameters.Simulation_Type = "TBHIV_SIM" 
    config.parameters.Acquisition_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Acquisition_Blocking_Immunity_Duration_Before_Decay = 0
    config.parameters.Incubation_Period_Exponential = 233.33
    config.parameters.Infectious_Period_Constant = 0
    config.parameters.Base_Infectivity_Constant = 0.0219
    config.parameters.Base_Mortality = 0
    config.parameters.Enable_Birth = 1
    config.parameters.Enable_Coinfection = 1
    config.parameters.Enable_Demographics_Birth = 1
    config.parameters.Enable_Demographics_Reporting = 0
    config.parameters.Enable_Disease_Mortality = 1
    config.parameters.Enable_Immune_Decay = 0
    #config.parameters.Load_Balance_Filename = ""
    config.parameters.Migration_Model = "NO_MIGRATION"
    config.parameters.Mortality_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Mortality_Blocking_Immunity_Duration_Before_Decay = 270
    config.parameters.Mortality_Time_Course = "DAILY_MORTALITY"
    config.parameters.Run_Number = 99
    #config.parameters.Sample_Rate_0_18mo = 1
    #config.parameters.Sample_Rate_10_14 = 1
    #config.parameters.Sample_Rate_15_19 = 1
    #config.parameters.Sample_Rate_18mo_4yr = 1
    #config.parameters.Sample_Rate_20_Plus = 1
    #config.parameters.Sample_Rate_5_9 = 1
    #config.parameters.Sample_Rate_Birth = 1
    #config.parameters.Serialization_Time_Steps = list()
    config.parameters.Simulation_Duration = 60
    config.parameters.Simulation_Timestep = 30
    #config.parameters.Start_Time = 0
    config.parameters.TB_Active_Cure_Rate = 2.40e-4
    config.parameters.TB_Active_Mortality_Rate = 4.45e-4
    config.parameters.TB_Extrapulmonary_Fraction_Adult = 0.1
    config.parameters.TB_Extrapulmonary_Fraction_Child = 0.4
    config.parameters.TB_Extrapulmonary_Mortality_Multiplier = 0.15
    config.parameters.TB_Fast_Progressor_Fraction_Type = "AGE"
    config.parameters.TB_Fast_Progressor_Fraction_Adult = 0.10
    config.parameters.TB_Fast_Progressor_Fraction_Child = 0.03
    config.parameters.TB_Fast_Progressor_Rate = 0.006
    config.parameters.TB_Immune_Loss_Fraction = 0
    config.parameters.TB_Inactivation_Rate = 1e-9
    config.parameters.TB_Latent_Cure_Rate = 1.0e-09
    config.parameters.TB_Slow_Progressor_Rate = 2.8e-5
    config.parameters.TB_Smear_Negative_Infectivity_Multiplier = 0.20
    config.parameters.TB_Active_Presymptomatic_Infectivity_Multiplier = 0.0011
    config.parameters.TB_Smear_Negative_Mortality_Multiplier = 0.30
    config.parameters.TB_Smear_Positive_Fraction_Adult = 0.65
    config.parameters.TB_Smear_Positive_Fraction_Child = 0.25
    config.parameters.Transmission_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Transmission_Blocking_Immunity_Duration_Before_Decay = 0
    config.parameters.TB_MDR_Fitness_Multiplier = 0.5
    config.parameters.TB_Presymptomatic_Cure_Rate = 0
    config.parameters.TB_Presymptomatic_Rate = 0.006
    config.parameters.TB_Relapsed_to_Active_Rate = 0.012
    config.parameters.Acute_Duration_In_Months = 1
    config.parameters.CD4_Time_Step = 365
    config.parameters.Enable_Coinfection_Mortality = 1
    config.parameters.CD4_Num_Steps = 20
    config.parameters.TB_CD4_Activation_Vector = [5e-4, 5e-4, 2.6e-4, 1.7e-4, 1.4e-4, 2.8e-5, 2.8e-5 ]
    config.parameters.CD4_Strata_Activation = [ 1, 100, 200, 300, 400, 500, 2000]
    config.parameters.TB_CD4_Infectiousness = [ 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 ]
    config.parameters.TB_CD4_Susceptibility = [ 1, 1, 1, 1, 1,1,1 ]
    config.parameters.TB_CD4_Strata_Infectiousness_Susceptibility = [ 1.0000000000000001e-09, 250, 300, 350, 500, 2000, 20000 ]
    config.parameters.TB_Active_Period_Distribution = "EXPONENTIAL_DISTRIBUTION"
    config.parameters.TB_Active_Period_Gaussian_Std_Dev = 10
    config.parameters.TB_Drug_Efficacy_Multiplier_Failed = 1
    config.parameters.TB_Drug_Efficacy_Multiplier_Relapsed = 1
    config.parameters.TB_Drug_Efficacy_Multiplier_MDR = 1
    config.parameters.ART_Reactivation_Factor = 1.0
    config.parameters.TB_Enable_Exogenous = 1
    config.parameters.CoInfection_Mortality_Rate_Off_ART = 3.0e-4
    config.parameters.CoInfection_Mortality_Rate_On_ART = 1.0e-4
    config.parameters.TB_CD4_Primary_Progression = [1,1,1,1,1,1,1]
    config.parameters.CD4_At_Death_LogLogistic_Scale = 2.96
    config.parameters.Birth_Rate_Time_Dependence = "NONE"
    config.parameters.ART_CD4_at_Initiation_Saturating_Reduction_in_Mortality = 1.0
    config.parameters.CD4_At_Death_LogLogistic_Heterogeneity = 0.7
    config.parameters.CD4_Post_Infection_Weibull_Scale = 560.4319099584783
    config.parameters.CD4_Post_Infection_Weibull_Heterogeneity = 0.2756
    config.parameters.Days_Between_Symptomatic_And_Death_Weibull_Heterogeneity = 0.5
    config.parameters.Days_Between_Symptomatic_And_Death_Weibull_Scale = 618.34
    config.parameters.Enable_Default_Reporting = 1
    config.parameters.Enable_Demographics_Builtin = 0
    config.parameters.HIV_Adult_Survival_Scale_Parameter_Intercept = 21.182
    config.parameters.HIV_Adult_Survival_Scale_Parameter_Slope = -0.2717
    config.parameters.HIV_Adult_Survival_Shape_Parameter = 2.0
    config.parameters.HIV_Age_Max_for_Adult_Age_Dependent_Survival = 75
    config.parameters.HIV_Age_Max_for_Child_Survival_Function = 15
    config.parameters.HIV_Child_Survival_Rapid_Progressor_Fraction = 0.57
    config.parameters.HIV_Child_Survival_Rapid_Progressor_Rate = 1.52
    config.parameters.HIV_Child_Survival_Slow_Progressor_Scale = 16.0
    config.parameters.HIV_Child_Survival_Slow_Progressor_Shape = 2.7
    config.parameters.Enable_Demographics_Risk = 1
    config.parameters.Enable_Maternal_Infection_Transmission = 0
    config.parameters.Enable_Natural_Mortality = 1

    return config
