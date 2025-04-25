import os
import time
import math
import shutil
from playwright.sync_api import sync_playwright, Error
from pathlib import Path
from reverso_anki import save_auth_state, get_browser_instance, load_config



def ensure_auth():
    if not Path("auth_state.json").is_file():
        print("🔒 The authorization file was not found. Launching authorization...")
        time.sleep(3)
        save_auth_state()
    else:
        try:
            with sync_playwright() as p:
                browser = p.webkit.launch(headless=True)
                browser.new_context(storage_state="auth_state.json").close()
                browser.close()
        except Error:
            print("❌ The authorization file is corrupted or invalid. Restarting authorization...")
            time.sleep(3)
            save_auth_state()

def fetch_favorites():
    config = load_config()
    html_folder = config.get("html_folder_path", "favorites_htmls")
    deleted_folder = config.get("deleted_folder_path", "favorites_deleted")
    headless = config.get("headless_browser", False)
    browser_name = config.get("browser", "webkit")

    ensure_auth()
    print("❇️ Starting to parse all the favorites!")
    time.sleep(3)
    
    with sync_playwright() as p:
        browser = get_browser_instance(p, browser_name, headless)
        context = browser.new_context(storage_state="auth_state.json")
        page = context.new_page()
        page.goto("https://www.reverso.net/favorites/en")
        page.wait_for_selector(".list-favourites", timeout=15000)
        time.sleep(2)

        total_text = page.inner_text("span.favourites-header__entry-data")
        total_count = int(total_text.split()[0])
        iterations = math.ceil(total_count / 50)
        print(f"🔢 Total favorites: {total_count}")
        print(f"🔁 Will repeat {iterations} time(s)")

        if not os.path.exists(deleted_folder):
            os.makedirs(deleted_folder)
        else:
            for file in os.listdir(deleted_folder):
                file_path = os.path.join(deleted_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        if os.path.exists(html_folder):
            for file in os.listdir(html_folder):
                if file.endswith(".html"):
                    src = os.path.join(html_folder, file)
                    dst = os.path.join(deleted_folder, file)
                    shutil.move(src, dst)
            shutil.rmtree(html_folder)

        os.makedirs(html_folder)

        for i in range(iterations):
            previous_height = 0
            while True:
                current_height = page.evaluate("(window.innerHeight + window.scrollY)")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == previous_height:
                    break
                previous_height = new_height

            html = page.content()
            with open(f"{html_folder}/favorites_page_{i+1}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"💾 Saved page {i+1}")

            for j in range(50):
                try:
                    card = page.query_selector("app-favourite-item-new:first-of-type")
                    if not card:
                        print(f"👍 There are no cards left")
                        break

                    buttons = card.query_selector_all(
                        "button.favourite-button.favourite-button_grey.favourite-button_medium.favourite-button_square"
                    )
                    if len(buttons) >= 4:
                        menu_button = buttons[3]
                        menu_button.click()
                        time.sleep(0.5)
                    else:
                        print(f"⚠️ Not enough menu buttons in card {j + 1}")
                        continue

                    delete_btn = page.wait_for_selector(".favourites-ellipsis-menu__button_delete", timeout=3000)
                    if delete_btn:
                        delete_btn.click()
                        print(f"✅ Deleted item {j + 1}")
                        page.wait_for_selector("app-favourite-item-new", timeout=5000)
                        time.sleep(0.8)
                    else:
                        print(f"❌ Couldn't find delete button for card {j + 1}")
                    time.sleep(0.6)

                except Exception as e:
                    print(f"❌ Failed to delete item {j + 1}: {e}")

        browser.close()
        print("🏁 Done. All favorites saved and deleted.")


if __name__ == "__main__":
    print("⚠️ Your favorites will be removed from the favorites list! Keep in mind!")
    time.sleep(3)
    fetch_favorites()
