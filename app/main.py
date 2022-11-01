from fastapi import FastAPI
import uvicorn
from authentication.routes import router as auth_router

app = FastAPI()


app.include_router(auth_router)


@app.get("/")
async def home():
    return {"data": "Home Page"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
