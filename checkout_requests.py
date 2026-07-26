import os
import sys
import re
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ERP_URL = os.getenv("ERP_URL", "https://techsup-erp.com/my/attendance").rstrip('/')
EMAIL = os.getenv("ERP_EMAIL", "Islam@techsupbusiness.com")
PASSWORD = os.getenv("ERP_PASSWORD", "Ii@123123")

def run_checkout_requests():
    logging.info("Starting lightweight HTTP session checkout...")
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    # Step 1: GET Login Page to get CSRF Token
    login_url = f"{ERP_URL}/web/login?redirect=/my/attendance"
    logging.info(f"Fetching login page: {login_url}")
    res = session.get(login_url)
    if res.status_code != 200:
        logging.error(f"Failed to fetch login page. Status: {res.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(res.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    csrf_token = csrf_input["value"] if csrf_input else None

    if not csrf_token:
        # Search in JS script tags for csrf_token
        match = re.search(r'csrf_token:s*["\']([^"\']+)["\']', res.text)
        if match:
            csrf_token = match.group(1)

    logging.info(f"Extracted initial CSRF Token: {csrf_token[:10]}...")

    # Step 2: POST Login Credentials
    payload = {
        "login": EMAIL,
        "password": PASSWORD,
        "csrf_token": csrf_token,
        "redirect": "/my/attendance"
    }
    logging.info(f"Posting login request for {EMAIL}...")
    login_res = session.post(f"{ERP_URL}/web/login", data=payload)
    
    # Step 3: GET Attendance Portal Page
    att_res = session.get(f"{ERP_URL}/my/attendance")
    att_soup = BeautifulSoup(att_res.text, "html.parser")

    # Step 4: Locate Checkout Form & CSRF Token
    checkout_form = att_soup.find("form", action=re.compile(r"/my/attendance/checkout"))
    if not checkout_form:
        if "Checked in" not in att_res.text:
            logging.info("Status: Already checked out or not checked in.")
            return
        else:
            logging.error("Checked in, but checkout form not found.")
            sys.exit(1)

    checkout_csrf = checkout_form.find("input", {"name": "csrf_token"})
    token_to_send = checkout_csrf["value"] if checkout_csrf else csrf_token

    # Step 5: POST Checkout
    checkout_url = f"{ERP_URL}/my/attendance/checkout"
    logging.info(f"Submitting POST to {checkout_url}...")
    final_res = session.post(checkout_url, data={"csrf_token": token_to_send})

    if final_res.status_code == 200:
        logging.info("Successfully checked out via direct HTTP POST!")
    else:
        logging.error(f"Checkout failed with HTTP status code {final_res.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    run_checkout_requests()
