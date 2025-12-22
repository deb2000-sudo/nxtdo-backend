from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from nxtdo-backend!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/Testing")
def test_endpoint():
    return {"message": "This is a Testing endpoint from feature branch!", "environment": "preview"}

@app.get("/Checking")
def test_endpoint():
    return {"message": "This is a Checking endpoint from checking!", "environment": "preview"}