import os
import sys
import asyncio
import logging
import requests
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

ERP_URL = os.getenv("ERP_URL", "https://techsup-erp.com/my/attendance")
EMAIL = os.getenv("ERP_EMAIL", "Islam@techsupbusiness.com")
PASSWORD = os.getenv("ERP_PASSWORD", "Ii@123123")

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_notification(message: str, is_success: bool = True):
    status_icon = "✅" if is_success else "❌"
    formatted_msg = f"{status_icon} **Odoo Attendance Bot Alert**\n{message}"
    
    # Send to Discord if configured
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json={"content": formatted_msg}, timeout=10)
            logging.info("Discord notification sent.")
        except Exception as e:
            logging.error(f"Failed to send Discord alert: {e}")

    # Send to Telegram if configured
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(tg_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": formatted_msg}, timeout=10)
            logging.info("Telegram notification sent.")
        except Exception as e:
            logging.error(f"Failed to send Telegram alert: {e}")

async def run_checkout():
    logging.info("Starting Odoo Auto Checkout Bot...")
    if not EMAIL or not PASSWORD:
        msg = "Error: ERP_EMAIL or ERP_PASSWORD environment variables are missing."
        logging.error(msg)
        send_notification(msg, is_success=False)
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Automatically accept JS confirm dialogs (e.g. confirm('Check out now?'))
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        try:
            login_page_url = f"{ERP_URL}/web/login?redirect=/my/attendance"
            logging.info(f"Navigating to login page: {login_page_url}")
            await page.goto(login_page_url, wait_until="networkidle", timeout=30000)

            # Fill in credentials
            logging.info("Filling in login credentials...")
            await page.wait_for_selector('input[name="login"], #login', timeout=10000)
            await page.fill('input[name="login"], #login', EMAIL)
            await page.fill('input[name="password"], #password', PASSWORD)

            # Click login button
            logging.info("Submitting login form...")
            await page.click('button[type="submit"]')

            # Wait for attendance page load
            await page.wait_for_url("**/my/attendance*", timeout=20000)
            logging.info("Successfully logged in and reached Attendance Portal.")

            # Check status on the page
            page_content = await page.content()
            
            checkout_button = page.locator('form[action*="/my/attendance/checkout"] button[type="submit"]')
            checkin_button = page.locator('form[action*="/my/attendance/checkin"] button[type="submit"]')
            
            checkout_exists = await checkout_button.count() > 0
            checkin_exists = await checkin_button.count() > 0

            target_mode = os.getenv("ACTION_MODE", "smart") # 'checkout', 'checkin', or 'smart'

            if target_mode == "checkin" or (target_mode == "smart" and checkin_exists):
                if checkin_exists:
                    logging.info("Check-in button found. Clicking Check-in button...")
                    await checkin_button.first.click()
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2)
                    msg = f"Successfully checked IN for {EMAIL} at {ERP_URL}!"
                    logging.info(msg)
                    send_notification(msg, is_success=True)
                else:
                    msg = f"User {EMAIL} is already checked in. No check-in action needed."
                    logging.info(msg)
                    send_notification(msg, is_success=True)

            elif target_mode == "checkout" or (target_mode == "smart" and checkout_exists):
                if checkout_exists:
                    logging.info("Check-out button found. Clicking Check-out button...")
                    await checkout_button.first.click()
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2)
                    msg = f"Successfully checked OUT for {EMAIL} at {ERP_URL}!"
                    logging.info(msg)
                    send_notification(msg, is_success=True)
                else:
                    msg = f"User {EMAIL} is already checked out. No check-out action needed."
                    logging.info(msg)
                    send_notification(msg, is_success=True)
            else:
                logging.info("Attendance page reached. Status verified.")

        except Exception as e:
            msg = f"Error occurred during auto checkout: {str(e)}"
            logging.error(msg, exc_info=True)
            send_notification(msg, is_success=False)
            sys.exit(1)
        finally:
            await browser.close()
            logging.info("Browser closed. Process completed.")

if __name__ == "__main__":
    asyncio.run(run_checkout())
