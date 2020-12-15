import unittest

class MalariaTestImports(unittest.TestCase):
    def setUp(self) -> None:
        self.expected_items = None
        self.found_items = None
        pass

    def verify_expected_items_present(self, namespace):
        self.found_items = dir(namespace)
        for item in self.expected_items:
            self.assertIn(
                item,
                self.found_items
            )

    def tearDown(self) -> None:
        pass

    def test_requirements(self):
        import emod_api
        import emodpy_malaria
        import emodpy
        # Testing that we can import all requirements
        checks = [dir(package) for package in [emod_api, emodpy_malaria, emodpy]]
        for package in checks:
            self.assertIn('__package__', package)

    def test_intervention_bednet(self):
        from emodpy_malaria import interventions
        from emodpy_malaria.interventions import bednet

        self.expected_items = [
            "Bednet"
        ]
        self.verify_expected_items_present(namespace=bednet)

    def test_intervention_sugartrap(self):
        from emodpy_malaria.interventions import sugartrap
        self.expected_items = [
            "SugarTrap"
        ]
        self.verify_expected_items_present(namespace=sugartrap)

    def test_demographics_imports_emodapi(self):
        import emodpy_malaria.demographics.MalariaDemographics as Demographics

        self.expected_items = [
            "from_pop_csv", "fromBasicNode"
        ]
        self.verify_expected_items_present(namespace=Demographics)
