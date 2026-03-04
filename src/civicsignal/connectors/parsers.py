from __future__ import annotations

import hashlib
import re
from html import unescape
from urllib.parse import urljoin

from .models import AgendaItemRecord, MeetingRecord

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def _clean_html_text(value: str) -> str:
    without_tags = TAG_RE.sub(" ", value)
    normalized = WHITESPACE_RE.sub(" ", unescape(without_tags)).strip()
    return normalized


def _stable_meeting_id(platform: str, city_id: str, body: str, meeting_date: str, title: str) -> str:
    base = f"{platform}|{city_id}|{body}|{meeting_date}|{title}".encode("utf-8")
    digest = hashlib.sha1(base).hexdigest()[:12]
    return f"{city_id}-{digest}"


def _extract_first_date(value: str) -> str:
    date_match = re.search(r"\b\d{1,2}/\d{1,2}/\d{4}\b", value)
    if date_match:
        return date_match.group(0)
    return ""


def _resolve_href(href: str | None, base_url: str | None) -> str | None:
    if not href:
        return None
    cleaned = unescape(href.strip())
    if cleaned.lower().startswith("javascript:"):
        return None
    if base_url:
        return urljoin(base_url, cleaned)
    return cleaned


def parse_granicus_meetings(html: str, city_id: str) -> list[MeetingRecord]:
    row_pattern = re.compile(
        r"<tr[^>]*data-body=[\"'](?P<body>[^\"']+)[\"'][^>]*>"
        r"(?P<row>.*?)"
        r"</tr>",
        re.IGNORECASE | re.DOTALL,
    )
    date_pattern = re.compile(r"<td[^>]*class=[\"']date[\"'][^>]*>(?P<value>.*?)</td>", re.IGNORECASE | re.DOTALL)
    title_pattern = re.compile(r"<td[^>]*class=[\"']title[\"'][^>]*>(?P<value>.*?)</td>", re.IGNORECASE | re.DOTALL)
    link_pattern = re.compile(
        r"<a[^>]*class=[\"'](?P<class_name>agenda|minutes|video)[\"'][^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>",
        re.IGNORECASE,
    )

    meetings: list[MeetingRecord] = []
    for row_match in row_pattern.finditer(html):
        body = _clean_html_text(row_match.group("body"))
        row = row_match.group("row")

        date_match = date_pattern.search(row)
        title_match = title_pattern.search(row)
        if not date_match or not title_match:
            continue

        meeting_date = _clean_html_text(date_match.group("value"))
        meeting_title = _clean_html_text(title_match.group("value"))

        links: dict[str, str | None] = {"agenda": None, "minutes": None, "video": None}
        for link_match in link_pattern.finditer(row):
            links[link_match.group("class_name").lower()] = link_match.group("href")

        source_url = links["agenda"] or links["minutes"] or links["video"] or ""
        meeting_id = _stable_meeting_id("granicus", city_id, body, meeting_date, meeting_title)

        meetings.append(
            MeetingRecord(
                external_meeting_id=meeting_id,
                meeting_date=meeting_date,
                meeting_title=meeting_title,
                meeting_body=body,
                agenda_url=links["agenda"],
                minutes_url=links["minutes"],
                video_url=links["video"],
                source_url=source_url,
            )
        )

    return meetings


def parse_legistar_meetings(html: str, city_id: str, base_url: str | None = None) -> list[MeetingRecord]:
    row_pattern = re.compile(
        r"<tr[^>]*data-meeting-body=[\"'](?P<body>[^\"']+)[\"'][^>]*>"
        r"(?P<row>.*?)"
        r"</tr>",
        re.IGNORECASE | re.DOTALL,
    )
    date_pattern = re.compile(r"<td[^>]*class=[\"']meeting-date[\"'][^>]*>(?P<value>.*?)</td>", re.IGNORECASE | re.DOTALL)
    title_pattern = re.compile(r"<td[^>]*class=[\"']meeting-title[\"'][^>]*>(?P<value>.*?)</td>", re.IGNORECASE | re.DOTALL)
    agenda_pattern = re.compile(r"<a[^>]*class=[\"']agenda-link[\"'][^>]*href=[\"'](?P<href>[^\"']+)[\"']", re.IGNORECASE)
    minutes_pattern = re.compile(r"<a[^>]*class=[\"']minutes-link[\"'][^>]*href=[\"'](?P<href>[^\"']+)[\"']", re.IGNORECASE)
    video_pattern = re.compile(r"<a[^>]*class=[\"']video-link[\"'][^>]*href=[\"'](?P<href>[^\"']+)[\"']", re.IGNORECASE)

    meetings: list[MeetingRecord] = []
    for row_match in row_pattern.finditer(html):
        body = _clean_html_text(row_match.group("body"))
        row = row_match.group("row")

        date_match = date_pattern.search(row)
        title_match = title_pattern.search(row)
        if not date_match or not title_match:
            continue

        meeting_date = _clean_html_text(date_match.group("value"))
        meeting_title = _clean_html_text(title_match.group("value"))
        agenda_match = agenda_pattern.search(row)
        minutes_match = minutes_pattern.search(row)
        video_match = video_pattern.search(row)

        agenda_url = _resolve_href(agenda_match.group("href") if agenda_match else None, base_url)
        minutes_url = _resolve_href(minutes_match.group("href") if minutes_match else None, base_url)
        video_url = _resolve_href(video_match.group("href") if video_match else None, base_url)
        source_url = agenda_url or minutes_url or video_url or (base_url or "")

        meeting_id = _stable_meeting_id("legistar", city_id, body, meeting_date, meeting_title)
        meetings.append(
            MeetingRecord(
                external_meeting_id=meeting_id,
                meeting_date=meeting_date,
                meeting_title=meeting_title,
                meeting_body=body,
                agenda_url=agenda_url,
                minutes_url=minutes_url,
                video_url=video_url,
                source_url=source_url,
            )
        )

    if meetings:
        return meetings

    telerik_row_pattern = re.compile(
        r"<tr[^>]*id=[\"'][^\"']*gridCalendar_ctl00__\d+[^\"']*[\"'][^>]*>"
        r"(?P<row>.*?)"
        r"</tr>",
        re.IGNORECASE | re.DOTALL,
    )
    body_pattern = re.compile(r"<a[^>]*id=[\"'][^\"']*hypBody[\"'][^>]*>(?P<value>.*?)</a>", re.IGNORECASE | re.DOTALL)
    detail_pattern = re.compile(
        r"<a[^>]*id=[\"'][^\"']*hypMeetingDetail[\"'][^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    agenda2_pattern = re.compile(
        r"<a[^>]*id=[\"'][^\"']*hypAgenda[\"'][^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    minutes2_pattern = re.compile(
        r"<a[^>]*id=[\"'][^\"']*hypMinutes[\"'][^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    video2_pattern = re.compile(
        r"<a[^>]*id=[\"'][^\"']*hypVideo[\"'][^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>",
        re.IGNORECASE | re.DOTALL,
    )

    for row_match in telerik_row_pattern.finditer(html):
        row = row_match.group("row")
        body_match = body_pattern.search(row)
        if not body_match:
            continue

        body = _clean_html_text(body_match.group("value"))
        if not body:
            continue

        row_text = _clean_html_text(row)
        meeting_date = _extract_first_date(row_text)
        if not meeting_date:
            continue

        detail_match = detail_pattern.search(row)
        agenda_match = agenda2_pattern.search(row)
        minutes_match = minutes2_pattern.search(row)
        video_match = video2_pattern.search(row)

        detail_url = _resolve_href(detail_match.group("href") if detail_match else None, base_url)
        agenda_url = _resolve_href(agenda_match.group("href") if agenda_match else None, base_url)
        minutes_url = _resolve_href(minutes_match.group("href") if minutes_match else None, base_url)
        video_url = _resolve_href(video_match.group("href") if video_match else None, base_url)

        meeting_title = f"{body} Meeting"
        source_url = detail_url or agenda_url or minutes_url or video_url or (base_url or "")
        meeting_id = _stable_meeting_id("legistar", city_id, body, meeting_date, meeting_title)

        meetings.append(
            MeetingRecord(
                external_meeting_id=meeting_id,
                meeting_date=meeting_date,
                meeting_title=meeting_title,
                meeting_body=body,
                agenda_url=agenda_url,
                minutes_url=minutes_url,
                video_url=video_url,
                source_url=source_url,
            )
        )

    return meetings


def _stable_agenda_item_id(city_id: str, meeting_external_id: str, item_number: str, title: str) -> str:
    base = f"agenda|{city_id}|{meeting_external_id}|{item_number}|{title}".encode("utf-8")
    digest = hashlib.sha1(base).hexdigest()[:12]
    return f"{meeting_external_id}-{digest}"


def parse_legistar_agenda_items(html: str, city_id: str, meeting_external_id: str) -> list[AgendaItemRecord]:
    row_pattern = re.compile(
        r"<tr[^>]*(?:id=[\"'][^\"']*(?:gridAgenda|gridMain)_ctl00__\d+[^\"']*[\"']|data-agenda-row=[\"'][^\"']+[\"'])[^>]*>"
        r"(?P<row>.*?)"
        r"</tr>",
        re.IGNORECASE | re.DOTALL,
    )
    cell_pattern = re.compile(r"<td[^>]*>(?P<cell>.*?)</td>", re.IGNORECASE | re.DOTALL)
    title_link_pattern = re.compile(r"<a[^>]*>(?P<value>.*?)</a>", re.IGNORECASE | re.DOTALL)

    items: list[AgendaItemRecord] = []
    for row_match in row_pattern.finditer(html):
        row_html = row_match.group("row")
        cells = [_clean_html_text(cell_match.group("cell")) for cell_match in cell_pattern.finditer(row_html)]
        if len(cells) < 2:
            continue

        item_number = ""
        for cell in cells:
            value = cell.strip()
            if re.match(r"^\d+\.$", value):
                item_number = value.rstrip(".")
                break
        if not item_number:
            for cell in cells:
                value = cell.strip()
                if re.match(r"^\d+$", value) and len(value) <= 3:
                    item_number = value
                    break

        if not item_number:
            continue

        title_match = title_link_pattern.search(row_html)
        title = _clean_html_text(title_match.group("value")) if title_match else ""
        if title and re.match(r"^\d{2}-\d+$", title):
            title = ""
        if not title:
            for cell in cells:
                candidate = cell.strip()
                if len(candidate) < 6:
                    continue
                if candidate.lower() in {"report", "resolution", "ordinance", "not available"}:
                    continue
                if re.match(r"^\d{2}-\d+$", candidate):
                    continue
                title = candidate
                break
        if not title:
            continue

        summary = None
        for cell in cells:
            candidate = cell.strip()
            if not candidate or candidate == title:
                continue
            if candidate.lower() in {"report", "resolution", "ordinance", "not available"}:
                continue
            if re.match(r"^\d{2}-\d+$", candidate):
                continue
            if candidate == item_number:
                continue
            summary = candidate
            break

        items.append(
            AgendaItemRecord(
                external_agenda_item_id=_stable_agenda_item_id(city_id, meeting_external_id, item_number, title),
                item_number=item_number,
                title=title,
                summary=summary,
                action=None,
                vote_result=None,
            )
        )

    return items
