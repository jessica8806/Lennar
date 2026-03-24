from __future__ import annotations

from dataclasses import dataclass

from .connectors.models import PlatformType


TRACKED_BODIES = ["City Council", "Planning Commission"]


@dataclass(frozen=True)
class CityConfig:
    city_id: str
    city_name: str
    platform_type: PlatformType
    discovery_url: str
    bodies: list[str]


def phase1_city_registry() -> list[CityConfig]:
    return [
        CityConfig("irvine", "Irvine", PlatformType.GRANICUS, "https://irvine.granicus.com/ViewPublisher.php", TRACKED_BODIES),
        CityConfig("anaheim", "Anaheim", PlatformType.GRANICUS, "https://anaheim.granicus.com/ViewPublisher.php", TRACKED_BODIES),
        CityConfig("santa-ana", "Santa Ana", PlatformType.LASERFICHE, "https://publicdocs.santa-ana.org/WebLink", TRACKED_BODIES),
        CityConfig("huntington-beach", "Huntington Beach", PlatformType.LEGISTAR, "https://huntingtonbeach.legistar.com/Calendar.aspx", TRACKED_BODIES),
        CityConfig("newport-beach", "Newport Beach", PlatformType.LEGISTAR, "https://newportbeach.legistar.com/Calendar.aspx", TRACKED_BODIES),
        CityConfig("costa-mesa", "Costa Mesa", PlatformType.LEGISTAR, "https://costamesa.legistar.com/Calendar.aspx", TRACKED_BODIES),
        CityConfig("fullerton", "Fullerton", PlatformType.LEGISTAR, "https://fullerton.legistar.com/Calendar.aspx", TRACKED_BODIES),
        CityConfig("garden-grove", "Garden Grove", PlatformType.NOVUSAGENDA, "https://gardengrove.novusagenda.com/AgendaPublic", TRACKED_BODIES),
        CityConfig("mission-viejo", "Mission Viejo", PlatformType.ONBASE, "https://dms.cityofmissionviejo.org/OnBaseAgendaOnline", TRACKED_BODIES),
        CityConfig("laguna-niguel", "Laguna Niguel", PlatformType.CIVICPLUS, "https://www.cityoflagunaniguel.org/AgendaCenter", TRACKED_BODIES),
    ]
