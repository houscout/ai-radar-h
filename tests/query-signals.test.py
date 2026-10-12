"""Behavioral tests using temporary, explicitly synthetic snapshots."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "query-signals.py"
SPEC = importlib.util.spec_from_file_location("query_signals", SCRIPT)
QUERY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(QUERY)


class QueryTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)
    self.ai = self.root / "ai"
    self.bio = self.root / "bio"
    self.write(self.ai, "ai", "2026-10-09")
    self.write(self.ai, "ai", "2026-10-11")
    self.write(self.bio, "biomed", "2026-10-10")

  def write(self, repo, radar, day):
    directory = repo / "data" / "daily"
    directory.mkdir(parents=True, exist_ok=True)
    project, domain = QUERY.PROJECTS[radar]
    data = {"schemaVersion": "1.0.0", "project": project, "domain": domain,
            "snapshotDate": day, "signals": [
              {"id": "01", "title": "Zulu", "publishedDate": "2026-10-01", "impact": {"level": "alto"}},
              {"id": "02", "title": "Alpha", "publishedDate": "2026-10-03", "impact": {"level": "desconocido"}},
              {"id": "03", "title": "Beta", "publishedDate": "2026-10-02", "impact": {"level": "medio"}},
            ]}
    (directory / (day + ".json")).write_text(json.dumps(data), encoding="utf-8")

  def query(self, day="latest", count=5, order="date", direction="desc"):
    return QUERY.query_radar(self.ai, "ai", day, count, order, direction)

  def test_exact_day_and_limit(self):
    result = self.query(day="2026-10-09", count=2)
    self.assertEqual(result["snapshotDate"], "2026-10-09")
    self.assertEqual([s["id"] for s in result["signals"]], ["02", "03"])

  def test_each_radar_has_its_own_latest(self):
    self.assertEqual(self.query()["snapshotDate"], "2026-10-11")
    result = QUERY.query_radar(self.bio, "biomed", "latest", 5, "date", "desc")
    self.assertEqual(result["snapshotDate"], "2026-10-10")

  def test_sort_orders(self):
    expected = {("date", "asc"): ["01", "03", "02"],
                ("impact", "desc"): ["01", "03", "02"],
                ("impact", "asc"): ["02", "03", "01"],
                ("title", "asc"): ["02", "03", "01"],
                ("original", "asc"): ["01", "02", "03"],
                ("original", "desc"): ["03", "02", "01"]}
    for (order, direction), ids in expected.items():
      with self.subTest(order=order, direction=direction):
        self.assertEqual([s["id"] for s in self.query(order=order, direction=direction)["signals"]], ids)

  def test_larger_n_and_zero(self):
    result = self.query(count=10)
    self.assertEqual(result["returnedCount"], 3)
    self.assertEqual(result["shortfall"], 7)
    self.assertEqual(self.query(count=0)["signals"], [])

  def test_no_fallback_for_missing_day(self):
    result = self.query(day="2026-10-08")
    self.assertEqual(result["status"], "missing")
    self.assertEqual(result["signals"], [])
    self.assertEqual(result["availableDays"], ["2026-10-09", "2026-10-11"])

  def test_invalid_json_and_wrong_domain(self):
    path = self.ai / "data/daily/2026-10-11.json"
    path.write_text("{broken", encoding="utf-8")
    self.assertEqual(self.query()["status"], "invalid")
    self.write(self.ai, "biomed", "2026-10-11")
    self.assertEqual(self.query()["status"], "invalid")

  def test_cli_partial_returns_json(self):
    process = subprocess.run(
      [sys.executable, str(SCRIPT), "--ai-repo", str(self.ai), "--biomed-repo", str(self.bio),
       "--day", "2026-10-11", "--count", "2"], capture_output=True, text=True, encoding="utf-8")
    self.assertEqual(process.returncode, 1)
    output = json.loads(process.stdout)
    self.assertEqual(output["returnedCount"], 2)
    self.assertEqual(output["results"][1]["status"], "missing")

  def test_invalid_arguments(self):
    for args in (["--count", "-1"], ["--day", "../x"], ["--day", "2026-02-30"]):
      process = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True)
      self.assertEqual(process.returncode, 2)
      self.assertEqual(process.stdout, b"")

  def test_read_only(self):
    path = self.ai / "data/daily/2026-10-11.json"
    before = path.read_bytes()
    self.query(count=1, order="title")
    self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
  unittest.main()
