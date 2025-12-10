from fastapi import FastAPI
from mangum import Mangum
from routes import store_routes, verify_routes

app = FastAPI(title="BlockCICD API")
app.include_router(store_routes.router)
app.include_router(verify_routes.router)
handler = Mangum(app)