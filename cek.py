from playwright.sync_api import Playwright, sync_playwright
from datetime import datetime
import pytz
import requests
import os
import sys
import time
import re

def baca_file(file_name: str) -> str:
    with open(file_name, 'r') as file:
        return file.read().strip()

def baca_file_list(file_name: str) -> list:
    with open(file_name, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def format_rupiah(angka):
    try:
        angka = float(angka)
        return f"Rp {angka:,.0f}".replace(",", ".")
    except:
        return angka

def kirim_telegram_log(pesan: str, parse_mode="Markdown"):
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    print(pesan)
    if telegram_token and telegram_chat_id:
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                data={
                    "chat_id": telegram_chat_id,
                    "text": pesan,
                    "parse_mode": parse_mode
                }
            )
            if response.status_code != 200:
                print(f"⚠️ Gagal kirim ke Telegram. Status: {response.status_code}")
                print(f"Respon Telegram: {response.text}")
        except Exception as e:
            print(f"⚠️ Error kirim Telegram: {e}")
    else:
        print("⚠️ Token atau Chat ID Telegram tidak tersedia.")

def wib():
    return datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M WIB")

def run(playwright: Playwright) -> int:
    sites = baca_file_list("site.txt")
    pw_env = os.getenv("pw")
    ada_error = False

    for entry in sites:
        try:
            site, userid_site, *_ = entry.split(':')
            full_url = f"https://{site}/lite"

            print(f"🌐 Membuka browser untuk {site}...")
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(**playwright.devices["Pixel 7"])
            page = context.new_page()

            page.goto(full_url, timeout=60000)

            if not userid_site or not pw_env:
                raise Exception("Username atau Password kosong!")

            page.locator("#entered_login").fill(userid_site)
            page.locator("#entered_password").fill(pw_env)
            page.get_by_role("button", name="Login").click()
            time.sleep(1)
            page.get_by_role("link", name="Transaction").click()
            print(f"🔎 Mengecek saldo dan riwayat kemenangan di {site}...")
            time.sleep(1)
            page.wait_for_selector("table.history tbody#transaction", timeout=30000)

            rows = page.locator("table.history tbody#transaction tr").all()

            if not rows:
                print(f"Tabel kosong di {site}")
                continue

            first_row = rows[0]
            cols = first_row.locator("td").all()

            if len(cols) >= 5:
                raw_saldo = cols[4].inner_text().strip()
                current_saldo = int(float(raw_saldo))

                keterangan = cols[2].inner_text().strip()
                status_full = cols[3].inner_text().strip()

                if "Menang Pool HOKIDRAW" in keterangan:
                    match = re.search(r"Menang\s*([\d.,]+)", status_full)
                    nilai_menang = match.group(1) if match else "Tidak ditemukan"

                    pesan_menang = (
                        f"<b>{userid_site}</b>\n"
                        f"<b>🏆 Menang</b>\n"
                        f"🎯 Menang {format_rupiah(nilai_menang)}\n"
                        f"💰 Saldo: {format_rupiah(current_saldo)}\n"
                        f"⌚ {wib()}"
                    )
                    kirim_telegram_log(pesan_menang, parse_mode="HTML")
                else:
                    pesan_kalah = (
                        f"<b>{userid_site}</b>\n"
                        f"<b>😢 Tidak Menang</b>\n"
                        f"💰 Saldo: {format_rupiah(current_saldo)}\n"
                        f"⌚ {wib()}"
                    )
                    kirim_telegram_log(pesan_kalah, parse_mode="HTML")

                # ==== AUTO WD LOGIC ====
                try:
                    if os.path.exists("autowd.txt"):
                        autowd_config = baca_file("autowd.txt")
                        if ':' in autowd_config:
                            batas_str, wd_amount_str = autowd_config.split(":")
                            batas_saldo = int(batas_str.strip())
                            wd_amount = wd_amount_str.strip()

                            if current_saldo >= batas_saldo:
                                print(f"💳 Saldo {current_saldo} >= {batas_saldo}, melakukan auto withdraw {wd_amount}")
                                page.get_by_role("link", name="Back to Menu").click()
                                time.sleep(1)
                                page.get_by_role("link", name="Withdraw").click()
                                time.sleep(1)
                                page.get_by_role("textbox", name="Withdraw").click()
                                time.sleep(1)
                                page.get_by_role("textbox", name="Withdraw").fill(wd_amount)
                                time.sleep(1)
                                page.get_by_role("button", name="Kirim").click()
                                time.sleep(2)

                                page.wait_for_selector("text=berhasil", timeout=15000)

                                kirim_telegram_log(
                                    f"<b>{userid_site}</b>\n"
                                    f"✅ Auto WD {format_rupiah(wd_amount)} berhasil\n"
                                    f"💰 Saldo sisa: {format_rupiah(current_saldo - int(wd_amount))}\n"
                                    f"⌚ {wib()}",
                                    parse_mode="HTML"
                                )
                except Exception as e:
                    print(f"⚠️ Gagal auto WD: {e}")

            context.close()
            browser.close()

        except Exception as e:
            ada_error = True
            print(f"❌ Error di {site}: {e}")
            try:
                context.close()
                browser.close()
            except:
                pass
            continue

    return 1 if ada_error else 0

if __name__ == "__main__":
    with sync_playwright() as playwright:
        exit_code = run(playwright)
        sys.exit(exit_code)
