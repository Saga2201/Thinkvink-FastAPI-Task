from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def getHelloWorld():
    return "Hell world!"