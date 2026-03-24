import unittest

from civicsignal.connectors.models import AgendaItemRecord, MeetingRecord
from civicsignal.signal_engine import SignalGenerationInput, generate_signals_for_agenda_item
from civicsignal.signal_models import SummarySource, SignalCategory, SignalConfidence, SignalRecord, validate_signal


class SignalSchemaTests(unittest.TestCase):
    def _meeting(self) -> MeetingRecord:
        return MeetingRecord(
            external_meeting_id="meeting-1",
            meeting_date="2026-03-01",
            meeting_title="City Council Regular Meeting",
            meeting_body="City Council",
            agenda_url="https://example.com/agenda",
            minutes_url=None,
            video_url=None,
            source_url="https://example.com/meeting",
        )

    def _agenda_item(self, title: str, summary: str) -> AgendaItemRecord:
        return AgendaItemRecord(
            external_agenda_item_id="item-1",
            item_number="1",
            title=title,
            summary=summary,
            action=None,
            vote_result=None,
        )

    def test_validate_rejects_invalid_category(self) -> None:
        signal = SignalRecord(
            signal_id="s1",
            city="fullerton",
            meeting_body="City Council",
            meeting_date="2026-03-01",
            agenda_item_number="1",
            signal_category=SignalCategory.POLICY_ORDINANCES,
            signal_type="policy",
            title="Policy update",
            summary="Policy update summary",
            summary_source=SummarySource.ITEM_DESCRIPTION,
            content_available=True,
            confidence=SignalConfidence.MEDIUM,
            project_entity_id=None,
            supporting_documents=["https://example.com/doc.pdf"],
            source_urls=["https://example.com/meeting"],
        )
        validate_signal(signal)

        invalid_signal = signal.__class__(
            signal_id=signal.signal_id,
            city=signal.city,
            meeting_body=signal.meeting_body,
            meeting_date=signal.meeting_date,
            agenda_item_number=signal.agenda_item_number,
            signal_category="Unknown",  # type: ignore[arg-type]
            signal_type=signal.signal_type,
            title=signal.title,
            summary=signal.summary,
            summary_source=signal.summary_source,
            content_available=signal.content_available,
            confidence=signal.confidence,
            project_entity_id=signal.project_entity_id,
            supporting_documents=signal.supporting_documents,
            source_urls=signal.source_urls,
        )
        with self.assertRaises(ValueError):
            validate_signal(invalid_signal)

    def test_validate_rejects_invalid_confidence(self) -> None:
        signal = SignalRecord(
            signal_id="s1",
            city="fullerton",
            meeting_body="City Council",
            meeting_date="2026-03-01",
            agenda_item_number="1",
            signal_category=SignalCategory.POLICY_ORDINANCES,
            signal_type="policy",
            title="Policy update",
            summary="Policy update summary",
            summary_source=SummarySource.ITEM_DESCRIPTION,
            content_available=True,
            confidence=SignalConfidence.MEDIUM,
            project_entity_id=None,
            supporting_documents=["https://example.com/doc.pdf"],
            source_urls=["https://example.com/meeting"],
        )
        invalid_signal = signal.__class__(
            signal_id=signal.signal_id,
            city=signal.city,
            meeting_body=signal.meeting_body,
            meeting_date=signal.meeting_date,
            agenda_item_number=signal.agenda_item_number,
            signal_category=signal.signal_category,
            signal_type=signal.signal_type,
            title=signal.title,
            summary=signal.summary,
            summary_source=signal.summary_source,
            content_available=signal.content_available,
            confidence="Unknown",  # type: ignore[arg-type]
            project_entity_id=signal.project_entity_id,
            supporting_documents=signal.supporting_documents,
            source_urls=signal.source_urls,
        )
        with self.assertRaises(ValueError):
            validate_signal(invalid_signal)

    def test_multiple_signals_generated_from_one_agenda_item(self) -> None:
        agenda_item = self._agenda_item(
            title="Housing development and zoning amendment",
            summary="Residential development project with zoning changes.",
        )
        signals = generate_signals_for_agenda_item(
            SignalGenerationInput(
                city="fullerton",
                meeting=self._meeting(),
                agenda_item=agenda_item,
                supporting_documents=["https://example.com/doc.pdf"],
            )
        )

        self.assertGreaterEqual(len(signals), 1)
        categories = {signal.signal_category for signal in signals}
        self.assertTrue(
            SignalCategory.HOUSING_DEVELOPMENT in categories
            or SignalCategory.ZONING_LAND_USE in categories
        )
        self.assertTrue(all(signal.confidence in {SignalConfidence.HIGH, SignalConfidence.MEDIUM, SignalConfidence.LOW} for signal in signals))

    def test_title_only_fallback_is_explicit_and_low_confidence(self) -> None:
        agenda_item = self._agenda_item(
            title="Public Hearing",
            summary="Public Hearing",
        )
        signals = generate_signals_for_agenda_item(
            SignalGenerationInput(
                city="fullerton",
                meeting=self._meeting(),
                agenda_item=agenda_item,
                supporting_documents=["https://example.com/doc.pdf"],
            )
        )

        self.assertGreaterEqual(len(signals), 1)
        self.assertTrue(all(signal.summary and signal.summary.startswith("Title-only:") for signal in signals))
        self.assertTrue(all(signal.summary_source == SummarySource.TITLE_ONLY for signal in signals))
        self.assertTrue(all(signal.confidence == SignalConfidence.LOW for signal in signals))

    def test_taxonomy_limits_over_classification_for_broad_packet_text(self) -> None:
        agenda_item = self._agenda_item(
            title="Traffic impact fee program update",
            summary="",
        )
        packet_text = (
            "This section references fee schedules, contract approval, ordinance waivers, "
            "public safety, parks, utilities, and policy notes across the meeting packet."
        )

        signals = generate_signals_for_agenda_item(
            SignalGenerationInput(
                city="fullerton",
                meeting=self._meeting(),
                agenda_item=agenda_item,
                supporting_documents=["https://example.com/doc.pdf"],
                agenda_packet_text=packet_text,
            )
        )

        self.assertGreaterEqual(len(signals), 1)
        self.assertLessEqual(len(signals), 2)

    def test_procedural_items_map_to_general_update(self) -> None:
        agenda_item = self._agenda_item(
            title="Procedural Waiver: Waive the full reading of all ordinances and resolutions",
            summary="",
        )

        signals = generate_signals_for_agenda_item(
            SignalGenerationInput(
                city="fullerton",
                meeting=self._meeting(),
                agenda_item=agenda_item,
                supporting_documents=["https://example.com/doc.pdf"],
                agenda_packet_text="Routine procedural language for meeting setup.",
            )
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].signal_type, "general_update")


if __name__ == "__main__":
    unittest.main()
