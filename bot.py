import os
import requests
import instaloader
import telebot
from telebot import types

# Bot tokenini kiriting
TOKEN = "7808942668:AAGYsPmFmCCnVsO6SiKQn-8okOpXkYs-k1U"
bot = telebot.TeleBot(TOKEN)

# Kanallar username yoki ID sini kiriting
CHANNELS = ["@nkcoder_uz", "@nkcodersgames", "@nkcodersdarslar"]  # 3 ta kanal

# Tilni saqlash uchun foydalanuvchi ma'lumotlari
user_data = {}

# Tillar
LANGUAGES = {
    'uz': "O'zbek tili",
    'ru': "Русский язык",
    'en': "English"
}

# Instagramdan video yuklash funksiyasi
def download_instagram_video(url):
    L = instaloader.Instaloader()
    post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
    video_url = post.video_url
    response = requests.get(video_url)
    with open("video.mp4", "wb") as file:
        file.write(response.content)
    return "video.mp4"

# Foydalanuvchini barcha kanallarga obuna bo'lganligini tekshirish
def is_user_subscribed(user_id):
    try:
        for channel in CHANNELS:
            chat_member = bot.get_chat_member(channel, user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                return False
        return True
    except Exception as e:
        print(f"Obunani tekshirishda xatolik: {e}")
        return False

# /start buyrug'i uchun handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_user_subscribed(user_id):
        keyboard = types.InlineKeyboardMarkup()
        for channel in CHANNELS:
            btn = types.InlineKeyboardButton(f"{channel} kanaliga o'tish", url=f"https://t.me/{channel[1:]}")
            keyboard.add(btn)
        bot.send_message(message.chat.id, "Iltimos, botdan to'liq foydalanish uchun quyidagi kanallarga obuna bo'ling. Obuna bo'lsangiz, /start ni bosing.", reply_markup=keyboard)
        return
    
    # Tilni tanlash uchun tugmalar
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn_uz = types.KeyboardButton(LANGUAGES['uz'])
    btn_ru = types.KeyboardButton(LANGUAGES['ru'])
    btn_en = types.KeyboardButton(LANGUAGES['en'])
    keyboard.add(btn_uz, btn_ru, btn_en)
    
    bot.send_message(message.chat.id, "Iltimos, tilni tanlang:", reply_markup=keyboard)

# Tilni tanlash uchun handler
@bot.message_handler(func=lambda message: message.text in LANGUAGES.values())
def handle_language_selection(message):
    user_id = message.from_user.id
    selected_language = message.text
    language_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(selected_language)]
    user_data[user_id] = {'language': language_code}
    
    # Tanlangan tilga qarab xabar yuborish
    if language_code == 'uz':
        bot.send_message(message.chat.id, "O'zbek tili tanlandi. Endi Instagram video havolasini yuboring.")
    elif language_code == 'ru':
        bot.send_message(message.chat.id, "Русский язык выбран. Теперь отправьте ссылку на видео Instagram.")
    elif language_code == 'en':
        bot.send_message(message.chat.id, "English selected. Now send the Instagram video link.")

# Foydalanuvchi xabariga javob berish
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    message_text = message.text

    # Foydalanuvchi tilini tekshirish
    if user_id not in user_data or 'language' not in user_data[user_id]:
        bot.send_message(message.chat.id, "Iltimos, avval tilni tanlang.")
        return

    # Instagram havolasini tekshirish
    if "instagram.com" in message_text:
        # "Video yuklanmoqda..." xabarini yuboramiz va uni saqlaymiz
        loading_message = bot.reply_to(message, "Video yuklanmoqda..." if user_data[user_id]['language'] == 'uz' 
                          else "Видео загружается..." if user_data[user_id]['language'] == 'ru' 
                          else "Video is loading...")
        try:
            video_path = download_instagram_video(message_text)
            with open(video_path, "rb") as video_file:
                bot.send_video(message.chat.id, video_file)
            os.remove(video_path)  # Faylni o'chirish

            # "Video yuklanmoqda..." xabarini o'chiramiz
            bot.delete_message(chat_id=message.chat.id, message_id=loading_message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Xatolik yuz berdi: {e}" if user_data[user_id]['language'] == 'uz' 
                         else f"Произошла ошибка: {e}" if user_data[user_id]['language'] == 'ru' 
                         else f"An error occurred: {e}")
    else:
        bot.reply_to(message, "Iltimos, Instagram video havolasini yuboring." if user_data[user_id]['language'] == 'uz' 
                     else "Пожалуйста, отправьте ссылку на видео Instagram." if user_data[user_id]['language'] == 'ru' 
                     else "Please send the Instagram video link.")

# Botni ishga tushurish
if __name__ == '__main__':
    bot.polling(none_stop=True)