"""Duration parsing supporting weeks ('w') and days ('d') beyond the standard Go format."""

import re
from datetime import datetime, timedelta, time

DAY = timedelta(days=1)
WEEK = timedelta(weeks=1)

_UNITS = {
    'ns': 1e-9,
    'us': 1e-6,
    'ms': 1e-3,
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'w': 604800,
}

_DURATION_RE = re.compile(r'(\d+(?:\.\d+)?)([a-z]+)')


def parse_duration(s):
    if not s:
        raise ValueError(f"invalid duration: {s!r}")
    if s == '0':
        return timedelta(0)
    total = 0.0
    for m in _DURATION_RE.finditer(s):
        val = float(m.group(1))
        unit = m.group(2)
        if unit not in _UNITS:
            raise ValueError(f"invalid duration unit: {unit!r}")
        total += val * _UNITS[unit]
    return timedelta(seconds=total)


def parse_datetime(now, s):
    s = s.strip()
    if not s:
        raise ValueError(f"invalid date/time: {s!r}")

    # Try "YYYY-MM-DD HH:MM:SS"
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})$', s)
    if m:
        parts = [int(x) for x in m.groups()]
        return now.replace(year=parts[0], month=parts[1], day=parts[2], hour=parts[3], minute=parts[4], second=parts[5], microsecond=0)

    # Try "YYYY-MM-DD"
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', s)
    if m:
        parts = [int(x) for x in m.groups()]
        return now.replace(year=parts[0], month=parts[1], day=parts[2], hour=0, minute=0, second=0, microsecond=0)

    # Try "HH:MM:SS"
    m = re.match(r'^(\d{2}):(\d{2}):(\d{2})$', s)
    if m:
        parts = [int(x) for x in m.groups()]
        d = now.replace(hour=parts[0], minute=parts[1], second=parts[2], microsecond=0)
        return _next_time(now, d)

    # Try "H:MM AM/PM" or "H:MM am/pm"
    m = re.match(r'^(\d{1,2}):(\d{2})\s*(am|pm)$', s, re.IGNORECASE)
    if m:
        h = int(m.group(1))
        mn = int(m.group(2))
        ampm = m.group(3).lower()
        if ampm == 'pm' and h != 12:
            h += 12
        elif ampm == 'am' and h == 12:
            h = 0
        d = now.replace(hour=h, minute=mn, second=0, microsecond=0)
        return _next_time(now, d)

    # Try "HH:MM" (24-hour)
    m = re.match(r'^(\d{2}):(\d{2})$', s)
    if m:
        h, mn = int(m.group(1)), int(m.group(2))
        d = now.replace(hour=h, minute=mn, second=0, microsecond=0)
        return _next_time(now, d)

    raise ValueError(f"invalid date/time format: {s!r}")


def _next_time(now, d):
    d = d.replace(tzinfo=now.tzinfo)
    if d <= now:
        d += timedelta(days=1)
    return d


def duration_string(duration, with_seconds):
    total_secs = int(duration.total_seconds())
    neg = total_secs < 0
    if neg:
        total_secs = -total_secs
        return "-" + duration_string(timedelta(seconds=total_secs), with_seconds)

    days = total_secs // 86400
    hours = (total_secs % 86400) // 3600
    minutes = (total_secs % 3600) // 60
    secs = total_secs % 60

    if days > 0:
        parts = [f"{days:02d}:{hours:02d}:{minutes:02d}"]
    elif hours > 0:
        parts = [f"{hours:02d}:{minutes:02d}"]
    else:
        parts = [f"{minutes:02d}"]

    if with_seconds:
        parts[0] += f":{secs:02d}"

    return parts[0]


def duration_ddhhmm(duration):
    total_secs = int(duration.total_seconds())
    neg = total_secs < 0
    if neg:
        total_secs = -total_secs
        return "-" + duration_ddhhmm(timedelta(seconds=total_secs))

    days = total_secs // 86400
    hours = (total_secs % 86400) // 3600
    minutes = (total_secs % 3600) // 60

    if days > 0:
        return f"{days:02d}:{hours:02d}:{minutes:02d}"
    if hours > 0 or days > 0:
        return f"{days * 24 + hours:02d}:{minutes:02d}"
    return f"{minutes:02d}"
