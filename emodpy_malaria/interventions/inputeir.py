from emod_api import schema_to_class as s2c
from emod_api.interventions import utils


def new_intervention(
        campaign,
        monthly_eir: list,
        age_dependence: str
):
    """
        Create the InputEIR intervention itself that will be nestled inside an event coordinator.

        Args:
            campaign:  Passed in campaign (from emod_api.campaign)
            monthly_eir: An array of 12 elements that contain an entomological inoculation rate (EIR) for each month;
                Each value should be between 0 and 1000
            age_dependence: Determines how InputEIR depends on the age of the target. Options are "OFF", "LINEAR",
                "SURFACE_AREA_DEPENDENT"

        Returns:
            InputEIR intervention
    """
    intervention = s2c.get_class_with_defaults("InputEIR", campaign.schema_path)
    if len(monthly_eir) != 12:
        raise ValueError(f"monthly_eir array needs to have 1 element per month (i.e., 12).")
    if any(i > 1000 for i in monthly_eir):
        raise ValueError(f"All monthly_eir array elements need to be <= 1000.")
    if any(i < 0 for i in monthly_eir):
        raise ValueError(f"All monthly_eir array elements need to be positive.")

    intervention.Monthly_EIR = monthly_eir
    intervention.Age_Dependence = age_dependence
    return intervention


def InputEIR(
        campaign,
        monthly_eir: list,
        start_day: int = 1,
        node_ids: list = None,
        age_dependence: str = "OFF"
):
    """
        Create a full CampaignEvent that distributes InputEIR to a population.

        Args:
            campaign: Passed in campaign (from emod_api.campaign)
            monthly_eir: An array of 12 elements that contain an entomological inoculation rate (EIR) for each month;
                Each value should be between 0 and 1000
            start_day: The day on which the monthly_eir cycle starts
            node_ids: Nodes to which this intervention is applied
            age_dependence: Determines how InputEIR depends on the age of the target. Options are "OFF", "LINEAR",
                "SURFACE_AREA_DEPENDENT"

        Returns:
            Campaign event to be added to campaign (from emod_api.camapign)
    """
    # First, get the objects
    event = s2c.get_class_with_defaults("CampaignEvent", campaign.schema_path)
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", campaign.schema_path)
    if coordinator is None:
        print("s2c.get_class_with_defaults returned None. Maybe no schema.json was provided.")
        return ""

    intervention = new_intervention(campaign, monthly_eir, age_dependence)
    coordinator.Intervention_Config = intervention
    coordinator.pop("Node_Property_Restrictions")

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    event.Start_Day = float(start_day)
    event.Nodeset_Config = utils.do_nodes(campaign.schema_path, node_ids)

    return event


def new_intervention_as_file(campaign, start_day: int, monthly_eir: list, filename: str = None):
    """
        Create an InputEIR intervention as its own file.

        Args:
            campaign: Passed in campaign (from emod_api.campaign)
            start_day: The day on which the monthly_eir cycle starts
            monthly_eir: An array of 12 elements that contain an entomological inoculation rate (EIR) for each month;
                Each value should be between 0 and 1000
            filename: filename used for the file created

        Returns:
            The filename of the file created
    """
    campaign.add(InputEIR(campaign, monthly_eir, start_day), first=True)
    if filename is None:
        filename = "InputEIR.json"
    campaign.save(filename)
    return filename
