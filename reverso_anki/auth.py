from playwright.sync_api import sync_playwright
import time
import json

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_browser_instance(playwright, browser_name, headless):
    if browser_name == "chromium":
        return playwright.chromium.launch(headless=headless)
    elif browser_name == "firefox":
        return playwright.firefox.launch(headless=headless)
    elif browser_name == "webkit":
        return playwright.webkit.launch(headless=headless)
    else:
        raise ValueError(f"❌ Unknown browser specified: {browser_name}")

def save_auth_state():
    with sync_playwright() as p:
        print('🔐 Log in to your account by selecting "log in" in the window that opens. After logging, press Enter here...')
        time.sleep(7)
        config = load_config()

        headless = config.get("headless_browser", False)
        browser_name = config.get("browser", "webkit")

        browser = get_browser_instance(p, browser_name, headless)
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://context.reverso.net/translation/")
        input()

        context.storage_state(path="auth_state.json")

        print("✅ Authorization is saved in auth_state.json")
        browser.close()
