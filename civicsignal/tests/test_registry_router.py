import unittest

from civicsignal.connectors.errors import UnsupportedPlatformError
from civicsignal.connectors.models import PlatformType
from civicsignal.connectors.registry import ConnectorRegistry


class ConnectorRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ConnectorRegistry.with_defaults()

    def test_resolves_all_supported_platforms(self) -> None:
        for platform in PlatformType:
            connector = self.registry.resolve(platform)
            self.assertEqual(connector.platform_name, platform.value)

    def test_resolves_platform_from_string(self) -> None:
        connector = self.registry.resolve("legistar")
        self.assertEqual(connector.platform_name, "legistar")

    def test_unsupported_platform_raises_deterministic_error(self) -> None:
        with self.assertRaises(UnsupportedPlatformError) as context:
            self.registry.resolve("unknown-platform")

        error = context.exception
        self.assertEqual(error.code, "unsupported_platform")
        self.assertIn("unknown-platform", str(error))


if __name__ == "__main__":
    unittest.main()
