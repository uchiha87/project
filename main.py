from playwright.sync_api import Playwright, sync_playwright
import time
from datetime import datetime
import pytz
import requests
import os
import sys

# Load dari environment atau GitHub Secret
userid = os.getenv("userid")
pw = os.getenv("pw")
telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

# Waktu lokal WIB
def waktu_wib():
    return datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M WIB")

def baca_file(file_name: str) -> str:
    with open(file_name, 'r') as file:
        return file.read().strip()

def kirim_telegram_log(pesan: str):
    print(pesan)
    if telegram_token and telegram_chat_id:
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                data={
                    "chat_id": telegram_chat_id,
                    "text": pesan,
                    "parse_mode": "Markdown"
                }
            )
            if response.status_code != 200:
                print(f"⚠️ Gagal kirim ke Telegram. Status: {response.status_code}")
                print(f"Respon Telegram: {response.text}")
        except Exception as e:
            print(f"⚠️ Error kirim Telegram: {e}")
    else:
        print("⚠️ Token atau Chat ID Telegram tidak tersedia.")

def parse_nomorbet(nomorbet: str):
    try:
        kombinasi, nominal = nomorbet.split('#')
        jumlah_kombinasi = len(kombinasi.split('*'))
        return jumlah_kombinasi, int(nominal)
    except:
        return 0, 0

def get_url_and_label(mode_site: str):
    mode_site = mode_site.lower()
    if mode_site == "up":
        return "https://up39987.com/lite", "[UP]"
    elif mode_site == "indra":
        return "https://indratogel31303.com/lite", "[INDRA]"
    else:
        # Kalau mau tambah site lain tinggal diatur disini
        print(f"❌ MODE_SITE '{mode_site}' tidak dikenali.")
        return None, None

def run_for_site(playwright: Playwright, mode_site: str) -> bool:
    url, label = get_url_and_label(mode_site)
    if not url:
        return False  # langsung anggap gagal kalau URL tidak valid

    try:
        print(f"🌐 Memproses {label} - {url}")
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(**playwright.devices["Pixel 7"])
        page = context.new_page()

        page.goto(url)
        page.locator("#entered_login").fill(userid)
        page.locator("#entered_password").fill(pw)
        page.get_by_role("button", name="Login").click()

        page.get_by_role("link", name="Pools").click()
        page.get_by_role("link", name="HOKIDRAW").click()
        time.sleep(2)
        page.get_by_role("button", name="4D Classic").click()
        time.sleep(2)

        nomorbet = baca_file("config.txt")
        jumlah_kombinasi, bet = parse_nomorbet(nomorbet)
        total_bet_rupiah = bet * jumlah_kombinasi

        page.get_by_role("cell", name="BET FULL").click()
        page.locator("#tebak").fill(nomorbet)
        page.once("dialog", lambda dialog: dialog.accept())

        page.get_by_role("button", name="KIRIM").click()

        print("⏳ Menunggu konfirmasi...")
        page.wait_for_selector("text=Bet Sukses!!", timeout=15000)

        saldo = page.locator("#bal-text").inner_text()

        pesan = (
            "[SUKSES]\n"
            f"{label}\n"
            f"🎯 TOTAL {jumlah_kombinasi} HARGA Rp. {bet}\n"
            f"💸 BAYAR Rp. {total_bet_rupiah}\n"
            f"💰 SALDO KAMU Rp. {saldo}\n"
            f"⌚ {waktu_wib()}"
        )
        kirim_telegram_log(pesan)

        context.close()
        browser.close()
        return True  # sukses
    except Exception as e:
        print(f"❌ Error di {label}: {e}")
        pesan = (
            "[GAGAL]\n"
            f"{label}\n"
            f"❌ Error: {str(e)}\n"
            f"⌚ {waktu_wib()}"
        )
        kirim_telegram_log(pesan)
        return False  # gagal

if __name__ == "__main__":
    semua_site = baca_file("site.txt").splitlines()
    error_detected = False
    sukses_site = []
    gagal_site = []

    with sync_playwright() as playwright:
        for site in semua_site:
            if site.strip() == "":
                continue
            result = run_for_site(playwright, site.strip())
            if result:
                sukses_site.append(site)
            else:
                gagal_site.append(site)
                error_detected = True

    # Summary akhir
    summary = (
        f"📋 Summary Taruhan\n"
        f"✅ Sukses: {len(sukses_site)} site\n"
        f"❌ Gagal: {len(gagal_site)} site\n"
        f"⌚ {waktu_wib()}"
    )
    kirim_telegram_log(summary)

    if error_detected:
        sys.exit(1)
    else:
        sys.exit(0)
