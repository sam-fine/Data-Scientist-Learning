import uvicorn


"""
The below command tells Uvicorn to start your application locally, located in the main.py file, on port 5000, 
and to automatically reload the server whenever you modify the code.
"""

if __name__ == "__main__":
    uvicorn.run("webhook:app", host="0.0.0.0", port=5000, reload=True)