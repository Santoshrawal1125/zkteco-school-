import logging
import firebase_admin
from firebase_admin import credentials, messaging
import os

logger = logging.getLogger('core')  # Use your existing logger or create a new one

# Load the service account credentials (load only once)
if not firebase_admin._apps:
    cred_path = os.path.join(os.path.dirname(__file__), 'firebase_credentials.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    logger.info("🔥 Firebase Admin SDK initialized.")


def send_fcm_notification(token, title, body):
    logger.info(f"🔔 Preparing to send notification to token: {token}")
    logger.info(f"Title: {title}")
    logger.info(f"Body: {body}")

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )

        response = messaging.send(message)
        logger.info(f"✅ Notification sent successfully. Response: {response}")

    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}", exc_info=True)
