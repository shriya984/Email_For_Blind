

import pyttsx3
import speech_recognition as sr
import requests
import webbrowser
import os
import re
import time

# ---------- CONFIG ----------
BASE_URL = "http://localhost/email_for_Blind"
FETCH_INBOX_API = f"{BASE_URL}/fetch_inbox.php"
FETCH_SENT_API  = f"{BASE_URL}/fetch_sent.php"
SEND_EMAIL_API  = f"{BASE_URL}/send_email.php"
CHECK_EMAIL_API = f"{BASE_URL}/check_email.php"
CREATE_ACCOUNT_API = f"{BASE_URL}/create_account.php"
LOGIN_API = f"{BASE_URL}/login.php"

INDEX_PAGE = f"{BASE_URL}/index.html"
CREATE_ACCOUNT_PAGE = f"{BASE_URL}/create_account.html"
LOGIN_PAGE = f"{BASE_URL}/login.html"
COMPOSE_PAGE = f"{BASE_URL}/compose.html"

# ---------- TTS + STT ----------
engine = pyttsx3.init()
engine.setProperty('rate', 160)
recognizer = sr.Recognizer()

def speak(text):
    """Speak locally using pyttsx3 and print text for debugging."""
    print(f"[TTS] {text}")
    engine.say(text)
    engine.runAndWait()

def listen(prompt=None, retries=3):
    """Listen via microphone with optional prompt and improved recognition."""
    if prompt:
        speak(prompt)
    for attempt in range(retries):
        try:
            with sr.Microphone() as source:
                # Increase ambient noise adjustment
                recognizer.adjust_for_ambient_noise(source, duration=1.2)
                recognizer.dynamic_energy_threshold = True
                speak("Listening now...")
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
                text = recognizer.recognize_google(audio)
                print(f"[STT] {text}")
                return text.strip()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Please speak clearly.")
        except sr.WaitTimeoutError:
            speak("No speech detected. Please speak now.")
        except Exception as e:
            print("[STT ERROR]", e)
            speak("Speech recognition failed. Try again.")
    speak("Max retries reached. Moving on.")
    return None


def confirm_input(value, field_name):
    """Ask user to confirm input value."""
    speak(f"You said {value} for {field_name}. Say yes to confirm, no to retry.")
    while True:
        response = listen()
        if response and "yes" in response.lower():
            return True
        elif response and "no" in response.lower():
            return False
        else:
            speak("Please say yes or no.")

def normalize_email_spoken(text):
    """Convert spoken email to proper format: 'john dot doe at gmail dot com' -> john.doe@gmail.com"""
    if not text:
        return ""
    text = text.lower()
    replacements = [
        (r'\s+at\s+', '@'),
        (r'\s+dot\s+', '.'),
        (r'\s+underscore\s+', '_'),
        (r'\s+dash\s+', '-'),
        (r'\s+hyphen\s+', '-'),
        (r'\s+period\s+', '.'),
        (r'\s+', '')  # remove extra spaces
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    text = re.sub(r'\.+', '.', text)  # remove repeated dots
    return text

# ---------- PAGE HANDLERS ----------
def open_page(url, message="Opening page"):
    webbrowser.open(url)
    speak(message)

# ---------- ACCOUNT CREATION ----------
def create_account():
    """Voice-driven create account flow with proper email check."""
    speak("Starting account creation. Opening create account page.")
    open_page(CREATE_ACCOUNT_PAGE)

    # ----- STEP 1: Name -----
    while True:
        name = listen("Please say your full name.")
        if not name:
            speak("Could not understand. Let's try again.")
            continue
        if confirm_input(name, "name"):
            break

    # ----- STEP 2: Email -----
    while True:
        raw_email = listen("Please say your email. Example: user at example dot com.")
        if not raw_email:
            speak("Could not understand email. Try again.")
            continue

        email = normalize_email_spoken(raw_email)
        speak(f"I understood your email as {email}.")

        if not confirm_input(email, "email"):
            continue

        # Check if email exists
        try:
            r = requests.get(CHECK_EMAIL_API, params={"email": email}, timeout=6)
            r.raise_for_status()
            j = r.json()
            if j.get("exists"):
                speak("This email already exists. Redirecting you to dashboard.")
                dashboard(email)  # ✅ correctly call dashboard with email
                return  # exit create_account
            else:
                break  # email is available
        except Exception as e:
            print("[ERROR] check_email failed:", e)
            speak("Failed to check email. Please try again later.")
            return

    # ----- STEP 3: Password -----
    while True:
        password = listen("Please say your password. Keep it short for accuracy.")
        if not password:
            continue
        confirm_password = listen("Please confirm your password.")
        if password != confirm_password:
            speak("Passwords do not match. Let's try again.")
            continue
        if confirm_input(password, "password"):
            break

    # ----- STEP 4: Send to Server -----
    try:
        resp = requests.post(CREATE_ACCOUNT_API, data={
            "name": name,
            "email": email,
            "password": password,
            "confirm_password": confirm_password
        }, timeout=8)

        resp.raise_for_status()
        j = resp.json()
        if j.get("success"):
            speak("Account created successfully. Redirecting to dashboard.")
            dashboard(email)  # ✅ now correctly called
        else:
            msg = j.get("message", "Unknown error")
            speak(f"Account creation failed. {msg}")
    except Exception as e:
        print("[ERROR] create_account POST failed:", e)
        speak("Failed to create account due to network or server error.")


# ---------- LOGIN ----------
def login():
    """Voice-driven login flow."""
    speak("Opening login page.")
    open_page(LOGIN_PAGE)

    # Email
    while True:
        raw_email = listen("Please say your email.")
        if not raw_email:
            continue
        email = normalize_email_spoken(raw_email)
        if confirm_input(email, "email"):
            break

    # Password
    while True:
        password = listen("Please say your password.")
        if not password:
            continue
        if confirm_input(password, "password"):
            break

    # Verify with server
    try:
        resp = requests.post(LOGIN_API, data={"email": email, "password": password}, timeout=6)
        if resp.status_code == 200:
            j = resp.json()
            if j.get("success"):
                speak("Login successful. Opening dashboard.")
                dashboard(email)
            else:
                speak("Login failed. Email or password incorrect.")
        else:
            speak("Server returned an error during login.")
    except Exception as e:
        print("Login error:", e)
        speak("Failed to login due to network error.")

# ---------- FETCH EMAILS ----------
def fetch_emails(folder, user_email):
    """Fetch emails and return list of dicts with sender, subject, message, starred."""
    try:
        url = FETCH_INBOX_API if folder=="inbox" else FETCH_SENT_API
        r = requests.get(url, params={"user": user_email})
        r.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "html.parser")
        emails = []
        for li in soup.find_all("li"):
            sender = subject = message = "Unknown"
            starred = False
            star_span = li.find("span", class_="star")
            if star_span and "★" in star_span.text:
                starred = True
            for b in li.find_all("b"):
                label = b.text.strip()
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
            emails.append({"sender": sender, "subject": subject, "message": message, "starred": starred})
        return emails
    except Exception as e:
        print("Error fetching emails:", e)
        speak(f"Could not fetch {folder}.")
        return []

def read_folder(folder, user_email):
    emails = fetch_emails(folder, user_email)
    if not emails:
        speak(f"No emails in {folder}.")
        return
    starred_emails = [e for e in emails if e['starred']]
    normal_emails = [e for e in emails if not e['starred']]
    sorted_emails = starred_emails + normal_emails
    speak(f"You have {len(emails)} emails in {folder}.")
    for i, mail in enumerate(sorted_emails, 1):
        prefix = "Starred " if mail['starred'] else ""
        speak(f"{prefix}Email {i}. From {mail['sender']}. Subject {mail['subject']}.")

# ---------- COMPOSE EMAIL ----------
def compose_email(user_email):
    open_page(COMPOSE_PAGE, "Opening compose email page.")

    # Recipient
    while True:
        recipient = listen("Please say the recipient email.")
        if not recipient:
            continue
        recipient = normalize_email_spoken(recipient)
        if confirm_input(recipient, "recipient"):
            break

    # Subject
    while True:
        subject = listen("Please say the subject.")
        if subject and confirm_input(subject, "subject"):
            break

    # Message
    while True:
        message = listen("Please say your message.")
        if message and confirm_input(message, "message"):
            break

    # Optional attachment
    attachment_path = ""
    attach_choice = listen("Do you want to attach a file? Say yes or no.")
    if attach_choice and "yes" in attach_choice.lower():
        while True:
            attachment_path = listen("Please say the full path of the file to attach.")
            if os.path.exists(attachment_path) and confirm_input(attachment_path, "attachment path"):
                break
            else:
                speak("File not found. Please try again.")
                attachment_path = ""

    # Send email
    try:
        files = {}
        if attachment_path:
            files['attachment'] = open(attachment_path, 'rb')
        data = {"recipient": recipient, "subject": subject, "message": message, "user": user_email}
        r = requests.post(SEND_EMAIL_API, data=data, files=files if files else None)
        if files:
            files['attachment'].close()
        if r.status_code == 200:
            j = r.json()
            if j.get("status") == "success":
                speak("Email sent successfully.")
            else:
                speak("Failed to send email.")
        else:
            speak("Server returned error while sending email.")
    except Exception as e:
        print("Error sending email:", e)
        speak("Failed to send email.")

# ---------- DASHBOARD ----------
def dashboard(user_email):
    open_page(INDEX_PAGE, "Opening dashboard.")
    while True:
        cmd = listen("Say 'read inbox', 'read sent', 'compose email', or 'logout'.")
        if not cmd:
            continue
        cmd = cmd.lower()
        if "inbox" in cmd:
            read_folder("inbox", user_email)
        elif "sent" in cmd:
            read_folder("sent", user_email)
        elif "compose" in cmd:
            compose_email(user_email)
        elif any(x in cmd for x in ["logout", "exit", "back"]):
            speak("Returning to main menu.")
            break
        else:
            speak("Command not recognized. Please try again.")

# ---------- MAIN ----------
def main():
    open_page(INDEX_PAGE, "Welcome to iMails voice assistant.")
    while True:
        cmd = listen("Say 'create account', 'login', or 'exit'.")
        if not cmd:
            continue
        cmd = cmd.lower()
        if any(x in cmd for x in ["create account", "signup"]):
            create_account()
        elif any(x in cmd for x in ["login", "log in"]):
            login()
        elif any(x in cmd for x in ["exit", "quit"]):
            speak("Goodbye!")
            break
        else:
            speak("Command not recognized. Please repeat.")

if __name__ == "__main__":
    main()
