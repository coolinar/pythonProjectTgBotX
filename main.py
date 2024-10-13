import telebot
import speech_recognition as sr
from pydub import AudioSegment
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Получаем токен из .env
API_TOKEN = os.getenv('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)
recognizer = sr.Recognizer()

# Инструкция по записи голосового сообщения
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "🎤 Отправьте мне голосовое сообщение. Я преобразую его в текст и сохраню в файл."
    )

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Скачиваем голосовое сообщение
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем его во временный файл
        with open('voice.ogg', 'wb') as f:
            f.write(downloaded_file)

        # Конвертируем ogg в wav
        audio = AudioSegment.from_ogg('voice.ogg')
        audio.export('voice.wav', format='wav')

        # Транскрибируем wav файл
        with sr.AudioFile('voice.wav') as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ru-RU')

        # Сохраняем транскрибированный текст в файл
        with open('transcript.txt', 'w') as f:
            f.write(text)

        # Отправляем пользователю подтверждение
        bot.reply_to(message, "Ваше голосовое сообщение было успешно транскрибировано и сохранено в файл `transcript.txt`.")

        # Отправляем файл пользователю
        with open('transcript.txt', 'rb') as f:
            bot.send_document(message.chat.id, f)

        # Удаляем временные файлы
        os.remove('voice.ogg')
        os.remove('voice.wav')
        os.remove('transcript.txt')

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

# Запускаем бота
bot.polling()
