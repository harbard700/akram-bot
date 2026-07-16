import telebot
import yt_dlp
import os
import re
import threading

# 🔑 التوكن من متغيرات البيئة (آمن)
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN is not set in environment variables!")

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()  # حذف الـ Webhook إن وجد

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = f"""
🎬 **مرحباً بك في بوت اكرم!**

👤 أهلاً بك يا {user_name}!

📥 أرسل الرابط وسأحمله لك.

✅ يدعم جميع المواقع:
• تيك توك (فيديو وصور)
• يوتيوب
• إنستغرام
• تويتر
• فيسبوك
• وكل المواقع الأخرى

🔥 يعمل 24/7 على السيرفر
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def download_media(message):
    url = message.text.strip()
    
    if not re.match(r'^https?://', url):
        bot.reply_to(message, "❌ أرسل رابطاً صحيحاً يبدأ بـ http:// أو https://")
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
                'extract_flat': False,
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
                
                bot.edit_message_text(
                    f"✅ **تم التحميل!**\n📁 {os.path.basename(file_path)}\n📦 {file_size:.2f} MB",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode='Markdown'
                )
                
                with open(file_path, 'rb') as f:
                    bot.send_document(message.chat.id, f)
                
                os.remove(file_path)
                print(f"✅ تم تحميل: {os.path.basename(file_path)}")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ خطأ: {error_msg}")
            bot.edit_message_text(
                f"❌ **خطأ في التحميل**\n{error_msg[:100]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='Markdown'
            )
    
    threading.Thread(target=process_download).start()

if __name__ == "__main__":
    print("✅ بوت اكرم يعمل الآن...")
    bot.infinity_polling()
