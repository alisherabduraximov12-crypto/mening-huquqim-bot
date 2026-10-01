import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")


# Foydalanuvchilarning vaqtinchalik holatini saqlash
user_data = {}


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


def set_webhook():
    if not RENDER_URL:
        return

    webhook_url = f"{RENDER_URL}/webhook"

    result = telegram(
        "setWebhook",
        {
            "url": webhook_url
        }
    )

    print("Webhook:", result)


def main_keyboard():
    return [
        ["🛒 Mahsulot muammosi"],
        ["💰 Pulni qaytarish", "🛠 Kafolat"],
        ["📝 Ariza tayyorlash"],
        ["📎 Kerakli hujjatlar"],
        ["⚖️ Huquqlarim", "📞 Aloqa"]
    ]


def yes_no_keyboard():
    return [
        ["✅ Ha", "❌ Yo‘q"]
    ]


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

    # Foydalanuvchi yuborgan faylni aniqlash
    document = message.get("document")
    photo = message.get("photo")

    text = message.get("text", "")

    # /start
    if text == "/start":
        user_data.pop(chat_id, None)

        send_message(
            chat_id,
            "🇺🇿 Mening Huquqim botiga xush kelibsiz!\n\n"
            "Men iste’molchi huquqlari bo‘yicha amaliy yordamchi bo‘laman.\n\n"
            "Quyidagi menyudan kerakli bo‘limni tanlang:",
            main_keyboard()
        )

        return "OK"

    # Mahsulot muammosi boshlanishi
    if text == "🛒 Mahsulot muammosi":
        user_data[chat_id] = {
            "step": 1,
            "product": "",
            "purchase_date": "",
            "problem": "",
            "seller_contacted": "",
            "seller_response": "",
            "receipt": "",
            "warranty": "",
            "installment_contract": "",
            "files": []
        }

        send_message(
            chat_id,
            "🛒 Mahsulot muammosi\n\n"
            "Muammoingizni aniqlash uchun bir nechta savol beraman.\n\n"
            "1️⃣ Qanday mahsulot sotib oldingiz?\n\n"
            "Masalan: muzlatgich, televizor, telefon yoki boshqa mahsulot."
        )

        return "OK"

    # Boshqa asosiy bo‘limlar
    if text == "💰 Pulni qaytarish":
        send_message(
            chat_id,
            "💰 Pulni qaytarish\n\n"
            "Mahsulot yoki xizmat bilan bog‘liq muammoingizni batafsil yozing.",
            main_keyboard()
        )
        return "OK"

    if text == "🛠 Kafolat":
        send_message(
            chat_id,
            "🛠 Kafolat masalasi\n\n"
            "Mahsulot nomi, sotib olingan sana va kafolat muddati haqida ma’lumot yozing.",
            main_keyboard()
        )
        return "OK"

    if text == "📝 Ariza tayyorlash":
        send_message(
            chat_id,
            "📝 Ariza tayyorlash\n\n"
            "Muammoingizni batafsil yozing. Keyingi bosqichda ariza loyihasini tayyorlashga yordam beraman.",
            main_keyboard()
        )
        return "OK"

    if text == "📎 Kerakli hujjatlar":
        send_message(
            chat_id,
            "📎 Kerakli hujjatlar\n\n"
            "Muammo turiga qarab kerakli hujjatlarni aniqlashga yordam beraman.\n\n"
            "Odatda mavjud bo‘lsa:\n"
            "🧾 chek;\n"
            "🛡 kafolat taloni;\n"
            "📄 muddatli to‘lov shartnomasi;\n"
            "📸 mahsulot yoki nuqson fotosurati/video;\n"
            "📝 sotuvchiga murojaat va uning javobi."
        )
        return "OK"

    if text == "⚖️ Huquqlarim":
        send_message(
            chat_id,
            "⚖️ Huquqlarim\n\n"
            "Iste’molchi huquqlaringiz bo‘yicha ma’lumot olish uchun "
            "muammoingizni yozing.",
            main_keyboard()
        )
        return "OK"

    if text == "📞 Aloqa":
        send_message(
            chat_id,
            "📞 Aloqa\n\n"
            "Mening Huquqim\n"
            "🇺🇿 Iste’molchi huquqlari bo‘yicha amaliy yordam.",
            main_keyboard()
        )
        return "OK"

    # Agar foydalanuvchi mahsulot bo‘yicha savol-javobda bo‘lsa
    if chat_id in user_data:
        data = user_data[chat_id]
        step = data.get("step", 1)

        # 1. Mahsulot
        if step == 1:
            data["product"] = text
            data["step"] = 2

            send_message(
                chat_id,
                "2️⃣ Mahsulotni qachon sotib oldingiz?\n\n"
                "Sanani imkon qadar aniq yozing.\n"
                "Masalan: 2026-yil 15-sentabr."
            )

            return "OK"

        # 2. Sotib olingan sana
        if step == 2:
            data["purchase_date"] = text
            data["step"] = 3

            send_message(
                chat_id,
                "3️⃣ Mahsulotda qanday muammo yuzaga keldi?\n\n"
                "Muammoni imkon qadar batafsil yozing."
            )

            return "OK"

        # 3. Muammo
        if step == 3:
            data["problem"] = text
            data["step"] = 4

            send_message(
                chat_id,
                "4️⃣ Sotuvchiga murojaat qildingizmi?",
                yes_no_keyboard()
            )

            return "OK"

        # 4. Sotuvchiga murojaat
        if step == 4:
            if text == "✅ Ha":
                data["seller_contacted"] = "Ha"
                data["step"] = 5

                send_message(
                    chat_id,
                    "5️⃣ Sotuvchi sizga nima javob berdi?\n\n"
                    "Javobni imkon qadar batafsil yozing."
                )

            elif text == "❌ Yo‘q":
                data["seller_contacted"] = "Yo‘q"
                data["seller_response"] = "Murojaat qilinmagan"
                data["step"] = 6

                send_message(
                    chat_id,
                    "6️⃣ Mahsulot uchun chek bormi?",
                    yes_no_keyboard()
                )

            else:
                send_message(
                    chat_id,
                    "Iltimos, quyidagi tugmalardan birini tanlang.",
                    yes_no_keyboard()
                )

            return "OK"

        # 5. Sotuvchi javobi
        if step == 5:
            data["seller_response"] = text
            data["step"] = 6

            send_message(
                chat_id,
                "6️⃣ Mahsulot uchun chek bormi?",
                yes_no_keyboard()
            )

            return "OK"

        # 6. Chek
        if step == 6:
            if text == "✅ Ha":
                data["receipt"] = "Ha"
            elif text == "❌ Yo‘q":
                data["receipt"] = "Yo‘q"
            else:
                send_message(
                    chat_id,
                    "Iltimos, quyidagi tugmalardan birini tanlang.",
                    yes_no_keyboard()
                )
                return "OK"

            data["step"] = 7

            send_message(
                chat_id,
                "7️⃣ Kafolat taloni bormi?",
                yes_no_keyboard()
            )

            return "OK"

        # 7. Kafolat taloni
        if step == 7:
            if text == "✅ Ha":
                data["warranty"] = "Ha"
            elif text == "❌ Yo‘q":
                data["warranty"] = "Yo‘q"
            else:
                send_message(
                    chat_id,
                    "Iltimos, quyidagi tugmalardan birini tanlang.",
                    yes_no_keyboard()
                )
                return "OK"

            data["step"] = 8

            send_message(
                chat_id,
                "8️⃣ Mahsulot muddatli to‘lovga olinganmi?",
                yes_no_keyboard()
            )

            return "OK"

        # 8. Muddatli to‘lov
        if step == 8:
            if text == "✅ Ha":
                data["installment_contract"] = "Ha"
                data["step"] = 9

                send_message(
                    chat_id,
                    "📄 Muddatli to‘lov shartnomasi nusxasi bo‘lsa, "
                    "shu yerga yuboring.\n\n"
                    "PDF, rasm yoki boshqa hujjat ko‘rinishida yuborishingiz mumkin."
                )

            elif text == "❌ Yo‘q":
                data["installment_contract"] = "Yo‘q"
                data["step"] = 10

                send_message(
                    chat_id,
                    "📎 Endi mavjud bo‘lsa, quyidagi hujjatlarni yuborishingiz mumkin:\n\n"
                    "🧾 chek\n"
                    "🛡 kafolat taloni\n"
                    "📸 mahsulot yoki nuqson fotosurati\n"
                    "📝 sotuvchi bilan yozishmalar\n\n"
                    "Hujjat yubormasangiz, 'O‘tkazib yuborish' deb yozing."
                )

            else:
                send_message(
                    chat_id,
                    "Iltimos, quyidagi tugmalardan birini tanlang.",
                    yes_no_keyboard()
                )

            return "OK"

        # 9. Muddatli to‘lov shartnomasi fayli
        if step == 9:
            if document:
                data["files"].append({
                    "type": "document",
                    "file_id": document.get("file_id")
                })

                data["step"] = 10

                send_message(
                    chat_id,
                    "✅ Shartnoma qabul qilindi.\n\n"
                    "📎 Endi mavjud bo‘lsa, boshqa hujjatlarni yuborishingiz mumkin:\n\n"
                    "🧾 chek\n"
                    "🛡 kafolat taloni\n"
                    "📸 mahsulot yoki nuqson fotosurati\n"
                    "📝 sotuvchi bilan yozishmalar\n\n"
                    "Tayyor bo‘lsangiz, 'Tugatish' deb yozing."
                )

            elif text.lower() == "o‘tkazib yuborish" or text.lower() == "otkazib yuborish":
                data["step"] = 10

                send_message(
                    chat_id,
                    "Mayli.\n\n"
                    "📎 Mavjud bo‘lsa, boshqa hujjatlarni yuboring.\n\n"
                    "Tayyor bo‘lsangiz, 'Tugatish' deb yozing."
                )

            else:
                send_message(
                    chat_id,
                    "Iltimos, muddatli to‘lov shartnomasini fayl sifatida yuboring "
                    "yoki 'O‘tkazib yuborish' deb yozing."
                )

            return "OK"

        # 10. Qo‘shimcha hujjatlar
        if step == 10:

            if document:
                data["files"].append({
                    "type": "document",
                    "file_id": document.get("file_id")
                })

                send_message(
                    chat_id,
                    "✅ Hujjat qabul qilindi.\n\n"
                    "Yana hujjat yuborishingiz mumkin yoki 'Tugatish' deb yozing."
                )

                return "OK"

            if photo:
                largest_photo = photo[-1]

                data["files"].append({
                    "type": "photo",
                    "file_id": largest_photo.get("file_id")
                })

                send_message(
                    chat_id,
                    "✅ Rasm qabul qilindi.\n\n"
                    "Yana hujjat yoki rasm yuborishingiz mumkin yoki 'Tugatish' deb yozing."
                )

                return "OK"

            if text.lower() in ["tugatish", "tayyor", "tamom"]:
                data["step"] = 11

                summary = (
                    "✅ Ma’lumotlaringiz qabul qilindi.\n\n"
                    "📋 Murojaat ma’lumotlari:\n\n"
                    f"🛒 Mahsulot: {data['product']}\n"
                    f"📅 Sotib olingan sana: {data['purchase_date']}\n"
                    f"⚠️ Muammo: {data['problem']}\n"
                    f"📞 Sotuvchiga murojaat: {data['seller_contacted']}\n"
                    f"💬 Sotuvchi javobi: {data['seller_response']}\n"
                    f"🧾 Chek: {data['receipt']}\n"
                    f"🛡 Kafolat taloni: {data['warranty']}\n"
                    f"📄 Muddatli to‘lov shartnomasi: {data['installment_contract']}\n"
                    f"📎 Biriktirilgan fayllar: {len(data['files'])} ta\n\n"
                    "Keyingi bosqichda ushbu ma’lumotlar asosida "
                    "qonuniy yo‘l-yo‘riq va zarur hujjatlar bo‘yicha yordam berish mumkin."
                )

                send_message(
                    chat_id,
                    summary,
                    main_keyboard()
                )

                user_data.pop(chat_id, None)

                return "OK"

            send_message(
                chat_id,
                "📎 Hujjat, rasm yoki fayl yuboring.\n\n"
                "Yoki tayyor bo‘lsangiz, 'Tugatish' deb yozing."
            )

            return "OK"

    # Oddiy noma’lum xabar
    send_message(
        chat_id,
        "Menyudan kerakli bo‘limni tanlang yoki /start buyrug‘ini yuboring.",
        main_keyboard()
    )

    return "OK"


set_webhook()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
