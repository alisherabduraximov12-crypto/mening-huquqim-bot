import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")


def telegram(method, data=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    response = requests.post(url, json=data or {})
    return response.json()


def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        data["reply_markup"] = {
            "keyboard": keyboard,
            "resize_keyboard": True
        }

    return telegram("sendMessage", data)


@app.route("/", methods=["GET"])
def home():
    return "Mening Huquqim bot ishlayapti!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True)

    if not update:
        return "OK"

    message = update.get("message")

    if not message:
        return "OK"

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        keyboard = [
            ["🛒 Mahsulot muammosi"],
            ["💰 Pulni qaytarish", "🛠 Kafolat"],
            ["📝 Ariza tayyorlash"],
            ["📎 Kerakli hujjatlar"],
            ["⚖️ Huquqlarim", "📞 Aloqa"]
        ]

        send_message(
            chat_id,
            "🇺🇿 Mening Huquqim botiga xush kelibsiz!\n\n"
            "Men iste’molchi huquqlari bo‘yicha amaliy yordamchi bo‘laman.\n\n"
            "Quyidagi menyudan kerakli bo‘limni tanlang:",
            keyboard
        )

    elif text == "🛒 Mahsulot muammosi":
        send_message(
            chat_id,
            "🛒 Mahsulot muammosi\n\n"
            "Muammoingizni aniqlash uchun bir nechta savol beraman.\n\n"
            "1️⃣ Qanday mahsulot sotib oldingiz?\n"
            "Masalan: muzlatgich, televizor, telefon yoki boshqa mahsulot."
        )

    elif text == "💰 Pulni qaytarish":
        send_message(
            chat_id,
            "💰 Pulni qaytarish bo‘yicha yordam.\n\n"
            "Avvalo mahsulot yoki xizmat bilan bog‘liq muammoingizni batafsil yozing."
        )

    elif text == "🛠 Kafolat":
        send_message(
            chat_id,
            "🛠 Kafolat masalasi.\n\n"
            "Mahsulot nomi, sotib olingan sana va kafolat muddati haqida ma’lumot yozing."
        )

    elif text == "📝 Ariza tayyorlash":
        send_message(
            chat_id,
            "📝 Ariza tayyorlash\n\n"
            "Sizga murojaat/ariza loyihasini tayyorlashda yordam beraman.\n\n"
            "Muammoingizni batafsil yozing."
        )

    elif text == "📎 Kerakli hujjatlar":
        send_message(
            chat_id,
            "📎 Kerakli hujjatlar\n\n"
            "Muammo turiga qarab kerakli hujjatlar ro‘yxatini aniqlashga yordam beraman.\n\n"
            "Muammoingizni yozing."
        )

    elif text == "⚖️ Huquqlarim":
        send_message(
            chat_id,
            "⚖️ Huquqlaringiz haqida\n\n"
            "Iste’molchi sifatida huquqlaringiz bo‘yicha ma’lumot olish uchun "
            "muammoingizni yozing."
        )

    elif text == "📞 Aloqa":
        send_message(
            chat_id,
            "📞 Aloqa\n\n"
            "Mening Huquqim\n"
            "🇺🇿 Iste’molchi huquqlari bo‘yicha amaliy yordam."
        )

    else:
        send_message(
            chat_id,
            "Xabaringiz qabul qilindi. 📝\n\n"
            "Menyudan kerakli bo‘limni tanlang yoki muammoingizni batafsil yozing."
        )

    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
