from fastapi import FastAPI
from routes.hash_routes import router as hash_router
from routes.store_routes import router as store_router
from routes.verify_routes import router as verify_router

app = FastAPI(title="BlockCICD Verification API")

app.include_router(hash_router, prefix="/hash", tags=["Hash"])
app.include_router(store_router, prefix="/store", tags=["Store"])
app.include_router(verify_router, prefix="/verify", tags=["Verify"])

@app.get("/")
def root():
    return {"message": "BlockCICD API Running"}
