from keep_alive import keep_alive
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import logging
import traceback
import requests
import html
import re
from datetime import datetime
import pytz

# --- আপনার ব্যক্তিগত তথ্য ---
IVASMS_EMAIL = "niloyg822@gmail.com"
IVASMS_PASSWORD = "N81234567"
TELEGRAM_TOKEN = "7549134101:AAFtBzB1gJ1hXj18zHLVTXQvtM3gZlkOvpw"
TELEGRAM_CHAT_ID = "-1002819267399"
BOT_NAME = "NILOY OTP"
ADMIN_USER_ID = 7052442701

# --- লগিং এবং URL সেটআপ ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGIN_URL = "https://www.ivasms.com/login"
SMS_PAGE_URL = "https://www.ivasms.com/portal/live/my_sms"

# --- টেলিগ্রাম ফাংশন ---
def send_to_telegram(message, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logging.info(f"✅ মেসেজ {chat_id}-তে পাঠানো হয়েছে।")
        else:
            logging.error(f"❌ {chat_id}-তে পাঠাতে ব্যর্থ! উত্তর: {response.text}")
    except Exception as e:
        logging.error(f"❌ টেলিগ্রাম পাঠানোর ফাংশনে ত্রুটি: {e}")

# --- মূল ফাংশন (চূড়ান্ত এবং সম্পূর্ণ সঠিক সংস্করণ) ---
def main():
    # --- ✅✅✅ মূল এবং চূড়ান্ত পরিবর্তনটি এখানে ---
    # পাঠানো মেসেজের একটি তালিকা মনে রাখার জন্য
    sent_messages = set()
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.get(LOGIN_URL)
        time.sleep(3)
        driver.find_element(By.NAME, "email").send_keys(IVASMS_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(IVASMS_PASSWORD)
        driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(5)
        
        if "login" in driver.current_url:
            raise Exception("লগইন ব্যর্থ।")
            
        logging.info("✅✅✅ লগইন সফল!")
        # শুধু অ্যাডমিনকে স্ট্যাটাস মেসেজ পাঠানো হচ্ছে
        send_to_telegram(f"<b>{BOT_NAME} BOT</b>\n🚀 <i>বট সফলভাবে চালু হয়েছে এবং কাজ করছে!</i>", ADMIN_USER_ID)
        
        driver.get(SMS_PAGE_URL)
        logging.info(f"👀 {SMS_PAGE_URL} পেজটি পর্যবেক্ষণ করা হচ্ছে...")
        
        while True:
            try:
                all_rows = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                
                # টেবিলটি উল্টো করে পড়া হচ্ছে, যাতে নতুন মেসেজ আগে পাওয়া যায়
                for row in reversed(all_rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 5:
                        number_details = cells[0].text.strip().split('\n')
                        number = number_details[1] if len(number_details) > 1 else "N/A"
                        service_name = cells[1].text.strip()
                        message_content = cells[4].text.strip()
                        
                        # --- ✅✅✅ ডুপ্লিকেট মেসেজ পাঠানোর সমস্যা সমাধান ---
                        # যদি এই মেসেজটি আগে না পাঠানো হয়ে থাকে
                        if message_content and message_content not in sent_messages:
                            logging.info(f"🆕 নতুন মেসেজ শনাক্ত হয়েছে: {message_content}")
                            
                            otp_code_match = re.search(r'\b\d{4,8}\b', message_content)
                            otp_code = otp_code_match.group(0) if otp_code_match else "N/A"
                            
                            tz = pytz.timezone('Asia/Dhaka')
                            current_time = datetime.now(tz).strftime('%d/%m/%Y, %H:%M:%S')

                            escaped_message = html.escape(message_content)
                            
                            formatted_msg = (
                                f"{BOT_NAME}\n"
                                f"✨ <b>OTP Received</b> ✨\n\n"
                                f"⏰ <b>Time:</b> {current_time}\n"
                                f"📞 <b>Number:</b> {number}\n"
                                f"🔧 <b>Service:</b> {service_name}\n"
                                f"🔑 <b>OTP Code:</b> <code>{otp_code}</code>\n\n"
                                f"<blockquote>{escaped_message}</blockquote>"
                            )
                            
                            # OTP মেসেজটি মূল গ্রুপে পাঠানো হচ্ছে
                            send_to_telegram(formatted_msg, TELEGRAM_CHAT_ID)
                            # মেসেজটিকে পাঠানো হয়েছে বলে চিহ্নিত করা
                            sent_messages.add(message_content) 
                            time.sleep(0.5) 
            except Exception:
                pass
            
            time.sleep(2)

    except Exception as e:
        error_details = traceback.format_exc()
        shutdown_message = f"<b>{BOT_NAME} BOT</b>\n🐞 **বট একটি অপ্রত্যাশিত সমস্যায় পড়েছে এবং বন্ধ হয়ে যাচ্ছে!**\n\n**কারণ:**\n`{e}`"
        # বট ক্র্যাশ করার মেসেজটিও শুধু অ্যাডমিনকে পাঠানো হচ্ছে
        send_to_telegram(shutdown_message, ADMIN_USER_ID)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    keep_alive()
    main()
