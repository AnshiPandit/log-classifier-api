from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class LogEntry(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "log classifier running"}

def classify_log(message:str) -> str:
    message_lower = message.lower()
    if any(word in message_lower for word in ["error", "exception", "faied", "critical", "fatal"]):
        return "ERROR"
    elif any(word in message_lower for word in ["warn", "warning", "deprecated", "slow"]):
        return "WARNING"
    elif any(word in message_lower for word in ["info", "started", "connected", "success", "completed"]):
        return "INFO"
    else:
        return "UNKNOWN"

@app.post("/classify")
def classify(log: LogEntry):
    label = classify_log(log.message)
    return {"message": log.message, "label": label}