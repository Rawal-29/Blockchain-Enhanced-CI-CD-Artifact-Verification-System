from fastapi import FastAPI
from mangum import Mangum
from routes import store_routes, verify_routes

app = FastAPI(title="Blockchain CI/CD Verification API")

app.include_router(store_routes.router)
app.include_router(verify_routes.router)

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Blockchain Verification API is operational."}

# AWS Lambda Handler
handler = Mangum(app)