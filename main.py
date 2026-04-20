from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from database import SessionLocal, LogRecord
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


# Training data — logs and their correct labels
TRAINING_DATA = [
    ("ERROR: database connection failed", "ERROR"),
    ("CRITICAL: out of memory", "ERROR"),
    ("Exception in thread main", "ERROR"),
    ("fatal error encountered", "ERROR"),
    ("WARNING: disk space low", "WARNING"),
    ("deprecated function called", "WARNING"),
    ("response time slow", "WARNING"),
    ("warn: retry attempt 3", "WARNING"),
    ("Server started successfully", "INFO"),
    ("User login completed", "INFO"),
    ("connected to database", "INFO"),
    ("info: job completed", "INFO"),
]


texts = [item[0] for item in TRAINING_DATA]
labels = [item[1] for item in TRAINING_DATA]

# Build and train the model
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression())
])
model.fit(texts, labels)


class LogEntry(BaseModel):
    message: str

class BulkLogRequest(BaseModel):
    messages: list[str]


# This is what runs in the background after response is sent
def save_to_db(message: str, label: str):
    db = SessionLocal()
    record = LogRecord(message=message, label=label)
    db.add(record)
    db.commit()
    db.close()   


def save_bulk_to_db(results: list[dict]):
    db = SessionLocal()
    for item in results:
        record = LogRecord(message=item["message"], label=item["label"])
        db.add(record)
    db.commit()
    db.close()


@app.get("/")
def root():
    return {"status": "log classifier running"}


@app.post("/classify")
def classify(log: LogEntry, background_tasks: BackgroundTasks):
    label = model.predict([log.message])[0]
    background_tasks.add_task(save_to_db, log.message, label)
    return {"message": log.message, "label": label}


@app.post("/classify/bulk")
def classify_bulk(request: BulkLogRequest, background_tasks: BackgroundTasks):
    results = [
        {"message": msg, "label": model.predict([msg])[0]}
        for msg in request.messages
    ]
    background_tasks.add_task(save_bulk_to_db, results)
    return {"results": results, "total": len(results)}


@app.get("/logs")
def get_logs():
    db = SessionLocal()
    logs = db.query(LogRecord).all()
    db.close()
    return [{"id": l.id, "message": l.message, "label": l.label, "timestamp": l.timestamp} for l in logs]


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return open("static/index.html").read()

@app.get("/db-check")
def db_check():
    import os
    url = os.environ.get("DATABASE_URL", "NOT SET")
    if "neon.tech" in url:
        return {"database": "neon_postgresql", "url": url}
    elif url == "NOT SET":
        return {"database": "sqlite_local", "url": url}
    else:
        return {"database": "other", "url": url}

