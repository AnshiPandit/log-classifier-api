# Log Classifier API

A backend API that classifies log messages into ERROR, WARNING, INFO, or UNKNOWN using a machine learning pipeline. Built with FastAPI and scikit-learn.

## What it does

- Classifies log messages using TF-IDF vectorization + Logistic Regression
- Persists every classification to PostgreSQL with timestamps
- Supports single and bulk classification
- Serves a live dashboard to visualize log distribution and browse all logs
- Fully containerized with Docker

## Tech stack

- **FastAPI** — REST API with automatic validation via Pydantic
- **scikit-learn** — TF-IDF + Logistic Regression classification pipeline
- **SQLAlchemy** — ORM for database persistence
- **PostgreSQL / SQLite** — PostgreSQL in production, SQLite locally via env var
- **Docker** — containerized for consistent deployment anywhere

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/classify` | Classify a single log message |
| POST | `/classify/bulk` | Classify multiple logs in one request |
| GET | `/logs` | Fetch all stored classifications |
| GET | `/dashboard` | Visual dashboard with charts and log browser |

## Run locally

```bash
git clone https://github.com/AnshiPandit/log-classifier-api.git
cd log-classifier-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit `http://localhost:8000/dashboard`

## Run with Docker

```bash
docker build -t log-classifier-api .
docker run -p 8000:8000 log-classifier-api
```

## Configuration

Set `DATABASE_URL` environment variable to use PostgreSQL. Falls back to SQLite automatically if not set.

DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

## Example usage

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"message": "ERROR: database connection failed"}'

curl -X POST "http://localhost:8000/classify/bulk" \
  -H "Content-Type: application/json" \
  -d '{"messages": ["ERROR: disk full", "Server started", "WARNING: high memory"]}'
```