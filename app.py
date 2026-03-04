#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, request


ROOT = Path(__file__).resolve().parent
app = Flask(__name__)


def _run_py(script_name: str, args: List[str]) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(ROOT / script_name), *args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), check=False)


def _require_json_keys(payload: Dict[str, Any], keys: List[str]) -> None:
    missing = [k for k in keys if not payload.get(k)]
    if missing:
        raise ValueError(f"Missing required JSON fields: {missing}")


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok", "service": "demand-forecast-api"})


@app.get("/pipeline")
def pipeline() -> Any:
    return jsonify(
        {
            "steps": [
                {
                    "name": "preprocess",
                    "script": "preprocess_sales.py",
                    "outputs": [
                        "sales_transactions_2017_2019.csv.gz",
                        "item_month_agg_2017_2019.csv",
                        "train_item_month_2017_2019_cutoff_YYYY-MM_with_roll.csv",
                        "test_item_month_2017_2019_start_YYYY-MM_with_roll.csv",
                    ],
                },
                {
                    "name": "train_evaluate",
                    "script": "train_evaluate_monthly.py",
                    "outputs": [
                        "predictions_test.csv",
                        "metrics_by_month.csv",
                        "metrics_overall.json",
                    ],
                },
                {
                    "name": "product_report",
                    "script": "product_last6m_report.py",
                    "outputs": [
                        "metrics_by_product_last6m.csv",
                        "results_by_product_month_last6m.csv",
                    ],
                },
            ]
        }
    )


@app.post("/preprocess")
def preprocess() -> Any:
    payload = request.get_json(silent=True) or {}
    try:
        _require_json_keys(payload, ["sales2017", "sales2018", "sales2019"])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    outdir = str(payload.get("outdir") or (ROOT / "data"))
    train_end = str(payload.get("train_end") or "2019-04-01")
    test_start = str(payload.get("test_start") or "2019-05-01")
    windows = payload.get("windows") or [3, 6, 12]

    args = [
        "--sales2017",
        str(payload["sales2017"]),
        "--sales2018",
        str(payload["sales2018"]),
        "--sales2019",
        str(payload["sales2019"]),
        "--outdir",
        outdir,
        "--train_end",
        train_end,
        "--test_start",
        test_start,
        "--windows",
        *[str(x) for x in windows],
    ]

    for year in ("2017", "2018", "2019"):
        key = f"sheet{year}"
        if payload.get(key):
            args.extend([f"--{key}", str(payload[key])])

    proc = _run_py("preprocess_sales.py", args)
    if proc.returncode != 0:
        return jsonify({"error": "preprocess failed", "stderr": proc.stderr, "stdout": proc.stdout}), 500

    outdir_path = Path(outdir)
    cutoff = train_end[:7]
    start = test_start[:7]

    resp = {
        "status": "ok",
        "stdout": proc.stdout,
        "outputs": {
            "train_csv": str(outdir_path / f"train_item_month_2017_2019_cutoff_{cutoff}_with_roll.csv"),
            "test_csv": str(outdir_path / f"test_item_month_2017_2019_start_{start}_with_roll.csv"),
            "panel_csv": str(outdir_path / "item_month_agg_2017_2019_with_roll.csv"),
        },
    }
    return jsonify(resp)


@app.post("/train-evaluate")
def train_evaluate() -> Any:
    payload = request.get_json(silent=True) or {}
    try:
        _require_json_keys(payload, ["train_csv", "test_csv"])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    outdir = str(payload.get("outdir") or (ROOT / "data"))
    args = [
        "--train_csv",
        str(payload["train_csv"]),
        "--test_csv",
        str(payload["test_csv"]),
        "--outdir",
        outdir,
    ]

    proc = _run_py("train_evaluate_monthly.py", args)
    if proc.returncode != 0:
        return jsonify({"error": "train-evaluate failed", "stderr": proc.stderr, "stdout": proc.stdout}), 500

    outdir_path = Path(outdir)
    metrics_path = outdir_path / "metrics_overall.json"
    metrics: Dict[str, Any] = {}
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    return jsonify(
        {
            "status": "ok",
            "stdout": proc.stdout,
            "metrics_overall": metrics,
            "outputs": {
                "predictions_csv": str(outdir_path / "predictions_test.csv"),
                "metrics_by_month_csv": str(outdir_path / "metrics_by_month.csv"),
                "metrics_overall_json": str(metrics_path),
            },
        }
    )


@app.post("/report-last")
def report_last() -> Any:
    payload = request.get_json(silent=True) or {}
    try:
        _require_json_keys(payload, ["pred_csv"])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    outdir = str(payload.get("outdir") or (ROOT / "data"))
    last_n_months = int(payload.get("last_n_months") or 6)

    args = [
        "--pred_csv",
        str(payload["pred_csv"]),
        "--outdir",
        outdir,
        "--last_n_months",
        str(last_n_months),
    ]

    proc = _run_py("product_last6m_report.py", args)
    if proc.returncode != 0:
        return jsonify({"error": "report failed", "stderr": proc.stderr, "stdout": proc.stdout}), 500

    outdir_path = Path(outdir)
    return jsonify(
        {
            "status": "ok",
            "stdout": proc.stdout,
            "outputs": {
                "metrics_by_product_csv": str(outdir_path / f"metrics_by_product_last{last_n_months}m.csv"),
                "results_by_product_month_csv": str(outdir_path / f"results_by_product_month_last{last_n_months}m.csv"),
            },
        }
    )


@app.post("/run-all")
def run_all() -> Any:
    payload = request.get_json(silent=True) or {}
    try:
        _require_json_keys(payload, ["sales2017", "sales2018", "sales2019"])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    outdir = str(payload.get("outdir") or (ROOT / "data"))
    train_end = str(payload.get("train_end") or "2019-04-01")
    test_start = str(payload.get("test_start") or "2019-05-01")
    last_n_months = int(payload.get("last_n_months") or 6)

    preprocess_args = [
        "--sales2017",
        str(payload["sales2017"]),
        "--sales2018",
        str(payload["sales2018"]),
        "--sales2019",
        str(payload["sales2019"]),
        "--outdir",
        outdir,
        "--train_end",
        train_end,
        "--test_start",
        test_start,
        "--windows",
        "3",
        "6",
        "12",
    ]

    preprocess_proc = _run_py("preprocess_sales.py", preprocess_args)
    if preprocess_proc.returncode != 0:
        return jsonify({"error": "preprocess failed", "stderr": preprocess_proc.stderr}), 500

    cutoff = train_end[:7]
    start = test_start[:7]
    train_csv = Path(outdir) / f"train_item_month_2017_2019_cutoff_{cutoff}_with_roll.csv"
    test_csv = Path(outdir) / f"test_item_month_2017_2019_start_{start}_with_roll.csv"

    train_proc = _run_py(
        "train_evaluate_monthly.py",
        ["--train_csv", str(train_csv), "--test_csv", str(test_csv), "--outdir", outdir],
    )
    if train_proc.returncode != 0:
        return jsonify({"error": "train-evaluate failed", "stderr": train_proc.stderr}), 500

    pred_csv = Path(outdir) / "predictions_test.csv"
    report_proc = _run_py(
        "product_last6m_report.py",
        ["--pred_csv", str(pred_csv), "--outdir", outdir, "--last_n_months", str(last_n_months)],
    )
    if report_proc.returncode != 0:
        return jsonify({"error": "report failed", "stderr": report_proc.stderr}), 500

    metrics = {}
    metrics_path = Path(outdir) / "metrics_overall.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    return jsonify(
        {
            "status": "ok",
            "steps": {
                "preprocess": "ok",
                "train_evaluate": "ok",
                "report_last": "ok",
            },
            "metrics_overall": metrics,
            "outputs": {
                "predictions_csv": str(Path(outdir) / "predictions_test.csv"),
                "metrics_by_month_csv": str(Path(outdir) / "metrics_by_month.csv"),
                "metrics_overall_json": str(metrics_path),
                "metrics_by_product_csv": str(Path(outdir) / f"metrics_by_product_last{last_n_months}m.csv"),
            },
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)