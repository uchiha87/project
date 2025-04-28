import re
import requests
from playwright.sync_api import sync_playwright
import os
import time

# --- Load .env ---

PASSWORD = os.getenv("pw")
BOT_TOKEN = os.getenv("telegram_token")
CHAT_ID = os.getenv("telegram_chat_id")

# --- Load site.txt ---
def load_sites():
    sites = []
    with open('site.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().split(":")
            if len(parts) >= 2:
                domain = parts[0]
                username = parts[1]
                sites.append((domain, username))
    return sites

# --- Kirim Telegram ---
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Pesan terkirim ke Telegram.")
    else:
        print(f"Gagal kirim Telegram. Status: {response.status_code}")

# --- Scrape per site ---
def process_site(playwright, domain, username):
    print(f"Memproses: {domain}")

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(**playwright.devices["Pixel 7"])
    page = context.new_page()
    
    try:
        page.goto(f"https://{domain}/lite", timeout=60000)

        # Login
        page.locator("#entered_login").click()
        page.locator("#entered_login").fill(username)
        page.locator("#entered_password").click()
        page.locator("#entered_password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

        # Klik Transaction
        page.get_by_role("link", name="Transaction").click()

        # Tunggu tabel tampil
        page.wait_for_selector("table.history tbody#transaction", timeout=30000)

        rows = page.locator("table.history tbody#transaction tr").all()

        if not rows:
            print(f"Tabel kosong di {domain}")
            return

        # Ambil hanya baris pertama (C2)
        first_row = rows[0]
        cols = first_row.locator("td").all()
        
        if len(cols) >= 5:
            tanggal = cols[0].inner_text().strip()
            periode = cols[1].inner_text().strip()
            keterangan = cols[2].inner_text().strip()
            status_full = cols[3].inner_text().strip()
            saldo = cols[4].inner_text().strip()

            if "Menang Pool HOKIDRAW" in keterangan:
                # Kalau menang
                match = re.search(r"Menang\s*([\d.,]+)", status_full)
                if match:
                    nilai_menang = match.group(1)
                else:
                    nilai_menang = "Tidak ditemukan"

                message = f"""<b>{domain.upper()}</b>
<b>Menang Pool HOKIDRAW</b>
Menang {nilai_menang}
SALDO {saldo}"""

                send_telegram(message)
            else:
                # Kalau tidak menang
                message = f"""<b>{domain.upper()}</b>
<b>Tidak Menang Pool HOKIDRAW</b>
SALDO {saldo}"""
                send_telegram(message)

    except Exception as e:
        print(f"Error saat proses {domain}: {e}")

    finally:
        context.close()
        browser.close()

# --- Main ---
def main():
    sites = load_sites()
    if not sites:
        print("site.txt kosong!")
        return

    with sync_playwright() as playwright:
        for domain, username in sites:
            process_site(playwright, domain, username)
            time.sleep(5)  # kasih delay antar site

if __name__ == "__main__":
    main()
