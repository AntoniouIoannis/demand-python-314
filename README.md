# Demand Python 314

[![Status](https://img.shields.io/badge/status-active-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.14-blue)]()

## 📌 Overview

This project is a **sales data preprocessing and API pipeline** that:

- reads 2017–2019 sales Excel files,
- standardizes and aggregates data to product-month level,
- completes grid and generates rolling statistics,
- provides a minimal Flask API to run the data pipeline.

---

## 🚀 Features

- 🧮 Sales data standardization & aggregation
- 📊 Rolling demand statistics (no leakage)
- 🐍 Python 3.14 compatible
- 🌐 Flask API with useful endpoints

---

## 📦 Files

The repository contains:

- `preprocess_sales.py` — main preprocessing script  
- `requirements.txt` — minimal dependencies  
- `run_preprocess.sh` — helper script  
- `README_preprocessing.md` — preprocessing guide

---

## 💻 Installation

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

---

## On Windows (PowerShell):

```bash
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

---

## ▶️ Run Preprocessing
bash run_preprocess.sh

🧠 Flask API (MVP)
To start the API:
bash run_preprocess.sh

Base URL: http://localhost:8080

---

API Endpoints
Method	Path	Description
GET	/health	Health check
GET	/pipeline	Run pipeline status or trigger
POST	/preprocess	Data preprocessing
POST	/train-evaluate	Train & evaluate models
POST	/report-last	Get last report
POST	/run-all	Run full pipeline

---


🐳 Docker Support Build Image:  docker build -t demand-python-314:latest .
Run Locally:  docker run --rm -p 8080:8080 demand-python-314:latest

☁️ Deploy to Google Cloud Run
Prerequisites:
Google Cloud SDK installed
Billing enabled
Valid GCP project selected
Deploy Steps :
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/demand-python-314

gcloud run deploy demand-python-314 \
  --image gcr.io/YOUR_GCP_PROJECT_ID/demand-python-314 \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080

📁 Outputs
After running preprocessing, you’ll get:
sales_transactions_2017_2019.csv.gz
item_month_agg_2017_2019.csv
train_item_month_2017_2019_cutoff_2019-04.csv
test_item_month_2017_2019_start_2019-05.csv
item_month_agg_2017_2019_with_roll.csv
train_item_month_2017_2019_cutoff_2019-04_with_roll.csv
test_item_month_2017_2019_start_2019-05_with_roll.csv

