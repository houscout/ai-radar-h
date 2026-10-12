"""Read archived radar snapshots without modifying them. Python 3.10+, stdlib only."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

IMPACT = {"alto": 3, "medio": 2, "bajo": 1, "desconocido": 0}
PROJECTS = {"ai": ("AI Radar", "ai"), "biomed": ("Biomedic Radar", "biomedicine")}


def parse_day(value):
  if value == "latest":
    return value
  try:
    if date.fromisoformat(value).isoformat() != value:
      raise ValueError()
  except ValueError:
    raise argparse.ArgumentTypeError("Use YYYY-MM-DD or latest")
  return value


def parse_count(value):
  try:
    count = int(value)
  except ValueError:
    raise argparse.ArgumentTypeError("Count must be a nonnegative integer")
  if count < 0:
    raise argparse.ArgumentTypeError("Count must be a nonnegative integer")
  return count


def available_days(directory):
  days = []
  if directory.is_dir():
    for path in directory.glob("*.json"):
      try:
        if parse_day(path.stem) != "latest":
          days.append(path.stem)
      except argparse.ArgumentTypeError:
        pass
  return sorted(days)


def read_snapshot(path, radar, selected_day):
  snapshot = json.loads(path.read_text(encoding="utf-8-sig"))
  project, domain = PROJECTS[radar]
  if not isinstance(snapshot, dict):
    raise ValueError("Snapshot must be a JSON object")
  if snapshot.get("schemaVersion") != "1.0.0":
    raise ValueError("Unsupported snapshot schemaVersion")
  if snapshot.get("project") != project or snapshot.get("domain") != domain:
    raise ValueError("Snapshot project/domain does not match selected radar")
  if snapshot.get("snapshotDate") != selected_day:
    raise ValueError("Snapshot date differs from filename")
  signals = snapshot.get("signals")
  if not isinstance(signals, list):
    raise ValueError("signals must be an array")
  ids = set()
  for signal in signals:
    if not isinstance(signal, dict):
      raise ValueError("Each signal must be an object")
    identifier = signal.get("id")
    if not isinstance(identifier, str) or not identifier or identifier in ids:
      raise ValueError("Signal IDs must be nonempty and unique")
    ids.add(identifier)
    if not isinstance(signal.get("title"), str) or not signal["title"]:
      raise ValueError("Signal title must be a nonempty string")
    published = signal.get("publishedDate")
    if not isinstance(published, str) or parse_day(published) == "latest":
      raise ValueError("Signal publishedDate must be YYYY-MM-DD")
    impact = signal.get("impact")
    if not isinstance(impact, dict) or impact.get("level") not in IMPACT:
      raise ValueError("Invalid impact level")
  return snapshot


def query_radar(repo, radar, day, count, order, direction):
  directory = Path(repo).resolve() / "data" / "daily"
  days = available_days(directory)
  selected_day = days[-1] if day == "latest" and days else day
  result = {
    "radar": radar, "project": PROJECTS[radar][0],
    "requestedDay": day, "snapshotDate": None,
    "availableDays": days, "requestedCount": count,
    "availableCount": 0, "returnedCount": 0,
    "status": "missing", "signals": [],
  }
  if selected_day == "latest" or selected_day not in days:
    result["error"] = "No snapshot exists for the requested day"
    return result
  path = directory / (selected_day + ".json")
  result["sourceFile"] = str(path)
  result["snapshotDate"] = selected_day
  try:
    snapshot = read_snapshot(path, radar, selected_day)
    signals = list(snapshot["signals"])
    if order == "date":
      signals.sort(key=lambda item: item["publishedDate"], reverse=direction == "desc")
    elif order == "impact":
      signals.sort(key=lambda item: IMPACT[item["impact"]["level"]], reverse=direction == "desc")
    elif order == "title":
      signals.sort(key=lambda item: item["title"].casefold(), reverse=direction == "desc")
    elif direction == "desc":
      signals.reverse()
    selected = signals[:count]
    result.update({
      "status": "ok", "availableCount": len(signals),
      "returnedCount": len(selected), "shortfall": max(0, count - len(selected)),
      "snapshotSchemaVersion": snapshot["schemaVersion"],
      "collection": snapshot.get("collection"),
      "savedAt": snapshot.get("savedAt"), "signals": selected,
    })
  except (OSError, ValueError, argparse.ArgumentTypeError) as exc:
    result["status"] = "invalid"
    result["error"] = str(exc)
  return result


def main(argv=None):
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--radar", choices=("both", "ai", "biomed"), default="both")
  parser.add_argument("--day", type=parse_day, default="latest", help="Snapshot day, not news day")
  parser.add_argument("--count", type=parse_count, default=5, help="Maximum signals PER radar")
  parser.add_argument("--order", choices=("date", "impact", "title", "original"), default="date")
  parser.add_argument("--direction", choices=("asc", "desc"), help="Default desc for date/impact; asc otherwise")
  parser.add_argument("--ai-repo", type=Path, default=Path.home() / "codex")
  parser.add_argument("--biomed-repo", type=Path, default=Path.home() / "biomedic-radar")
  args = parser.parse_args(argv)
  direction = args.direction or ("desc" if args.order in ("date", "impact") else "asc")
  radars = ("ai", "biomed") if args.radar == "both" else (args.radar,)
  results = [query_radar(
    args.ai_repo if radar == "ai" else args.biomed_repo,
    radar, args.day, args.count, args.order, direction,
  ) for radar in radars]
  response = {
    "queryVersion": "1.0.0",
    "query": {"radar": args.radar, "day": args.day, "countPerRadar": args.count,
              "order": args.order, "direction": direction},
    "returnedCount": sum(result["returnedCount"] for result in results),
    "results": results,
  }
  print(json.dumps(response, ensure_ascii=False, indent=2))
  return 0 if all(result["status"] == "ok" for result in results) else 1


if __name__ == "__main__":
  if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
  try:
    raise SystemExit(main())
  except BrokenPipeError:
    raise SystemExit(0)
