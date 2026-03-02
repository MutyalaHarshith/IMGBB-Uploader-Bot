import telebot
import requests
import os
from telebot.types import Message

BOT_TOKEN = os.getenv('BOT_TOKEN')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

if not BOT_TOKEN or not IMGBB_API_KEY:
    print("Set BOT_TOKEN and IMGBB_API_KEY environment variables!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'imageUrl'])
def handle_image_request(message: Message):
    bot.reply_to(message, "*Send me the image to upload!*", parse_mode='Markdown')

@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
    bot.reply_to(message, "⏳ Uploading...")
    
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    
    image_response = requests.get(file_url)
    if image_response.status_code != 200:
        bot.reply_to(message, "❌ Failed to download image.")
        return
    
    imgbb_url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    files = {'image': ('image.jpg', image_response.content, 'image/jpeg')}
    imgbb_response = requests.post(imgbb_url, files=files)
    
    if imgbb_response.status_code == 200:
        data = imgbb_response.json()
        if data.get('success'):
            link = data['data']['url']
            # Fixed: Use triple quotes for multiline f-string
            success_msg = f"""📁 *Your Image Uploaded to ImgBB!*

🔗 [Open Link]({link})"""
            bot.reply_to(message, success_msg, 
                        parse_mode='Markdown', disable_web_page_preview=True)
        else:
            bot.reply_to(message, f"❌ ImgBB error: {data.get('error', 'Unknown')}")
    else:
        bot.reply_to(message, "❌ Upload failed.")

print("Bot starting...")
bot.polling(none_stop=True)
