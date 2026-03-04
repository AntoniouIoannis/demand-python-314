# Demand Python 314

## 📌 Project Overview

This repository contains a sales preprocessing pipeline and a minimal Flask API.  
It helps you standardize and aggregate sales data (2017–2019), create rolling statistics,  
and expose API endpoints for triggering the pipeline and related tasks.

---

## 🚀 Key Features

- 🧮 Sales data preprocessing and cleaning
- 📅 Aggregation of sales data to product-month level
- 🔄 Rolling statistics generation (no leakage)
- 🐍 Flask API with multiple endpoints
- 🐳 Docker support for local testing
- ☁️ Google Cloud Run deployment ready

---

## 📦 Repository Contents

- `preprocess_sales.py` — main pipeline script  
- `requirements.txt` — minimal Python dependencies  
- `run_preprocess.sh` — helper shell script  
- `README_preprocessing.md` — detailed preprocessing guide  
- `app.py` — Flask API implementation

---

## 💻 Installation

**Create & activate virtual environment (Linux / MacOS):**
```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

**On Windows (PowerShell):**

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## ▶️ Running the Pipeline

To run the preprocessing pipeline:

```bash
bash run_preprocess.sh
```

---

## 🧠 Flask API (MVP)

Bring up the API server:

```bash
python app.py
```

The base URL is:

```
http://localhost:8080
```

### Available Endpoints

| Method | Path              | Purpose                            |
| ------ | ----------------- | ---------------------------------- |
| GET    | `/health`         | API health check                   |
| GET    | `/pipeline`       | Trigger or inspect pipeline status |
| POST   | `/preprocess`     | Run data preprocessing             |
| POST   | `/train-evaluate` | Train and evaluate models          |
| POST   | `/report-last`    | Get latest report                  |
| POST   | `/run-all`        | Run full pipeline workflow         |

**Example (PowerShell):**

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/run-all" `
  -ContentType "application/json" ^
  -Body (@{
      sales2017 = "./data/sales 2017.xlsx"
      sales2018 = "./data/sales 2018.xlsx"
      sales2019 = "./data/sales 2019.xlsx"
      outdir = "./data"
  } | ConvertTo-Json)
```

---

## 🐳 Docker Support

**Build Docker image:**

```bash
docker build -t demand-python-314:latest .
```

**Run locally in container:**

```bash
docker run --rm -p 8080:8080 demand-python-314:latest
```

---

## ☁️ Deploy to Google Cloud Run

Make sure you have:

* ✔️ Google Cloud SDK installed
* ✔️ Billing enabled
* ✔️ Selected GCP project

Steps:

```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID

gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com

gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/demand-python-314

gcloud run deploy demand-python-314 \
  --image gcr.io/YOUR_GCP_PROJECT_ID/demand-python-314 \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```

**Test deployment:**

```bash
curl https://YOUR_CLOUD_RUN_URL/health
```

---

## 📁 Output Files

After running preprocessing (with default `outdir`), the following are created:

* `sales_transactions_2017_2019.csv.gz`
* `item_month_agg_2017_2019.csv`
* `train_item_month_2017_2019_cutoff_2019-04.csv`
* `test_item_month_2017_2019_start_2019-05.csv`
* `item_month_agg_2017_2019_with_roll.csv`
* `train_item_month_2017_2019_cutoff_2019-04_with_roll.csv`
* `test_item_month_2017_2019_start_2019-05_with_roll.csv

```


[1]: https://github.com/AntoniouIoannis/demand-python-314/blob/main/README.md "demand-python-314/README.md at main · AntoniouIoannis/demand-python-314 · GitHub"
