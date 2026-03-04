from __future__ import annotations

import time
from urllib.parse import parse_qs, urlparse, urlunparse

from .fetch import fetch_html_with_fallback
from .interface import PlatformConnector
from .models import (
    AgendaItemRecord,
    ConnectorRequest,
    DiscoverMeetingsResult,
    DocumentRecord,
    DocumentType,
    DryRunMetrics,
    ExtractDocumentsResult,
    MeetingRecord,
    ParseAgendaResult,
)
from .parsers import parse_granicus_meetings, parse_legistar_agenda_items, parse_legistar_meetings


GRANICUS_SAMPLE_HTML = """
<table id=\"meetings\">
    <tr data-body=\"City Council\">
        <td class=\"date\">{start_date}</td>
        <td class=\"title\">City Council Regular Meeting</td>
        <td><a class=\"agenda\" href=\"{base}/AgendaViewer.php?view_id=1\">Agenda</a></td>
        <td><a class=\"minutes\" href=\"{base}/MinutesViewer.php?view_id=1\">Minutes</a></td>
        <td><a class=\"video\" href=\"{base}/player/clip/1\">Video</a></td>
    </tr>
    <tr data-body=\"Planning Commission\">
        <td class=\"date\">{end_date}</td>
        <td class=\"title\">Planning Commission Regular Meeting</td>
        <td><a class=\"agenda\" href=\"{base}/AgendaViewer.php?view_id=2\">Agenda</a></td>
        <td><a class=\"minutes\" href=\"{base}/MinutesViewer.php?view_id=2\">Minutes</a></td>
        <td><a class=\"video\" href=\"{base}/player/clip/2\">Video</a></td>
    </tr>
</table>
"""


LEGISTAR_SAMPLE_HTML = """
<table id=\"ctl00_ContentPlaceHolder1_gridCalendar_ctl00\">
    <tr data-meeting-body=\"City Council\">
        <td class=\"meeting-date\">{start_date}</td>
        <td class=\"meeting-title\">City Council Meeting</td>
        <td><a class=\"agenda-link\" href=\"{base}/MeetingDetail.aspx?ID=612345&GUID=stub-city-council\">Agenda</a></td>
        <td><a class=\"minutes-link\" href=\"{base}/View.ashx?M=M&ID=612345&GUID=stub-city-council\">Minutes</a></td>
        <td><a class=\"video-link\" href=\"{base}/video.aspx?Mode=Granicus&ID1=612345\">Video</a></td>
    </tr>
    <tr data-meeting-body=\"Planning Commission\">
        <td class=\"meeting-date\">{end_date}</td>
        <td class=\"meeting-title\">Planning Commission Meeting</td>
        <td><a class=\"agenda-link\" href=\"{base}/MeetingDetail.aspx?ID=612346&GUID=stub-planning\">Agenda</a></td>
        <td><a class=\"minutes-link\" href=\"{base}/View.ashx?M=M&ID=612346&GUID=stub-planning\">Minutes</a></td>
        <td><a class=\"video-link\" href=\"{base}/video.aspx?Mode=Granicus&ID1=612346\">Video</a></td>
    </tr>
</table>
"""


def _matches_requested_body(meeting_body: str, requested_bodies: list[str]) -> bool:
    normalized_meeting = meeting_body.lower()
    for requested in requested_bodies:
        if requested.lower() in normalized_meeting:
            return True
    return False


def _extract_legistar_meeting_id(source_url: str) -> int | None:
    parsed = urlparse(source_url)
    meeting_id = (parse_qs(parsed.query).get("ID") or [None])[0]
    if not meeting_id or not meeting_id.isdigit():
        return None
    return int(meeting_id)


def _looks_like_stub_meeting(source_url: str) -> bool:
    meeting_id = _extract_legistar_meeting_id(source_url)
    if meeting_id is None:
        return True
    return meeting_id < 1000


def _build_legistar_fallback_agenda_html(meeting: MeetingRecord) -> str:
    rows: list[str] = []
    for index in range(1, 13):
        rows.append(
            """
            <tr id=\"ctl00_ContentPlaceHolder1_gridAgenda_ctl00__{index}\">
                <td>{item_number}</td>
                <td><a id=\"ctl00_ContentPlaceHolder1_gridAgenda_ctl00_ctl{row}_hypItemLink\">{title}</a></td>
                <td>Discussion item {index} for {body}</td>
            </tr>
            """.format(
                index=index,
                item_number=index,
                row=4 + index,
                title=f"{meeting.meeting_body} Agenda Item {index}",
                body=meeting.meeting_body,
            )
        )

    return "<table id=\"ctl00_ContentPlaceHolder1_gridAgenda_ctl00\">" + "".join(rows) + "</table>"


class StubConnector(PlatformConnector):
    platform_name = "stub"

    def discover_meetings(self, request: ConnectorRequest) -> DiscoverMeetingsResult:
        start = time.perf_counter()
        meetings = [
            MeetingRecord(
                external_meeting_id=f"{request.city_id}-{body.lower().replace(' ', '-')}-{request.date_range.start_date}",
                meeting_date=request.date_range.start_date,
                meeting_title=f"{body} Regular Meeting",
                meeting_body=body,
                agenda_url=f"{request.discovery_url}/agenda",
                minutes_url=f"{request.discovery_url}/minutes",
                video_url=f"{request.discovery_url}/video",
                source_url=request.discovery_url,
            )
            for body in request.bodies
        ]
        runtime_ms = int((time.perf_counter() - start) * 1000)
        metrics = DryRunMetrics(meetings_discovered=len(meetings), runtime_ms=runtime_ms)
        return DiscoverMeetingsResult(meetings=meetings, metrics=metrics)

    def parse_agenda(self, request: ConnectorRequest, meeting: MeetingRecord) -> ParseAgendaResult:
        start = time.perf_counter()
        agenda_items = [
            AgendaItemRecord(
                external_agenda_item_id=f"{meeting.external_meeting_id}-001",
                item_number="1",
                title=meeting.meeting_title,
                summary=None,
                action=None,
                vote_result=None,
            )
        ]
        runtime_ms = int((time.perf_counter() - start) * 1000)
        metrics = DryRunMetrics(
            meetings_parsed=1,
            agenda_items_parsed=len(agenda_items),
            runtime_ms=runtime_ms,
        )
        return ParseAgendaResult(agenda_items=agenda_items, metrics=metrics)

    def extract_documents(self, request: ConnectorRequest, meeting: MeetingRecord) -> ExtractDocumentsResult:
        start = time.perf_counter()
        agenda_url = meeting.agenda_url or meeting.source_url
        documents = [
            DocumentRecord(
                external_document_id=f"{meeting.external_meeting_id}-agenda",
                document_type=DocumentType.AGENDA,
                file_url=agenda_url,
                file_name="agenda.pdf",
                file_size_bytes=1024,
                linked_agenda_item_id=None,
            )
        ]
        runtime_ms = int((time.perf_counter() - start) * 1000)
        metrics = DryRunMetrics(documents_referenced=len(documents), runtime_ms=runtime_ms)
        return ExtractDocumentsResult(documents=documents, metrics=metrics)


class GranicusConnector(StubConnector):
    platform_name = "granicus"

    def discover_meetings(self, request: ConnectorRequest) -> DiscoverMeetingsResult:
        start = time.perf_counter()
        fallback_html = GRANICUS_SAMPLE_HTML.format(
            start_date=request.date_range.start_date,
            end_date=request.date_range.end_date,
            base=request.discovery_url.rstrip("/"),
        )
        html = fallback_html
        errors_count = 0
        if request.live_fetch:
            fetched = fetch_html_with_fallback(
                request.discovery_url,
                fallback_html=fallback_html,
                timeout_seconds=request.timeout_seconds,
                max_retries=request.max_retries,
                verify_ssl=request.verify_ssl,
            )
            html = fetched.html
            if not fetched.used_live_source:
                errors_count += 1

        meetings = parse_granicus_meetings(html=html, city_id=request.city_id)
        if request.live_fetch and not meetings:
            meetings = parse_granicus_meetings(html=fallback_html, city_id=request.city_id)
            errors_count += 1

        filtered = [meeting for meeting in meetings if _matches_requested_body(meeting.meeting_body, request.bodies)]
        runtime_ms = int((time.perf_counter() - start) * 1000)
        metrics = DryRunMetrics(meetings_discovered=len(filtered), errors_count=errors_count, runtime_ms=runtime_ms)
        return DiscoverMeetingsResult(meetings=filtered, metrics=metrics)


class LegistarConnector(StubConnector):
    platform_name = "legistar"

    @staticmethod
    def _derive_legistar_agenda_url(meeting: MeetingRecord) -> str | None:
        candidate = meeting.agenda_url
        if candidate and "View.ashx" in candidate:
            return candidate

        source = meeting.source_url
        if "MeetingDetail.aspx" not in source:
            return None

        parsed = urlparse(source)
        query = parse_qs(parsed.query)
        meeting_id = (query.get("ID") or [None])[0]
        if not meeting_id:
            return None

        guid = (query.get("GUID") or [None])[0]
        new_query = f"M=A&ID={meeting_id}"
        if guid:
            new_query = f"{new_query}&GUID={guid}"
        return urlunparse((parsed.scheme, parsed.netloc, "/View.ashx", "", new_query, ""))

    def discover_meetings(self, request: ConnectorRequest) -> DiscoverMeetingsResult:
        start = time.perf_counter()
        base = request.discovery_url.rstrip("/")
        fallback_html = LEGISTAR_SAMPLE_HTML.format(
            start_date=request.date_range.start_date,
            end_date=request.date_range.end_date,
            base=base.replace("/Calendar.aspx", ""),
        )
        html = fallback_html
        errors_count = 0

        if request.live_fetch:
            fetched = fetch_html_with_fallback(
                request.discovery_url,
                fallback_html=fallback_html,
                timeout_seconds=request.timeout_seconds,
                max_retries=request.max_retries,
                verify_ssl=request.verify_ssl,
            )
            html = fetched.html
            if not fetched.used_live_source:
                errors_count += 1
                runtime_ms = int((time.perf_counter() - start) * 1000)
                metrics = DryRunMetrics(meetings_discovered=0, errors_count=errors_count, runtime_ms=runtime_ms)
                return DiscoverMeetingsResult(meetings=[], metrics=metrics)

        meetings = parse_legistar_meetings(html=html, city_id=request.city_id, base_url=request.discovery_url)
        if request.live_fetch and not meetings:
            meetings = parse_legistar_meetings(html=fallback_html, city_id=request.city_id, base_url=request.discovery_url)
            errors_count += 1

        filtered = [meeting for meeting in meetings if _matches_requested_body(meeting.meeting_body, request.bodies)]

        if request.live_fetch:
            valid_live_meetings: list[MeetingRecord] = []
            for meeting in filtered:
                if _looks_like_stub_meeting(meeting.source_url):
                    errors_count += 1
                    continue
                valid_live_meetings.append(meeting)
            filtered = valid_live_meetings

        runtime_ms = int((time.perf_counter() - start) * 1000)
        metrics = DryRunMetrics(meetings_discovered=len(filtered), errors_count=errors_count, runtime_ms=runtime_ms)
        return DiscoverMeetingsResult(meetings=filtered, metrics=metrics)

    def parse_agenda(self, request: ConnectorRequest, meeting: MeetingRecord) -> ParseAgendaResult:
        start = time.perf_counter()
        detail_url = meeting.source_url if "MeetingDetail.aspx" in meeting.source_url else meeting.agenda_url
        fallback_html = _build_legistar_fallback_agenda_html(meeting)
        html = fallback_html
        errors_count = 0
        meeting_detail_200_count = 0

        if request.live_fetch and detail_url:
            fetched = fetch_html_with_fallback(
                detail_url,
                fallback_html=fallback_html,
                timeout_seconds=request.timeout_seconds,
                max_retries=request.max_retries,
                verify_ssl=request.verify_ssl,
            )
            if fetched.used_live_source:
                html = fetched.html
                if fetched.status_code == 200:
                    meeting_detail_200_count = 1
            else:
                errors_count += 1
                runtime_ms = int((time.perf_counter() - start) * 1000)
                metrics = DryRunMetrics(
                    meetings_parsed=1,
                    meeting_detail_200_count=meeting_detail_200_count,
                    agenda_items_parsed=0,
                    errors_count=errors_count,
                    runtime_ms=runtime_ms,
                )
                return ParseAgendaResult(agenda_items=[], metrics=metrics)

        agenda_items = parse_legistar_agenda_items(
            html=html,
            city_id=request.city_id,
            meeting_external_id=meeting.external_meeting_id,
        )

        runtime_ms = int((time.perf_counter() - start) * 1000)
        metrics = DryRunMetrics(
            meetings_parsed=1,
            meeting_detail_200_count=meeting_detail_200_count,
            agenda_items_parsed=len(agenda_items),
            errors_count=errors_count,
            runtime_ms=runtime_ms,
        )
        return ParseAgendaResult(agenda_items=agenda_items, metrics=metrics)

    def extract_documents(self, request: ConnectorRequest, meeting: MeetingRecord) -> ExtractDocumentsResult:
        start = time.perf_counter()
        documents: list[DocumentRecord] = []

        agenda_url = self._derive_legistar_agenda_url(meeting)
        if agenda_url:
            documents.append(
                DocumentRecord(
                    external_document_id=f"{meeting.external_meeting_id}-agenda",
                    document_type=DocumentType.AGENDA,
                    file_url=agenda_url,
                    file_name="agenda.pdf",
                    file_size_bytes=1024,
                    linked_agenda_item_id=None,
                )
            )

        if meeting.minutes_url and "View.ashx" in meeting.minutes_url:
            documents.append(
                DocumentRecord(
                    external_document_id=f"{meeting.external_meeting_id}-minutes",
                    document_type=DocumentType.ATTACHMENT,
                    file_url=meeting.minutes_url,
                    file_name="minutes.pdf",
                    file_size_bytes=1024,
                    linked_agenda_item_id=None,
                )
            )

        runtime_ms = int((time.perf_counter() - start) * 1000)
        metrics = DryRunMetrics(documents_referenced=len(documents), runtime_ms=runtime_ms)
        return ExtractDocumentsResult(documents=documents, metrics=metrics)


class LaserficheConnector(StubConnector):
    platform_name = "laserfiche"


class NovusAgendaConnector(StubConnector):
    platform_name = "novusagenda"


class OnBaseConnector(StubConnector):
    platform_name = "onbase"


class CivicPlusConnector(StubConnector):
    platform_name = "civicplus"
