from fastapi import FastAPI
from app.routers import ai_tools, reviews, admin

app = FastAPI(title="AI Tool Finder Backend")

# Include routers
app.include_router(ai_tools.router)
app.include_router(reviews.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Welcome to AI Tool Finder Backend"}
