from fastapi import FastAPI

app = FastAPI(title="Helpdesk API")
@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}