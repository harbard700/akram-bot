import telebot
import yt_dlp
import os
import re
import threading

TOKEN = os.environ.get("BOT_TOKEN", "8778509203:AAEiqi4z2fvNYVB20QFsy3qGygT4oetbWwM")
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f"🎬 **مرحباً بك في بوت اكرم!**\n👤 أهلاً بك يا {message.from_user.first_name}!\n📥 أرسل الرابط وسأحمله لك.")

@bot.message_handler(func=lambda m: re.match(r'^https?://', m.text))
def download_media(message):
    url = message.text.strip()
    status = bot.reply_to(message, "⏳ جاري التحميل...")
    
    def process():
        try:
            ydl_opts = {'format': 'best[ext=mp4]/best', 'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
                if not os.path.exists(path):
                    files = os.listdir(DOWNLOAD_FOLDER)
                    path = os.path.join(DOWNLOAD_FOLDER, files[0]) if files else None
                if path and os.path.exists(path):
                    size = os.path.getsize(path) / (1024 * 1024)
                    bot.edit_message_text(f"✅ **تم التحميل!**\n📁 {os.path.basename(path)}\n📦 {size:.2f} MB", chat_id=message.chat.id, message_id=status.message_id)
                    with open(path, 'rb') as f:
                        bot.send_document(message.chat.id, f)
                    os.remove(path)
                else:
                    raise Exception("الملف غير موجود")
        except Exception as e:
            bot.edit_message_text(f"❌ **خطأ:** {str(e)[:100]}", chat_id=message.chat.id, message_id=status.message_id)
    
    threading.Thread(target=process).start()

if __name__ == "__main__":
    print("✅ بوت اكرم يعمل على Render...")
    bot.infinity_polling()
