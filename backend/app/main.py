from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ocr import router as ocr_router

app = FastAPI(
    title="UST McDelivery API",
    description="OCR-based McDonald's receipt processing for HKUST delivery platform",
    version="0.1.0",
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ocr_router)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "UST McDelivery API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
