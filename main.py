from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from database import SessionLocal, LogRecord

app = FastAPI()

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

@app.get("/")
def root():
    return {"status": "log classifier running"}

@app.post("/classify")
def classify(log: LogEntry):
    label = model.predict([log.message])[0]

    # Save to database
    db = SessionLocal()
    record = LogRecord(message=log.message, label=label)
    db.add(record)
    db.commit()
    db.close()

    return {"message": log.message, "label": label}

@app.get("/logs")
def get_logs():
    db = SessionLocal()
    logs = db.query(LogRecord).all()
    db.close()
    return [{"id": l.id, "message": l.message, "label": l.label, "timestamp": l.timestamp} for l in logs]