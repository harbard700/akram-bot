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
# 🔑 التوكن الجديد
# ============================================
TOKEN = "8778509203:AAGgB5owopk1Sv2p_sIdHItLa6f6wByRIo8"

# ============================================
# 🚀 حذف الـ Webhook
# ============================================
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
except:
    pass

time.sleep(1)

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

# ============================================
# 📁 مجلد التحميل
# ============================================
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ============================================
# 📥 دالة استخراج رابط الصورة من تيك توك
# ============================================
def get_tiktok_photo_url(url):
    api_url = f"https://www.tikwm.com/api/?url={url}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                images = data['data'].get('images', [])
                if images:
                    return images[0]
    except:
        pass
    return None

# ============================================
# 🎯 رسالة الترحيب
# ============================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🎬 أرسل رابط الفيديو أو الصورة وسأقوم بتحميلها لك.")

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

    def process():
        try:
            # 🔍 التحقق من رابط صورة تيك توك
            if "tiktok.com" in url and "/photo/" in url:
                photo_url = get_tiktok_photo_url(url)
                if photo_url:
                    img_data = requests.get(photo_url).content
                    file_path = f"{DOWNLOAD_FOLDER}/tiktok_photo.jpg"
                    with open(file_path, 'wb') as f:
                        f.write(img_data)
                else:
                    raise Exception("تعذر استخراج رابط الصورة")
            else:
                # تحميل فيديو أو محتوى آخر
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
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
                            raise Exception("الملف غير موجود")

            # إرسال الملف
            ext = os.path.splitext(file_path)[1].lower()
            with open(file_path, 'rb') as f:
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    bot.send_photo(message.chat.id, f)
                elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                    bot.send_video(message.chat.id, f)
                else:
                    bot.send_document(message.chat.id, f)

            os.remove(file_path)

            try:
                bot.edit_message_text("✅ تم التحميل والإرسال", chat_id=message.chat.id, message_id=status_msg.message_id)
            except:
                pass

        except Exception as e:
            error_msg = str(e)
            print(f"❌ خطأ: {error_msg}")
            try:
                bot.edit_message_text(f"❌ خطأ: {error_msg[:100]}", chat_id=message.chat.id, message_id=status_msg.message_id)
            except:
                pass

    threading.Thread(target=process).start()

# ============================================
# 🚀 تشغيل البوت
# ============================================
if __name__ == "__main__":
    print("✅ البوت يعمل...")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)
