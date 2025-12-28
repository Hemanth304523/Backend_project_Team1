from fastapi import FastAPI
from routers import auth,review,tool,user
from database import engine
import model

app = FastAPI(title="AI Tool Finder Backend")

model.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(review.router)
app.include_router(tool.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Welcome to AI Tool Finder Backend"}
