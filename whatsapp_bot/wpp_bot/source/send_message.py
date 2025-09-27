from twilio.rest import Client
import os
from dotenv import load_dotenv

"""
This module provides a function for sending messages using the Twilio API.
"""

# Load environment variables from the .env file.
load_dotenv()

def send_message(to: str, message: str) -> None:
    """
    Sends a WhatsApp message using the Twilio REST API client.

    This function authenticates with Twilio using credentials from environment
    variables and sends a text message to a specified recipient from your
    Twilio WhatsApp number.

    You would use this for scenarios where you need to send a message to a user at a later time or from a different
    part of your application. (MessagingResponse() in webhook is for immediate responses)
    LIST USE CASES

    Args:
        to: The recipient's WhatsApp number (e.g., 'whatsapp:+1234567890').
        message: The text content of the message to be sent.

    Returns:
        None. Prints a success or failure message to the console.

    Raises:
        TwilioException: If the message fails to send due to an API error.
    """
    # Get Twilio credentials from environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    # Initialize the Twilio client
    client = Client(account_sid, auth_token)

    try:
        # The from_ number is the Twilio WhatsApp number
        message = client.messages.create(
            body=message,
            from_='whatsapp:YOUR_TWILIO_WHATSAPP_NUMBER',
            to=to
        )
        print(f"Message sent to {to}. SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send message: {e}")