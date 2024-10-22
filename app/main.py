# app.main.py
from app.routers import product
from fastapi import FastAPI, status 
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import RedirectResponse



app = FastAPI(
    title="Product Management API",
    docs_url="/api/docs",
    description="API for managing products with CRUD operations",
    version="/api/v1",
)

# Routers
app.include_router(product.router, prefix="/api/v1", tags=["products"])



# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
@app.get(
    "/",
    include_in_schema=False,
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
)
def index():
    return "/api/docs"
