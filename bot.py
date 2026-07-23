#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
import yt_dlp
import os
import re
import threading
import time
import requests

# ============================================
# 🔑 التوكن
# ============================================
TOKEN = "8778509203:AAEiqi4z2fvNYVB20QFsy3qGygT4oetbWwM"

# ============================================
# 🚀 حذف الـ Webhook
# ============================================
try:
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    print(f"✅ Webhook deleted: {response.json()}")
except Exception as e:
    print(f"⚠️ Could not delete webhook: {e}")

time.sleep(2)

# ============================================
# 🚀 تشغيل البوت (مع إعدادات افتراضية)
# ============================================
DEFAULT_API_URL = "https://api.telegram.org"
DEFAULT_PROXIES = {}

bot = telebot.TeleBot(
    TOKEN,
    api_url=DEFAULT_API_URL,
    proxies=DEFAULT_PROXIES
)

# ============================================
# 📁 مجلد التحميل
# ============================================
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ============================================
# 🎯 رسالة الترحيب
# ============================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = f"""
🎬 **مرحباً بك في بوت اكرم لتحميل الفيديوهات والصور** 🎬

👤 أهلاً بك يا {user_name}!

📥 أرسل الرابط وسأقوم بتحميله لك.

✅ **يدعم جميع المواقع:**
• تيك توك (فيديو وصور)
• يوتيوب
• إنستغرام
• فيسبوك
• تويتر
• وكل المواقع الأخرى

⚡ **يعمل 24/7 على السيرفر**
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# ============================================
# 📥 دالة التحميل
# ============================================
@bot.message_handler(func=lambda message: True)
def download_media(message):
    url = message.text.strip()
    
    if not re.match(r'^https?://', url):
        bot.reply_to(message, "❌ أرسل رابطاً صحيحاً")
        return
    
    status_msg = bot.reply_to(message, "⏳ جاري التحميل...")
    
    def process_download():
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best[ext=jpg]/best[ext=png]/best',
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'socket_timeout': 30,
                'retries': 5,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                if not os.path.exists(file_path):
                    files = os.listdir(DOWNLOAD_FOLDER)
                    if files:
                        file_path = os.path.join(DOWNLOAD_FOLDER, files[0])
                    else:
                        raise Exception("لم يتم العثور على الملف")
                
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                ext = os.path.splitext(file_path)[1].lower()
                
                with open(file_path, 'rb') as f:
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                        bot.send_photo(message.chat.id, f)
                    elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                        bot.send_video(message.chat.id, f)
                    else:
                        bot.send_document(message.chat.id, f)
                
                os.remove(file_path)
                
                bot.edit_message_text(
                    f"✅ **تم التحميل!**\n📁 {os.path.basename(file_path)}\n📦 {file_size:.2f} MB",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode='Markdown'
                )
                
                print(f"✅ تم تحميل: {os.path.basename(file_path)}")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ خطأ: {error_msg}")
            bot.edit_message_text(
                f"❌ **خطأ في التحميل**\n{error_msg[:150]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='Markdown'
            )
    
    threading.Thread(target=process_download).start()

# ============================================
# 🚀 تشغيل البوت
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("✅ بوت اكرم يعمل الآن...")
    print("📥 يدعم الفيديو والصور من جميع المواقع")
    print("=" * 50)
    
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"⚠️ Error: {e}")
            print("🔄 Restarting in 5 seconds...")
            time.sleep(5)
