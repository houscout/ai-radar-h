"""Validate a radar snapshot against its schema and editorial invariants."""
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from jsonschema import Draft202012Validator, FormatChecker


def validate_snapshot(snapshot, schema, weekly=False):
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(snapshot)
    signals = snapshot["signals"]
    ids = [signal["id"] for signal in signals]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate signal IDs")
    if len(signals) > 5:
        raise ValueError("At most five signals are allowed")
    now = datetime.fromisoformat(snapshot["savedAt"].replace("Z", "+00:00"))
    local = now.astimezone(ZoneInfo("America/Matamoros"))
    if snapshot["snapshotDate"] != local.date().isoformat():
        raise ValueError("Snapshot date differs from savedAt in America/Matamoros")
    urls = set()
    groups = set()
    for signal in signals:
        if signal["action"]["status"] != "proposed":
            raise ValueError("Research actions must remain proposed")
        url = signal["sources"][0]["url"].rstrip("/")
        if url in urls:
            raise ValueError("Duplicate primary source URL")
        urls.add(url)
        group = signal["eventGroupId"]
        if weekly and group and group in groups:
            raise ValueError("Select one weekly signal per event group")
        if group:
            groups.add(group)
        for source in signal["sources"]:
            accessed = datetime.fromisoformat(source["accessedAt"].replace("Z", "+00:00"))
            if accessed > now + timedelta(minutes=5):
                raise ValueError("Source consultation date is in the future")
        if weekly:
            published = datetime.fromisoformat(signal["publishedDate"]).date()
            if not local.date() - timedelta(days=7) <= published <= local.date():
                raise ValueError("Publication date outside weekly window")
        if signal["biomedical"]:
            regulatory = signal["biomedical"]["regulatory"]
            if regulatory["status"] == "verified" and not all(
                regulatory[key] for key in ("jurisdiction", "sourceUrl", "verifiedAt")
            ):
                raise ValueError("Verified regulatory status requires evidence")
    return len(signals)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("schema", type=Path)
    parser.add_argument("--weekly", action="store_true")
    args = parser.parse_args()
    count = validate_snapshot(
        json.loads(args.snapshot.read_text(encoding="utf-8-sig")),
        json.loads(args.schema.read_text(encoding="utf-8-sig")),
        args.weekly,
    )
    print(f"Valid snapshot: {count} signals")


if __name__ == "__main__":
    main()

