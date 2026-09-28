"""Portable reports; embedded JSON and HTML are escaped independently."""

import csv
import html
import json


def write_reports(report, output):
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["case_id", "family", "expected_status", "status", "matches_expected"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["results"])
    rows = []
    for result in report["results"]:
        witness = next((r.get("witness") for r in result["rules"] if r.get("witness")), None)
        evidence = html.escape(json.dumps(witness, indent=2)) if witness else "No violation evidence"
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(result[k]))}</td>" for k in ("case_id", "expected_status", "status"))
                    + f"<td><details><summary>Inspect evidence</summary><pre>{evidence}</pre></details></td></tr>")
    content = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Embodied Safety Toolkit report</title>
<style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 20px;color:#192b36;background:#f5f8fa}
table{border-collapse:collapse;width:100%;background:white}td,th{border:1px solid #ccd6df;padding:10px;text-align:left}
pre{white-space:pre-wrap;max-width:600px;font-size:12px}h1{color:#174e66}input{padding:10px;margin:15px 0;width:300px}</style>
<h1>Embodied Safety Toolkit</h1><p>Synthetic regression suite. These counts are software checks, not model safety scores.</p>
<p>SUMMARY</p><label>Filter cases <input id="filter" placeholder="Case name or status"></label>
<table><thead><tr><th>Case</th><th>Expected</th><th>Observed</th><th>Evidence</th></tr></thead><tbody>ROWS</tbody></table>
<script>document.getElementById('filter').addEventListener('input',e=>{for(const row of document.querySelectorAll('tbody tr'))row.hidden=!row.textContent.toLowerCase().includes(e.target.value.toLowerCase())});</script></html>"""
    content = content.replace("SUMMARY", html.escape(json.dumps(report["summary"]))).replace("ROWS", "".join(rows))
    (output / "report.html").write_text(content, encoding="utf-8")
