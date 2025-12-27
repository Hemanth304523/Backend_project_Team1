from fastapi import FastAPI

import model
from database import engine


from routers import auth,admin,user,tool,review
app=FastAPI()



model.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(tool.router)
app.include_router(review.router)

