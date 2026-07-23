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
# 🚀 حذف الـ Webhook (مع معالجة الأخطاء)
# ============================================
try:
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    print(f"✅ Webhook deleted: {response.json()}")
except Exception as e:
    print(f"⚠️ Could not delete webhook: {e}")

time.sleep(1)

# ============================================
# 🚀 إنشاء البوت (بدون api_url أو proxies)
# ============================================
bot = telebot.TeleBot(TOKEN)

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
    bot.reply_to(message, "🎬 أرسل رابط الفيديو أو الصورة وسأقوم بتحميلها لك.")

# ============================================
# 📥 دالة التحميل (تدعم الفيديو والصور)
# ============================================
@bot.message_handler(func=lambda message: True)
def download_media(message):
    url = message.text.strip()
    
    # التحقق من صحة الرابط
    if not re.match(r'^https?://', url):
        bot.reply_to(message, "❌ أرسل رابطاً صحيحاً يبدأ بـ http:// أو https://")
        return
    
    # رسالة "جاري التحميل"
    status_msg = bot.reply_to(message, "⏳ جاري التحميل...")
    
    def process_download():
        try:
            # إعدادات yt-dlp (تدعم الفيديو والصور)
            ydl_opts = {
                'format': 'best[ext=mp4]/best[ext=jpg]/best[ext=png]/best[ext=webp]/best',
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
                
                # إذا لم يتم العثور على الملف، حاول البحث عنه
                if not os.path.exists(file_path):
                    files = os.listdir(DOWNLOAD_FOLDER)
                    if files:
                        file_path = os.path.join(DOWNLOAD_FOLDER, files[0])
                    else:
                        raise Exception("لم يتم العثور على الملف المحمل")
                
                # تحديد نوع الملف
                ext = os.path.splitext(file_path)[1].lower()
                
                # إرسال الملف حسب نوعه
                with open(file_path, 'rb') as f:
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                        bot.send_photo(message.chat.id, f)
                    elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                        bot.send_video(message.chat.id, f)
                    else:
                        bot.send_document(message.chat.id, f)
                
                # حذف الملف بعد الإرسال
                os.remove(file_path)
                
                # تحديث رسالة النجاح
                try:
                    bot.edit_message_text(
                        "✅ تم التحميل والإرسال بنجاح!",
                        chat_id=message.chat.id,
                        message_id=status_msg.message_id
                    )
                except Exception as e:
                    print(f"⚠️ Could not edit message: {e}")
                
                print(f"✅ تم تحميل وإرسال: {os.path.basename(file_path)}")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ خطأ: {error_msg}")
            try:
                bot.edit_message_text(
                    f"❌ حدث خطأ أثناء التحميل\n\n📌 {error_msg[:150]}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
                )
            except Exception as e:
                print(f"⚠️ Could not edit message: {e}")
    
    # تشغيل التحميل في خيط منفصل
    threading.Thread(target=process_download).start()

# ============================================
# 🚀 تشغيل البوت مع إعادة تشغيل تلقائي
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
