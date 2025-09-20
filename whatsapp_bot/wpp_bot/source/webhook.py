# New code with Twilio
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from fastapi import FastAPI, Request, HTTPException, Response, Query
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs

"""
A webhook is a mechanism that allows an application to receive real-time notifications from other applications 
about specific events.

FastAPI is a modern, high-performance web framework for building APIs with Python.

This module defines the main FastAPI application for a WhatsApp bot.
    
It handles incoming webhooks from the Twilio API, validates the requests for security,
and processes incoming messages to send an automated response.

https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests#create-a-custom-decorator
"""


# Load environment variables from the .env file.
load_dotenv()

# Initialize the FastAPI application.
app = FastAPI()

# async def initiates coroutine

# Health check
@app.get("/")
async def home():
    return {"message": "API is up"}


@app.post("/webhook")
async def handle_webhook(request: Request):
    form = await request.form()
    form_dict = dict(form)

    validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))

    # url = str(request.url)
    # print("Validating against URL:", url)

    if not validator.validate(request.url, request.form, request.headers.get('X-TWILIO-SIGNATURE', '')):
        print("Signature mismatch")
        print("Signature header:", request.headers.get('X-TWILIO-SIGNATURE', ''))
        print("Form dict:", form_dict)
        raise HTTPException(status_code=403, detail="Invalid signature")

    sender = form_dict.get("From")
    body = form_dict.get("Body")

    resp = MessagingResponse()
    resp.message(f"Hey {sender}, your bot is up! You said: {body}")
    return Response(content=str(resp), media_type="application/xml")