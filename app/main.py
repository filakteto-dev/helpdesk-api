from fastapi import FastAPI

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.tickets import router as tickets_router

app = FastAPI(title="Helpdesk API")

app.include_router(auth_router)
app.include_router(tickets_router)

@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

