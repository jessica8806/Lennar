import tempfile
import unittest
from pathlib import Path

from civicsignal.change_detection import detect_changes, document_hash, meeting_hash
from civicsignal.change_runner import run_change_detection
from civicsignal.connectors.models import DocumentRecord, DocumentType, MeetingRecord


class ChangeDetectionTests(unittest.TestCase):
    def test_meeting_hash_is_canonicalized(self) -> None:
        m1 = MeetingRecord(
            external_meeting_id="m1",
            meeting_date="2026-03-01",
            meeting_title="City Council Meeting",
            meeting_body="City Council",
            agenda_url="https://example.com/agenda",
            minutes_url=None,
            video_url=None,
            source_url="https://example.com/agenda",
        )
        m2 = MeetingRecord(
            external_meeting_id="m1",
            meeting_date="2026-03-01",
            meeting_title="  CITY   COUNCIL   MEETING ",
            meeting_body="city council",
            agenda_url="https://example.com/agenda",
            minutes_url=None,
            video_url=None,
            source_url="https://example.com/agenda",
        )
        self.assertEqual(meeting_hash(m1), meeting_hash(m2))

    def test_detect_changes_new_changed_unchanged(self) -> None:
        previous = {"a": "h1", "b": "h2"}
        current = {"a": "h1", "b": "h3", "c": "h4"}
        result = detect_changes(previous, current, entity_type="meeting")

        self.assertEqual(result.new_count, 1)
        self.assertEqual(result.changed_count, 1)
        self.assertEqual(result.unchanged_count, 1)

    def test_document_hash_changes_when_size_changes(self) -> None:
        d1 = DocumentRecord(
            external_document_id="d1",
            document_type=DocumentType.AGENDA,
            file_url="https://example.com/a.pdf",
            file_name="a.pdf",
            file_size_bytes=100,
        )
        d2 = DocumentRecord(
            external_document_id="d1",
            document_type=DocumentType.AGENDA,
            file_url="https://example.com/a.pdf",
            file_name="a.pdf",
            file_size_bytes=101,
        )
        self.assertNotEqual(document_hash(d1), document_hash(d2))

    def test_two_pass_runner_produces_unchanged_second_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "change-state.json"

            first = run_change_detection(
                start_date="2026-03-01",
                end_date="2026-03-03",
                city_id="fullerton",
                live_fetch=False,
                state_path=str(state_file),
                persist=True,
            )
            second = run_change_detection(
                start_date="2026-03-01",
                end_date="2026-03-03",
                city_id="fullerton",
                live_fetch=False,
                state_path=str(state_file),
                persist=True,
            )

            self.assertEqual(len(first), 1)
            self.assertEqual(len(second), 1)
            self.assertGreater(first[0].meetings_new, 0)
            self.assertEqual(second[0].meetings_new, 0)
            self.assertGreater(second[0].meetings_unchanged, 0)


if __name__ == "__main__":
    unittest.main()
