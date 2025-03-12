import os
import base64
import json
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

from flask_cors import CORS
from flask import Flask, jsonify
import smtplib
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
import time
import schedule
import threading

# from db import get_connection 
from db import fetch_data_from_db

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)
# ✅ MongoDB Connection
# MONGO_URI = "mongodb+srv://devangsawant127:dev9930@cluster0.ow3la.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(MONGO_URI)
# db = client["events_db"]
# events_collection = db["events"]
# master_data_collection = db["master_data"]  # Collection where emails are stored


# # ✅ Integrated Email (from .env)
# INTEGRATED_EMAIL = os.getenv("EMAIL_USER")  # This email will receive event notifications

# # ✅ Google Calendar API Setup
# def get_calendar_service():
#     SERVICE_ACCOUNT_JSON_BASE64 = os.getenv("GOOGLE_CREDENTIALS_JSON_BASE64")
#     creds_dict = json.loads(base64.b64decode(SERVICE_ACCOUNT_JSON_BASE64).decode("utf-8"))
#     SCOPES = ["https://www.googleapis.com/auth/calendar"]
#     creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
#     return build("calendar", "v3", credentials=creds)

# CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

# # ✅ Function to Add Event to Google Calendar
# def add_event_to_calendar(event_name, event_date):
#     service = get_calendar_service()

#     event = {
#         "summary": event_name,
#         "description": f"Reminder: {event_name} is happening!",
#         "start": {"date": event_date},
#         "end": {"date": event_date},
#         "visibility": "public",
#     }

#     service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
#     print(f"✅ Event added to Google Calendar: {event_name} on {event_date}")

# # ✅ Function to Send Email
# def send_email(subject, body, recipient):
#     try:
#         msg = MIMEMultipart()
#         msg["From"] = INTEGRATED_EMAIL
#         msg["To"] = recipient
#         msg["Subject"] = subject
#         msg.attach(MIMEText(body, "html"))

#         with SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT", 587))) as server:
#             server.starttls()
#             server.login(INTEGRATED_EMAIL, os.getenv("EMAIL_PASS"))
#             server.sendmail(INTEGRATED_EMAIL, recipient, msg.as_string())
#             print(f"✅ Email sent to {recipient}")

#     except Exception as e:
#         print(f"❌ Email sending failed: {e}")


# @app.route('/get_dropdown_values', methods=['POST'])
# def get_dropdown_values():
#     try:
#         data = request.get_json()
#         project_name = data.get("project_name")
#         dropdown_assignment = data.get("dropdown_assignment")

#         if not project_name or not dropdown_assignment:
#             return jsonify({"error": "Project name and dropdown assignment are required"}), 400

#         dropdowns = {}

#         conn = get_connection(project_name)
#         cursor = conn.cursor()

#         # Loop through dropdown assignments to get values
#         for column, mapping in dropdown_assignment.items():
#             table, value_column = mapping.split(".")
#             id_column = "id"  # Assuming the primary key is named 'id'

#             # Fetch ID and value from master table
#             query = f"SELECT {id_column}, {value_column} FROM {table} WHERE deleted = 'FALSE'"
            
#             if column == "full_name" or column == "resource_name" or column == "mentor_name":
#                 query += " AND (dol IS NULL OR dol = '')"  # ✅ Allow employees with NULL or empty dol

#             if column == "mentor_name":
#                 query = query + f""" AND designation::TEXT IN (
#                                 SELECT id::TEXT FROM designation 
#                                 WHERE designation IN ('Project Manager', 'Senior Data Analyst', 'Founder')
#                             );
#                             """
#             # print(query)
#             cursor.execute(query)
#             rows = cursor.fetchall()

#             # Store as a list of dictionaries with 'id' and 'name'
#             dropdowns[column] = [{"id": row[0], "name": row[1]} for row in rows]
#             # print(f"🛠️ Fetching dropdown for {column}: {dropdowns[column]}")  # ✅ Debugging log


#         release_connection(project_name, conn)
#         return jsonify({"dropdowns": dropdowns}), 200

#     except Exception as e:
#         error_message = str(e)
#         return jsonify({"error": error_message}), 500

# def get_scheduled_emails(event_date=None, event_time=None, event_frequency=None):
#     query = {}

#     if event_date:
#         query["event_date"] = event_date
#     if event_time:
#         query["event_time"] = event_time
#     if event_frequency:
#         query["event_frequency"] = event_frequency

#     results = db["email_schedule_table"].find(query)
#     return list(results)  # Convert cursor to list for processing

# @app.route("/add_event", methods=["POST"])
# def add_event():
#     data = request.json
#     event_name = data.get("event_name")
#     event_date = data.get("event_date")

#     if not event_name or not event_date:
#         return jsonify({"error": "Missing event details"}), 400

#     # ✅ Store event in MongoDB
#     event_data = {"name": event_name, "event_date": event_date}
#     events_collection.insert_one(event_data)

#     # ✅ Sync to Google Calendar
#     add_event_to_calendar(event_name, event_date)

#     # ✅ Fetch all user emails from master_data
#     users = master_data_collection.find({}, {"email": 1})  # Get only email field
#     user_emails = [user["email"] for user in users if "email" in user]

#     # ✅ Send Email Notification to All Users
#     subject = f"📅 New Event: {event_name}"
#     body = f"<p>Reminder: '<b>{event_name}</b>' is scheduled for {event_date}.</p>"

#     for email in user_emails:
#         send_email(subject, body, email)  # Send email to each user

#     return jsonify({"message": "Event added successfully & emails sent!"})

@app.route("/send_mail", methods=["POST", "GET"])
def send_mail():
    """Fetch users with expiring subscriptions and send email notifications."""
    conn = fetch_data_from_db.get_connection()
    cursor = conn.cursor()

    query = """
    SELECT activation_date, user_name, email, expiry_date
    FROM send_email;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # ✅ Properly release connection
    fetch_data_from_db.release_connection(conn)

    today = date.today()
    email_list = []

    for row in rows:
        activation_date, user_name, email, expiry_date_str = row
        expiry_date = datetime.strptime(expiry_date_str, "%d/%m/%Y").date()
        days_left = (expiry_date - today).days

        if days_left in [1, 7, 15, 30]:
            email_list.append((user_name, email, days_left))

    for user_name, email, days_left in email_list:
        send_email_notification(user_name, email, days_left)

    print(f"Emails sent: {len(email_list)}")
    return jsonify({"emails_sent": len(email_list)})

def send_email_notification(user_name, recipient_email, days_left):
    """Send an email notification."""
    sender_email = "dataastraa.it@gmail.com"
    sender_password = "rkqz xniw xbgt vdnp"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = "Subscription Renewal Reminder"

    email_body = f"""
    Hi {user_name},

    This is a friendly reminder that your subscription is expiring in {days_left} days.
    Please renew it to continue enjoying our services.

    Best regards,
    Your Company
    """
    msg.attach(MIMEText(email_body, "plain"))

    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

    print(f"Email sent to {recipient_email}")

# ✅ Serve the HTML frontend
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

