#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
import yt_dlp
import os
import re
import threading
import time
import shutil

# ============================================
# 🔑 التوكن (ضع التوكن الخاص بك هنا)
# ============================================
TOKEN = "8778509203:AAEiqi4z2fvNYVB20QFsy3qGygT4oetbWwM"  # استبدله بتوكنك

# ============================================
# 🚀 تشغيل البوت
# ============================================
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()  # إزالة أي Webhook سابق

# ============================================
# 📁 مجلد التحميل المؤقت
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
# 📥 دالة التحميل الأساسية
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
            # إعدادات yt-dlp
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
                
                # إذا لم يتم العثور على الملف، حاول البحث عنه
                if not os.path.exists(file_path):
                    files = os.listdir(DOWNLOAD_FOLDER)
                    if files:
                        file_path = os.path.join(DOWNLOAD_FOLDER, files[0])
                    else:
                        raise Exception("لم يتم العثور على الملف المحمل")
                
                # تحديد حجم الملف
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                
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
                bot.edit_message_text(
                    f"✅ **تم التحميل بنجاح!**\n📁 {os.path.basename(file_path)}\n📦 {file_size:.2f} MB",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode='Markdown'
                )
                
                print(f"✅ تم تحميل وإرسال: {os.path.basename(file_path)}")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ خطأ: {error_msg}")
            bot.edit_message_text(
                f"❌ **حدث خطأ أثناء التحميل**\n\n📌 {error_msg[:150]}...",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='Markdown'
            )
    
    # تشغيل التحميل في خيط منفصل (لتجنب تجميد البوت)
    threading.Thread(target=process_download).start()

# ============================================
# 🚀 تشغيل البوت
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("✅ بوت اكرم يعمل الآن...")
    print("📥 يدعم الفيديو والصور من جميع المواقع")
    print("=" * 50)
    bot.infinity_polling()
