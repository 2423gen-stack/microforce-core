import os
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Microforce MCP/Backend Server")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Microforce Backend",
        "db_host": os.getenv("DB_HOST", "localhost")
    }

if __name__ == "__main__":
    # In docker, bind to 0.0.0.0
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
