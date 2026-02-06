from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(title="AURA Agentic AI Backend")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
