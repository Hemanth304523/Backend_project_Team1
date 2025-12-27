from fastapi import FastAPI
from app.routers import ai_tools, reviews, admin

app = FastAPI(title="AI Tool Finder Backend")

# Include routers
app.include_router(ai_tools.router)
app.include_router(reviews.router)
app.include_router(admin.router)

@app.get("/")
def root():
<<<<<<< HEAD
    return {"message": "Welcome to AI Tool Finder Backend"}
=======
    return {"message": "Welcome to AI Tool Finder Backend"}
>>>>>>> e1df838ce77c58b6d2cf61546d81d077f00f7451
