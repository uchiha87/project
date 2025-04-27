import re
 import sys
 
 from dotenv import load_dotenv
 load_dotenv()
 # Tidak perlu load dotenv lagi
 # from dotenv import load_dotenv
 # load_dotenv()
 
 # Load dari environment
 userid = os.getenv("userid")
 pw = os.getenv("pw")
 telegram_token = os.getenv("TELEGRAM_TOKEN")
 telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
 mode_site = os.getenv("MODE_SITE", "").lower()
 
 # Waktu lokal WIB
 wib = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M WIB")
 
 # Cek mode site
 if mode_site == "up":
     url = "https://up39987.com/lite"
     label = "[UP]"
 elif mode_site == "indra":
     url = "https://indratogel31303.com/lite"
     label = "[INDRA]"
 else:
     print("❌ MODE_SITE di .env tidak valid atau tidak diatur.")
     sys.exit(1)
 
 def log_status(emoji: str, message: str):
     print(f"{emoji} {message}")
 wib = lambda: datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M WIB")
 
 def baca_file(file_name: str) -> str:
     with open(file_name, 'r') as file:
         return file.read().strip()
 
 def baca_file_list(file_name: str) -> list:
     with open(file_name, 'r') as file:
         return [line.strip() for line in file if line.strip()]
 
 def kirim_telegram_log(pesan: str):
     print(pesan)
     if telegram_token and telegram_chat_id:
 @@ -67,41 +55,41 @@ def parse_nomorbet(nomorbet: str):
         return 0, 0
 
 def run(playwright: Playwright) -> None:
     try:
         log_status("📂", "Membaca file nomorbet...")
         nomorbet = baca_file("config.txt")
         jumlah_kombinasi, bet = parse_nomorbet(nomorbet)
         total_bet_rupiah = bet * jumlah_kombinasi
         log_status("📬", f"Nomor ditemukan: {nomorbet}")
 
         log_status("🌐", "Membuka browser dan login...")
         browser = playwright.chromium.launch(headless=True)
         context = browser.new_context(**playwright.devices["Pixel 7"])
         page = context.new_page()
 
         page.goto(url)
         page.locator("#entered_login").fill(userid)
         page.locator("#entered_password").fill(pw)
         page.get_by_role("button", name="Login").click()
 
         log_status("🔐", "Login berhasil, masuk ke menu Pools > HOKIDRAW > 4D Classic")
         page.get_by_role("link", name="Pools").click()
         page.get_by_role("link", name="HOKIDRAW").click()
         time.sleep(2)
         page.get_by_role("button", name="4D Classic").click()
         time.sleep(2)
 
         log_status("🧾", "Mengisi form taruhan...")
         page.get_by_role("cell", name="BET FULL").click()
         page.locator("#tebak").fill(nomorbet)
         page.once("dialog", lambda dialog: dialog.accept())
 
         log_status("📨", "Mengirim taruhan...")
         page.get_by_role("button", name="KIRIM").click()
 
         log_status("⏳", "Menunggu konfirmasi dari sistem...")
     nomorbet = baca_file("config.txt")
     jumlah_kombinasi, bet = parse_nomorbet(nomorbet)
     total_bet_rupiah = bet * jumlah_kombinasi
     sites = baca_file_list("site.txt")
 
     for site in sites:
         full_url = f"https://{site}/lite"
         label = f"[{site.upper()}]"
 
         try:
             print(f"🌐 Membuka browser untuk {site}...")
             browser = playwright.chromium.launch(headless=True)
             context = browser.new_context(**playwright.devices["Pixel 7"])
             page = context.new_page()
 
             page.goto(full_url)
             page.locator("#entered_login").fill(userid)
             page.locator("#entered_password").fill(pw)
             page.get_by_role("button", name="Login").click()
 
             print(f"🔐 Login ke {site} berhasil, masuk menu Pools > HOKIDRAW > 4D Classic")
             page.get_by_role("link", name="Pools").click()
             page.get_by_role("link", name="HOKIDRAW").click()
             time.sleep(2)
             page.get_by_role("button", name="4D Classic").click()
             time.sleep(2)
 
             print(f"🧾 Mengisi form taruhan di {site}...")
             page.get_by_role("cell", name="BET FULL").click()
             page.locator("#tebak").fill(nomorbet)
             page.once("dialog", lambda dialog: dialog.accept())
 
             print(f"📨 Mengirim taruhan di {site}...")
             page.get_by_role("button", name="KIRIM").click()
 
             page.wait_for_selector("text=Bet Sukses!!", timeout=15000)
 
             page.get_by_role("link", name="Back to Menu").click()
 @@ -111,45 +99,40 @@ def run(playwright: Playwright) -> None:
                 saldo = page.locator("#bal-text").inner_text()
             except Exception as e:
                 saldo = "tidak diketahui"
                 print("⚠️ Gagal ambil saldo:", e)
             
                 print(f"⚠️ Gagal ambil saldo di {site}:", e)
 
             pesan_sukses = (
                 "[SUKSES]\n"
                 f"[SUKSES]\n"
                 f"{label}\n"
                 f"🎯 TOTAL {jumlah_kombinasi} HARGA Rp. {bet}\n"
                 f"💸 BAYAR Rp. {total_bet_rupiah}\n"
                 f"💰 SALDO KAMU Rp. {saldo}\n"
                 f"⌚ {wib}"
                 f"💰 SALDO Rp. {saldo}\n"
                 f"⌚ {wib()}"
             )
             log_status("✅", pesan_sukses)
             kirim_telegram_log(pesan_sukses)
         except:
             log_status("❌", "Gagal: Teks 'Bet Sukses!!' tidak ditemukan.")
 
             context.close()
             browser.close()
         except Exception as e:
             print(f"❌ Error di {site}: {e}")
             try:
                 saldo = page.locator("#bal-text").inner_text()
             except Exception as e:
             except:
                 saldo = "tidak diketahui"
                 print("⚠️ Gagal ambil saldo:", e)
 
             pesan_gagal = (
                 "[GAGAL]\n"
                 f"[GAGAL]\n"
                 f"{label}\n"
                 f"❌ TOTAL {jumlah_kombinasi} HARGA Rp. {bet}\n"
                 f"💸 BAYAR Rp. {total_bet_rupiah}\n"
                 f"💰 SALDO KAMU Rp. {saldo}\n"
                 f"⌚ {wib}"
                 f"💰 SALDO Rp. {saldo}\n"
                 f"⌚ {wib()}"
             )
             kirim_telegram_log(pesan_gagal)
 
             context.close()
             browser.close()
             sys.exit(1)
 
         context.close()
         browser.close()
     except Exception as e:
         log_status("❌", "Terjadi kesalahan saat menjalankan script.")
         print("Detail error:", e)
         kirim_telegram_log(f"[GAGAL]\n❌ Error: {str(e)}")
         sys.exit(1)
             continue  # Lanjut ke site berikutnya
 
 if __name__ == "__main__":
     with sync_playwright() as playwright:
