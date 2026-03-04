# Sales preprocessing package (2017–2019)

This package reads the 2017–2019 sales Excel files, standardizes them, aggregates to product-month,
completes the product-month grid, performs an 80/20 chronological split, and creates rolling statistics
(no leakage) over ordered demand.

## Files
- `preprocess_sales.py` — main pipeline script
- `requirements.txt` — minimal Python dependencies
- `run_preprocess.sh` — convenience runner (edit input paths if needed)
- `README_preprocessing.md` — this guide

## Install
```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows (PowerShell):
```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
```bash
bash run_preprocess.sh
```

## Flask API (MVP)
Run:
```bash
python app.py
```

Base URL: `http://localhost:8080`

Endpoints:
- `GET /health`
- `GET /pipeline`
- `POST /preprocess`
- `POST /train-evaluate`
- `POST /report-last`
- `POST /run-all`

Example (PowerShell):
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/run-all" -ContentType "application/json" -Body (@{
  sales2017 = "./data/sales 2017.xlsx"
  sales2018 = "./data/sales 2018.xlsx"
  sales2019 = "./data/sales 2019.xlsx"
  outdir = "./data"
} | ConvertTo-Json)
```

## Docker (Cloud Run-ready)
Build image:
```bash
docker build -t demand-python-314:latest .
```

Run locally in container:
```bash
docker run --rm -p 8080:8080 demand-python-314:latest
```

## Deploy to Google Cloud Run
Prerequisites: Google Cloud SDK installed, project selected, and billing enabled.

```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/demand-python-314
gcloud run deploy demand-python-314 --image gcr.io/YOUR_GCP_PROJECT_ID/demand-python-314 --platform managed --region europe-west1 --allow-unauthenticated --port 8080
```

After deploy, test:
```bash
curl https://YOUR_CLOUD_RUN_URL/health
```

## Outputs (written to `--outdir`, default `/mnt/data`)
- `sales_transactions_2017_2019.csv.gz`
- `item_month_agg_2017_2019.csv`
- `train_item_month_2017_2019_cutoff_2019-04.csv`
- `test_item_month_2017_2019_start_2019-05.csv`
- `item_month_agg_2017_2019_with_roll.csv`
- `train_item_month_2017_2019_cutoff_2019-04_with_roll.csv`
- `test_item_month_2017_2019_start_2019-05_with_roll.csv`
