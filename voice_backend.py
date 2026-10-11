import pyttsx3
import speech_recognition as sr
import requests
import webbrowser
from bs4 import BeautifulSoup
import os

# ---------- CONFIG ----------
BASE_URL = "http://localhost/email_for_Blind"
FETCH_INBOX_API = f"{BASE_URL}/fetch_inbox.php"
FETCH_SENT_API  = f"{BASE_URL}/fetch_sent.php"
SEND_EMAIL_API  = f"{BASE_URL}/send_email.php"
SPEAK_API       = f"{BASE_URL}/speak.php"   # ✅ NEW for browser speech sync
MAIN_PAGE = f"{BASE_URL}/main.html"
INDEX_PAGE = f"{BASE_URL}/index.html"
CREATE_ACCOUNT_PAGE = f"{BASE_URL}/signup.html"
LOGIN_PAGE = f"{BASE_URL}/login.html"
COMPOSE_PAGE = f"{BASE_URL}/compose.html"

# ---------- TTS + STT ----------
engine = pyttsx3.init()
engine.setProperty('rate', 160)
recognizer = sr.Recognizer()

def speak(text):
    """
    Speaks locally using pyttsx3 and also sends the same text to the browser
    so that it can be spoken there using the Web Speech API.
    """
    print(f"[TTS] {text}")
    engine.say(text)
    engine.runAndWait()

    # ✅ NEW: Send text to browser for speech
    try:
        requests.post(SPEAK_API, data={"text": text})
    except Exception as e:
        print(f"[WARN] Could not send text to browser: {e}")

def listen(prompt=None, retries=3):
    if prompt:
        speak(prompt)
    for _ in range(retries):
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.6)
                speak("Listening...")
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
                text = recognizer.recognize_google(audio)
                print(f"[STT] {text}")
                return text.strip()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except sr.WaitTimeoutError:
            speak("No speech detected.")
    return None

def confirm_input(value, field_name):
    speak(f"You said {value} for {field_name}. Say yes to confirm, no to retry.")
    while True:
        response = listen()
        if response and "yes" in response.lower():
            return True
        elif response and "no" in response.lower():
            return False
        else:
            speak("Please say yes or no.")

# ---------- BACKEND HELPERS ----------
def fetch_emails(folder, user="shriyajedhe984@gmail.com"):
    """Fetch emails from PHP and parse HTML."""
    try:
        url = FETCH_INBOX_API if folder == "inbox" else FETCH_SENT_API
        r = requests.get(url, params={"user": user})
        r.raise_for_status()
        html = r.text

        soup = BeautifulSoup(html, "html.parser")
        emails = []
        for li in soup.find_all("li"):
            b_tags = li.find_all("b")
            sender = subject = message = "Unknown"
            starred = False
            star_span = li.find("span", class_="star")
            if star_span and "★" in star_span.get_text():
                starred = True
            for b in b_tags:
                label = b.get_text(strip=True)
                value = b.next_sibling
                if value:
                    if isinstance(value, str):
                        value = value.strip()
                    else:
                        value = value.get_text(strip=True)
                if label == "From:":
                    sender = value
                elif label == "Subject:":
                    subject = value
                elif label == "Message:":
                    message = value
            emails.append({
                "sender": sender,
                "subject": subject,
                "message": message,
                "starred": starred
            })
        return emails
    except Exception as e:
        print("Error fetching emails:", e)
        speak(f"Unable to fetch emails from {folder}.")
        return []

def send_email(recipient, subject, message, attachment_path=""):
    try:
        files = {}
        if attachment_path and os.path.exists(attachment_path):
            files['attachment'] = open(attachment_path, 'rb')
        data = {"recipient": recipient, "subject": subject, "message": message}
        r = requests.post(SEND_EMAIL_API, data=data, files=files)
        if files:
            files['attachment'].close()
        r.raise_for_status()
        resp = r.json()
        if resp.get("status") == "success":
            speak(resp.get("message"))
        else:
            speak("Failed to send email.")
        return resp
    except Exception as e:
        print("Error sending email:", e)
        speak("Failed to send email.")
        return None

# ---------- VOICE FEATURES ----------
def open_page(url, message="Opening page"):
    webbrowser.open(url)
    speak(message)

def read_folder(folder):
    emails = fetch_emails(folder)
    if not emails:
        speak(f"No emails found in {folder}.")
        return
    # Prioritize starred emails first
    starred_emails = [e for e in emails if e['starred']]
    normal_emails = [e for e in emails if not e['starred']]
    sorted_emails = starred_emails + normal_emails

    speak(f"You have {len(emails)} emails in {folder}.")
    for i, mail in enumerate(sorted_emails, start=1):
        prefix = "Starred " if mail['starred'] else ""
        speak(f"{prefix}Email {i}. From {mail['sender']}. Subject {mail['subject']}.")

def compose_email():
    open_page(COMPOSE_PAGE, "Opening compose page.")

# ---------- VOICE-ASSISTED ACCOUNT CREATION ----------
def create_account():
    fields = ["name", "email", "password", "confirm password"]
    user_data = {}

    for field in fields:
        while True:
            value = listen(f"Please say your {field}.")
            if not value:
                speak(f"Could not understand your {field}. Please try again.")
                continue
            if confirm_input(value, field):
                user_data[field] = value
                break

    if user_data["password"] != user_data["confirm password"]:
        speak("Password and confirm password do not match. Let's try again.")
        return create_account()

    try:
        response = requests.post(f"{BASE_URL}/create_account.php", data={
            "name": user_data["name"],
            "email": user_data["email"],
            "password": user_data["password"],
            "confirm_password": user_data["confirm password"]
        })
        if response.status_code == 200:
            speak("Account creation request sent successfully!")
            print("[INFO]", response.text)
        else:
            speak("Failed to create account. Server returned an error.")
            print("[ERROR]", response.status_code, response.text)
    except Exception as e:
        speak("Failed to reach the server. Please check your connection.")
        print("[EXCEPTION]", e)

# ---------- MAIN DASHBOARD ----------
def main():
    open_page(MAIN_PAGE, "Welcome to iMails voice assistant.")
    while True:
        command = listen("Say 'create account', 'login', 'dashboard' or 'exit'.")
        if not command:
            continue
        command = command.lower()
        print(f"[DEBUG] Recognized command: {command}")

        if any(word in command for word in ["create account", "signup", "sign up"]):
            open_page(CREATE_ACCOUNT_PAGE, "Opening create account page.")
        elif any(word in command for word in ["login", "log in"]):
            open_page(LOGIN_PAGE, "Opening login page.")
        elif any(word in command for word in ["dashboard", "inbox"]):
            open_page(INDEX_PAGE, "Opening email dashboard.")
            dashboard_loop()
        elif any(word in command for word in ["exit", "quit", "close"]):
            speak("Goodbye!")
            break
        else:
            speak("Command not recognized. Please repeat.")

def dashboard_loop():
    while True:
        command = listen("Say 'read inbox', 'read sent', 'compose email', or 'go back'.")
        if not command:
            continue
        command = command.lower()
        print(f"[DEBUG] Dashboard command: {command}")

        if any(word in command for word in ["inbox", "read inbox"]):
            read_folder("inbox")
        elif any(word in command for word in ["sent", "read sent"]):
            read_folder("sent")
        elif any(word in command for word in ["compose", "compose email"]):
            compose_email()
        elif any(word in command for word in ["back", "go back", "return"]):
            speak("Returning to main menu.")
            return
        else:
            speak("Unknown option. Please say again.")

if __name__ == "__main__":
    main()
