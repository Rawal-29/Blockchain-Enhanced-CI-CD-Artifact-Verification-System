from fastapi import FastAPI
from routes import store_routes
from routes import verify_routes

app = FastAPI(title="Blockchain CI/CD Verification API")

# Register routers
app.include_router(store_routes.router) 
app.include_router(verify_routes.router)

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Blockchain Verification API is operational."}