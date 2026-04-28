import datetime as dt
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


PACKAGE_DIR = REPO_ROOT / "python_ics"
UTC = dt.timezone.utc
UID_PATTERN = re.compile(
    r"^UID:(?P<uid>[A-Za-z0-9-]+)\r?$", re.MULTILINE
)
DTSTAMP_PATTERN = re.compile(
    r"^DTSTAMP:(?P<stamp>\d{8}T\d{6}Z)\r?$", re.MULTILINE
)


def _calendar_classes():
    from python_ics.classes import BaseCalendar, Event

    return BaseCalendar, Event


def _serialize(event, monkeypatch):
    BaseCalendar, _ = _calendar_classes()
    monkeypatch.chdir(PACKAGE_DIR)
    return BaseCalendar(events=[event]).get_execution_string()


def _event(**overrides):
    _, Event = _calendar_classes()
    data = {
        "title": "Planning",
        "dt_start": dt.datetime(2026, 1, 2, 3, 4, 5),
        "dt_end": dt.datetime(2026, 1, 2, 4, 4, 5),
        "location": "Mars Base",
        "description": "Roadmap review",
    }
    data.update(overrides)
    return Event(**data)


def _unfold_contentline(serialized, property_name):
    lines = serialized.replace("\r\n", "\n").split("\n")
    for index, line in enumerate(lines):
        if line.startswith(f"{property_name}:"):
            parts = [line]
            cursor = index + 1
            while cursor < len(lines) and lines[cursor].startswith(" "):
                parts.append(lines[cursor][1:])
                cursor += 1
            return "".join(parts)
    raise AssertionError(
        f"{property_name} content line not found in serialized output"
    )


def test_generates_uid_when_event_does_not_define_one(monkeypatch):
    event = _event()
    serialized = _serialize(event, monkeypatch)

    match = UID_PATTERN.search(serialized)

    assert match, serialized
    assert match.group("uid")


def test_dtstamp_is_dynamic_utc(monkeypatch):
    event = _event()
    before = dt.datetime.now(UTC).replace(microsecond=0)
    serialized = _serialize(event, monkeypatch)
    after = dt.datetime.now(UTC).replace(microsecond=0)

    match = DTSTAMP_PATTERN.search(serialized)

    assert match, serialized
    dtstamp = dt.datetime.strptime(
        match.group("stamp"), "%Y%m%dT%H%M%SZ"
    ).replace(tzinfo=UTC)
    assert before <= dtstamp <= after


def test_utc_aware_datetimes_serialize_without_hardcoded_europe_paris(
    monkeypatch,
):
    event = _event(
        dt_start=dt.datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        dt_end=dt.datetime(2026, 1, 2, 4, 4, 5, tzinfo=UTC),
    )

    serialized = _serialize(event, monkeypatch)

    assert "Europe/Paris" not in serialized
    assert "DTSTART:20260102T030405Z" in serialized
    assert "DTEND:20260102T040405Z" in serialized


def test_text_fields_are_escaped_per_rfc5545(monkeypatch):
    event = _event(
        title=r"Sprint review, phase 2; blockers\risks",
        location="Mars, Sector 7; Dome A",
        description="Line 1\nLine 2; Line 3, final",
    )

    serialized = _serialize(event, monkeypatch)

    assert (
        r"SUMMARY:Sprint review\, phase 2\; blockers\\risks"
        in serialized
    )
    assert r"LOCATION:Mars\, Sector 7\; Dome A" in serialized
    assert r"DESCRIPTION:Line 1\nLine 2\; Line 3\, final" in serialized


def test_long_content_lines_are_folded_on_continuation_boundaries(
    monkeypatch,
):
    location = "North Habitat " * 8
    event = _event(location=location, description=None)

    serialized = _serialize(event, monkeypatch)
    folded_line = _unfold_contentline(serialized, "LOCATION")

    assert "\r\n " in serialized
    assert folded_line == f"LOCATION:{location}"

    for raw_line in re.split(r"\r?\n", serialized):
        if raw_line.startswith("LOCATION:") or raw_line.startswith(" "):
            assert len(raw_line.encode("utf-8")) <= 75
