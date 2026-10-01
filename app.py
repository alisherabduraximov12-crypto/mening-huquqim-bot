import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Foydalanuvchi holatlari.
# Keyinchalik buni SQLite/PostgreSQL bazaga o'tkazamiz.
user_data = {}


# =========================================================
# TELEGRAM YORDAMCHI FUNKSIYALAR
# =========================================================

def telegram(method, data=None):
    try:
        response = requests.post(
            f"{TELEGRAM_API}/{method}",
            json=data or {},
            timeout=20
        )
        return response.json()
    except Exception:
        return {}


def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        data["reply_markup"] = keyboard

    return telegram("sendMessage", data)


def main_keyboard():
    return {
        "keyboard": [
            [{"text": "🛒 Mahsulot muammosi"}],
            [{"text": "💰 Pulni qaytarish"}, {"text": "🛠 Kafolat"}],
            [{"text": "📎 Kerakli hujjatlar"}, {"text": "⚖️ Huquqlarim"}],
            [{"text": "📞 Aloqa"}]
        ],
        "resize_keyboard": True
    }


def yes_no_keyboard():
    return {
        "keyboard": [
            [{"text": "✅ Ha"}, {"text": "❌ Yo‘q"}],
            [{"text": "⬅️ Orqaga"}, {"text": "🏠 Bosh menyu"}]
        ],
        "resize_keyboard": True
    }


def skip_keyboard():
    return {
        "keyboard": [
            [{"text": "⏭ O‘tkazib yuborish"}],
            [{"text": "🏠 Bosh menyu"}]
        ],
        "resize_keyboard": True
    }


def finish_keyboard():
    return {
        "keyboard": [
            [{"text": "🏁 Yakunlash"}],
            [{"text": "🏠 Bosh menyu"}]
        ],
        "resize_keyboard": True
    }


# =========================================================
# WEBHOOK
# =========================================================

@app.route("/", methods=["GET"])
def home():
    return "Mening Huquqim bot is live!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}

    try:
        handle_update(update)
    except Exception as e:
        print("BOT ERROR:", e)

    return "OK"


def set_webhook():
    if not BOT_TOKEN or not RENDER_EXTERNAL_URL:
        return

    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"

    telegram(
        "setWebhook",
        {
            "url": webhook_url,
            "drop_pending_updates": True
        }
    )


# =========================================================
# BOSHLANG'ICH HOLAT
# =========================================================

def new_user(chat_id):
    user_data[chat_id] = {
        "section": None,
        "step": None,
        "product": "",
        "purchase_date": "",
        "problem": "",
        "seller_contacted": None,
        "seller_response": "",
        "service_contacted": None,
        "service_response": "",
        "receipt": None,
        "warranty": None,
        "installment": None,
        "contract": None,
        "evidence": [],
        "problem_type": None
    }


def get_user(chat_id):
    if chat_id not in user_data:
        new_user(chat_id)
    return user_data[chat_id]


# =========================================================
# START
# =========================================================

def start_bot(chat_id):
    new_user(chat_id)

    send_message(
        chat_id,
        "🇺🇿 Mening Huquqim botiga xush kelibsiz!\n\n"
        "Men iste’molchi huquqlari bo‘yicha amaliy yo‘l-yo‘riq beruvchi yordamchiman.\n\n"
        "Muammoingizni aniqlaymiz, mavjud hujjat va dalillarni hisobga olamiz, "
        "so‘ng tegishli qonuniy yo‘lni tushuntiramiz.\n\n"
        "Quyidagi menyudan kerakli bo‘limni tanlang:",
        main_keyboard()
    )


# =========================================================
# MAHSULOT MUAMMOSI
# =========================================================

def start_product_problem(chat_id):
    new_user(chat_id)

    data = user_data[chat_id]
    data["section"] = "product"
    data["step"] = "product"

    send_message(
        chat_id,
        "🛒 Mahsulot muammosi\n\n"
        "Muammoingizni to‘g‘ri aniqlash uchun bir nechta savol beraman.\n\n"
        "1️⃣ Qanday mahsulot sotib oldingiz?\n\n"
        "Masalan: muzlatgich, televizor, telefon, mebel va hokazo."
    )


def product_question(chat_id, text):
    data = get_user(chat_id)
    step = data["step"]

    # 1. Mahsulot
    if step == "product":
        data["product"] = text
        data["step"] = "purchase_date"

        send_message(
            chat_id,
            "2️⃣ Mahsulotni qachon sotib oldingiz?\n\n"
            "Sanani imkon qadar aniq yozing.\n"
            "Masalan: 15.09.2026"
        )
        return

    # 2. Xarid sanasi
    if step == "purchase_date":
        data["purchase_date"] = text
        data["step"] = "problem"

        send_message(
            chat_id,
            "3️⃣ Mahsulotda qanday muammo yuzaga keldi?\n\n"
            "Muammoni batafsil yozing."
        )
        return

    # 3. Muammo
    if step == "problem":
        data["problem"] = text
        data["step"] = "seller_contacted"

        send_message(
            chat_id,
            "4️⃣ Mahsulot sotib olingan savdo tashkilotiga "
            "murojaat qilganmisiz?",
            yes_no_keyboard()
        )
        return

    # 4. Savdo tashkiloti
    if step == "seller_contacted":
        if text == "✅ Ha":
            data["seller_contacted"] = True
            data["step"] = "seller_response"

            send_message(
                chat_id,
                "5️⃣ Savdo tashkiloti sizga qanday javob berdi?\n\n"
                "Javobni yozing. Agar yozma javob bo‘lsa, keyin uni "
                "hujjat sifatida yuborishingiz mumkin."
            )
        elif text == "❌ Yo‘q":
            data["seller_contacted"] = False
            data["step"] = "service_contacted"

            send_message(
                chat_id,
                "6️⃣ Mahsulot ishlab chiqaruvchisi yoki uning "
                "servis xizmatiga murojaat qilganmisiz?",
                yes_no_keyboard()
            )
        else:
            send_message(
                chat_id,
                "Iltimos, quyidagi tugmalardan birini tanlang.",
                yes_no_keyboard()
            )
        return

    # 5. Savdo javobi
    if step == "seller_response":
        data["seller_response"] = text
        data["step"] = "service_contacted"

        send_message(
            chat_id,
            "6️⃣ Mahsulot ishlab chiqaruvchisi yoki uning "
            "servis xizmatiga murojaat qilganmisiz?",
            yes_no_keyboard()
        )
        return

    # 6. Servis
    if step == "service_contacted":
        if text == "✅ Ha":
            data["service_contacted"] = True
            data["step"] = "service_response"

            send_message(
                chat_id,
                "7️⃣ Servis xizmati qanday xulosa yoki javob berdi?\n\n"
                "Masalan: ta’mirlash kerakligi, zavod nuqsoni, "
                "foydalanuvchi aybi yoki boshqa xulosa."
            )
        elif text == "❌ Yo‘q":
            data["service_contacted"] = False
            data["step"] = "receipt"

            send_message(
                chat_id,
                "8️⃣ Kassa yoki tovar cheki mavjudmi?",
                yes_no_keyboard()
            )
        else:
            send_message(
                chat_id,
                "Iltimos, quyidagi tugmalardan birini tanlang.",
                yes_no_keyboard()
            )
        return

    # 7. Servis javobi
    if step == "service_response":
        data["service_response"] = text
        data["step"] = "receipt"

        send_message(
            chat_id,
            "8️⃣ Kassa yoki tovar cheki mavjudmi?",
            yes_no_keyboard()
        )
        return

    # 8. Chek
    if step == "receipt":
        if text == "✅ Ha":
            data["receipt"] = True
        elif text == "❌ Yo‘q":
            data["receipt"] = False
        else:
            send_message(
                chat_id,
                "Iltimos, quyidagi tugmalardan birini tanlang.",
                yes_no_keyboard()
            )
            return

        data["step"] = "warranty"

        send_message(
            chat_id,
            "9️⃣ Kafolat taloni yoki kafolat muddati ko‘rsatilgan "
            "texnik hujjat mavjudmi?",
            yes_no_keyboard()
        )
        return

    # 9. Kafolat
    if step == "warranty":
        if text == "✅ Ha":
            data["warranty"] = True
        elif text == "❌ Yo‘q":
            data["warranty"] = False
        else:
            send_message(
                chat_id,
                "Iltimos, quyidagi tugmalardan birini tanlang.",
                yes_no_keyboard()
            )
            return

        data["step"] = "installment"

        send_message(
            chat_id,
            "🔟 Mahsulotni muddatli to‘lov yoki kredit asosida olganmisiz?",
            yes_no_keyboard()
        )
        return

    # 10. Muddatli to'lov
    if step == "installment":
        if text == "✅ Ha":
            data["installment"] = True
            data["step"] = "contract"

            send_message(
                chat_id,
                "📄 Muddatli to‘lov/kredit shartnomasi nusxasi mavjud bo‘lsa, "
                "shu yerga yuboring.\n\n"
                "Agar hozir yubormoqchi bo‘lmasangiz, "
                "«⏭ O‘tkazib yuborish»ni bosing.",
                skip_keyboard()
            )

        elif text == "❌ Yo‘q":
            data["installment"] = False
            data["step"] = "evidence"

            send_message(
                chat_id,
                "📎 Endi mavjud bo‘lsa, qo‘shimcha dalillarni yuboring:\n\n"
                "🧾 chek\n"
                "🛡 kafolat taloni\n"
                "📄 servis xulosasi\n"
                "📸 mahsulot yoki nuqson fotosi/video\n"
                "📝 sotuvchi bilan yozishmalar yoki javob\n\n"
                "Tayyor bo‘lgach «🏁 Yakunlash»ni bosing.",
                finish_keyboard()
            )
        else:
            send_message(
                chat_id,
                "Iltimos, quyidagi tugmalardan birini tanlang.",
                yes_no_keyboard()
            )
        return

    # 11. Shartnoma
    if step == "contract":
        if text in ["⏭ O‘tkazib yuborish", "O‘tkazib yuborish"]:
            data["contract"] = None
            data["step"] = "evidence"

            send_message(
                chat_id,
                "📎 Qo‘shimcha dalillarni yuborishingiz mumkin.\n\n"
                "Masalan: chek, kafolat taloni, servis xulosasi, "
                "foto/video yoki sotuvchi bilan yozishmalar.\n\n"
                "Tayyor bo‘lgach «🏁 Yakunlash»ni bosing.",
                finish_keyboard()
            )
            return

        send_message(
            chat_id,
            "Iltimos, shartnoma faylini yuboring yoki "
            "«⏭ O‘tkazib yuborish»ni bosing.",
            skip_keyboard()
        )
        return


# =========================================================
# FAYL VA FOTO QABUL QILISH
# =========================================================

def handle_document(chat_id, document):
    data = get_user(chat_id)

    file_id = document.get("file_id")

    if not file_id:
        return

    step = data.get("step")

    # Muddatli to'lov shartnomasi
    if step == "contract":
        data["contract"] = file_id
        data["step"] = "evidence"

        send_message(
            chat_id,
            "✅ Shartnoma qabul qilindi.\n\n"
            "Endi qo‘shimcha dalillarni yuborishingiz mumkin:\n"
            "🧾 chek\n"
            "🛡 kafolat taloni\n"
            "📄 servis xulosasi\n"
            "📸 foto/video\n"
            "📝 yozishmalar yoki javob.\n\n"
            "Tayyor bo‘lgach «🏁 Yakunlash»ni bosing.",
            finish_keyboard()
        )
        return

    # Boshqa hujjatlar
    data["evidence"].append({
        "type": "document",
        "file_id": file_id
    })

    send_message(
        chat_id,
        "✅ Hujjat qabul qilindi.\n\n"
        "Yana hujjat yoki dalil yuborishingiz mumkin. "
        "Tayyor bo‘lsangiz «🏁 Yakunlash»ni bosing.",
        finish_keyboard()
    )


def handle_photo(chat_id, photo):
    data = get_user(chat_id)

    if not photo:
        return

    file_id = photo[-1].get("file_id")

    if not file_id:
        return

    data["evidence"].append({
        "type": "photo",
        "file_id": file_id
    })

    send_message(
        chat_id,
        "✅ Foto qabul qilindi.\n\n"
        "Yana dalil yuborishingiz mumkin yoki "
        "«🏁 Yakunlash»ni bosing.",
        finish_keyboard()
    )


# =========================================================
# YAKUNIY TAHLIL
# =========================================================

def analyze_case(data):
    product = data.get("product", "").lower()
    problem = data.get("problem", "").lower()

    text = (
        "🔎 MUROJAAT BO‘YICHA DASTLABKI YO‘L-YO‘RIQ\n\n"
        f"🛒 Mahsulot: {data.get('product')}\n"
        f"📅 Xarid sanasi: {data.get('purchase_date')}\n\n"
        f"📝 Muammo: {data.get('problem')}\n\n"
    )

    # Uy-joy / qurilish
    housing_words = [
        "uy", "kvartira", "xonadon", "quruvchi",
        "qurilish", "novostroy", "yangi uy",
        "uy-joy", "uy joy"
    ]

    if any(word in product or word in problem for word in housing_words):
        text += (
            "🏠 Eslatma:\n"
            "Siz ko‘rsatgan holat uy-joy yoki qurilish munosabatlari "
            "bilan bog‘liq bo‘lishi mumkin.\n\n"
            "Bunday holatda masalaning aniq mazmuniga qarab tegishli "
            "vakolatli tashkilotga yoki sudga murojaat qilish masalasi "
            "ko‘rib chiqiladi.\n\n"
            "Bot ushbu holatni oddiy chakana tovar nizosi sifatida "
            "avtomatik baholamaydi.\n\n"
        )

    # Firibgarlik / jinoyat
    crime_words = [
        "firibgar", "aldadi", "o‘g‘irladi", "o'g'irladi",
        "jinoyat", "pulimni olib", "soxta hujjat"
    ]

    if any(word in problem for word in crime_words):
        text += (
            "⚠️ Muhim:\n"
            "Agar holatda jinoyat yoki firibgarlik alomatlari mavjud "
            "deb hisoblasangiz, huquqni muhofaza qiluvchi organlarga "
            "murojaat qilish masalasi ham ko‘rib chiqilishi mumkin.\n\n"
        )

    # Nuqsonli tovar
    defect_words = [
        "buzildi", "nuqson", "ishlamayapti", "ishlamaydi",
        "sindi", "yaroqsiz", "nosoz", "defekt", "ishdan chiqdi"
    ]

    if any(word in problem for word in defect_words):
        text += (
            "🛠 Nuqsonli tovar bo‘yicha:\n"
            "“Iste’molchilarning huquqlarini himoya qilish to‘g‘risida”gi "
            "Qonunning 13-moddasiga ko‘ra, shartnoma tuzish vaqtida "
            "aytib o‘tilmagan nuqson mavjud bo‘lsa, qonunda nazarda "
            "tutilgan talablarni qo‘yish imkoniyati mavjud.\n\n"
            "Talab turiga qarab tovarni almashtirish, nuqsonni bepul "
            "bartaraf etish, narxni kamaytirish yoki shartnomani bekor "
            "qilish va zararlarni qoplash masalalari yuzaga kelishi mumkin.\n\n"
            "📚 Huquqiy asos: Qonunning 13–17-moddalari.\n\n"
        )

    # Sotuvchiga murojaat qilinmagan
    if data.get("seller_contacted") is False:
        text += (
            "🏪 Siz savdo tashkilotiga hali murojaat qilmaganingizni "
            "ko‘rsatdingiz.\n\n"
            "Amaliy jihatdan avvalo sotuvchiga talabingizni aniq "
            "bayon qilgan holda murojaat qilish va murojaat qilinganini "
            "tasdiqlovchi dalilni saqlab qo‘yish foydali.\n\n"
        )

    # Servis
    if data.get("service_contacted") is False:
        text += (
            "🔧 Siz ishlab chiqaruvchi yoki servis xizmatiga "
            "murojaat qilmaganingizni ko‘rsatdingiz.\n\n"
            "Agar mahsulot kafolatli yoki texnik jihatdan murakkab "
            "tovar bo‘lsa, servis ko‘rigi/xulosasi muammoning sababini "
            "aniqlashda muhim dalil bo‘lishi mumkin.\n\n"
        )

    # Hujjatlar
    text += "📎 Mavjud ma’lumotlar:\n"

    text += "🧾 Chek: "
    text += "mavjud" if data.get("receipt") else "mavjud emas/ko‘rsatilmagan"
    text += "\n"

    text += "🛡 Kafolat hujjati: "
    text += "mavjud" if data.get("warranty") else "mavjud emas/ko‘rsatilmagan"
    text += "\n"

    text += "💳 Muddatli to‘lov/kredit: "
    text += "ha" if data.get("installment") else "yo‘q"
    text += "\n"

    if data.get("installment"):
        text += (
            "📄 Muddatli to‘lov shartnomasi: "
            + ("qabul qilingan" if data.get("contract") else "taqdim etilmagan")
            + "\n"
        )

    text += (
        "\n⚖️ Muhim:\n"
        "Ushbu bot dastlabki huquqiy yo‘l-yo‘riq beradi. "
        "Yakuniy huquqiy baho barcha hujjatlar, shartnoma, ekspertiza "
        "va boshqa dalillarni o‘rganish natijasiga bog‘liq bo‘lishi mumkin.\n\n"
        "Agar masala boshqa maxsus vakolatli davlat organi yoki sud "
        "vakolatiga kirsa, tegishli tashkilotga murojaat qilish "
        "masalasi ko‘rib chiqiladi."
    )

    return text


def finish_case(chat_id):
    data = get_user(chat_id)

    result = analyze_case(data)

    send_message(
        chat_id,
        result,
        main_keyboard()
    )

    # Holatni tozalaymiz
    new_user(chat_id)


# =========================================================
# STATIK BO'LIMLAR
# =========================================================

def show_documents(chat_id):
    send_message(
        chat_id,
        "📎 Kerakli hujjatlar\n\n"
        "Muammoga qarab quyidagilar foydali bo‘lishi mumkin:\n\n"
        "🧾 kassa yoki tovar cheki\n"
        "🛡 kafolat taloni / texnik pasport\n"
        "📄 muddatli to‘lov yoki kredit shartnomasi\n"
        "🔧 servis xulosasi\n"
        "📝 sotuvchining yozma javobi\n"
        "📸 mahsulot yoki nuqson fotosi/video\n"
        "📑 boshqa tegishli hujjatlar.\n\n"
        "Hujjatlarning qaysi biri kerakligi muammoning turiga "
        "qarab farq qiladi.",
        main_keyboard()
    )


def show_rights(chat_id):
    send_message(
        chat_id,
        "⚖️ Iste’molchi huquqlari\n\n"
        "Iste’molchi tovar va xizmatlar haqida to‘liq va ishonchli "
        "ma’lumot olish, sifatli va xavfsiz tovar olish, yetkazilgan "
        "zararni qoplashni talab qilish hamda o‘z huquqlarini himoya "
        "qilish uchun vakolatli davlat organlari va sudga murojaat "
        "qilish huquqiga ega.\n\n"
        "Nuqsonli tovar bo‘yicha Qonunning 13-moddasida nazarda "
        "tutilgan talablar mavjud.\n\n"
        "📚 Asosiy manbalar:\n"
        "• “Iste’molchilarning huquqlarini himoya qilish to‘g‘risida”gi Qonun\n"
        "• VMning 2003-yil 13-fevraldagi 75-son qarori bilan "
        "tasdiqlangan Chakana savdo qoidalari.\n\n"
        "Aniq holat bo‘yicha huquqiy yo‘l-yo‘riq olish uchun "
        "🛒 Mahsulot muammosi bo‘limidan foydalaning.",
        main_keyboard()
    )


def show_contact(chat_id):
    send_message(
        chat_id,
        "📞 Aloqa\n\n"
        "Murojaat yo‘nalishini aniqlash uchun avvalo "
        "🛒 Mahsulot muammosi bo‘limidagi savollarga javob bering.\n\n"
        "Shunda masalani vakolat doirasidan kelib chiqib "
        "yo‘naltirish osonroq bo‘ladi.",
        main_keyboard()
    )


# =========================================================
# UPDATE QABUL QILISH
# =========================================================

def handle_update(update):
    message = update.get("message")

    if not message:
        return

    chat = message.get("chat", {})
    chat_id = chat.get("id")

    if not chat_id:
        return

    # Foto
    if "photo" in message:
        handle_photo(chat_id, message["photo"])
        return

    # Hujjat
    if "document" in message:
        handle_document(chat_id, message["document"])
        return

    text = message.get("text", "").strip()

    if not text:
        return

    # START
    if text == "/start":
        start_bot(chat_id)
        return

    # Bosh menyu
    if text == "🏠 Bosh menyu":
        start_bot(chat_id)
        return

    # Mahsulot muammosi
    if text == "🛒 Mahsulot muammosi":
        start_product_problem(chat_id)
        return

    # Statik bo'limlar
    if text == "📎 Kerakli hujjatlar":
        show_documents(chat_id)
        return

    if text == "⚖️ Huquqlarim":
        show_rights(chat_id)
        return

    if text == "📞 Aloqa":
        show_contact(chat_id)
        return

    if text == "💰 Pulni qaytarish":
        send_message(
            chat_id,
            "💰 Pulni qaytarish masalasini to‘g‘ri aniqlash uchun "
            "avvalo mahsulot va muammo haqida ma’lumot olish kerak.\n\n"
            "🛒 Mahsulot muammosi bo‘limidan foydalaning.",
            main_keyboard()
        )
        return

    if text == "🛠 Kafolat":
        send_message(
            chat_id,
            "🛠 Kafolat masalasida mahsulot turi, kafolat muddati, "
            "servis xulosasi va sotuvchining javobi muhim bo‘lishi mumkin.\n\n"
            "🛒 Mahsulot muammosi bo‘limidan foydalanib, holatni "
            "bosqichma-bosqich kiriting.",
            main_keyboard()
        )
        return

    # Yakunlash
    if text == "🏁 Yakunlash":
        data = get_user(chat_id)

        if data.get("section") == "product":
            finish_case(chat_id)
        else:
            start_bot(chat_id)

        return

    # O'tkazib yuborish
    if text in ["⏭ O‘tkazib yuborish", "O‘tkazib yuborish"]:
        data = get_user(chat_id)

        if data.get("step") == "contract":
            data["contract"] = None
            data["step"] = "evidence"

            send_message(
                chat_id,
                "📎 Endi mavjud bo‘lsa, qo‘shimcha dalillarni yuboring.\n\n"
                "Tayyor bo‘lgach «🏁 Yakunlash»ni bosing.",
                finish_keyboard()
            )
        else:
            send_message(
                chat_id,
                "Bu bosqichda o‘tkazib yuborish mavjud emas."
            )

        return

    # Mahsulot savol-javoblari
    data = get_user(chat_id)

    if data.get("section") == "product":
        product_question(chat_id, text)
        return

    # Noma'lum buyruq
    send_message(
        chat_id,
        "Iltimos, menyudagi bo‘limlardan birini tanlang.",
        main_keyboard()
    )


# =========================================================
# ISHGA TUSHISH
# =========================================================

if __name__ == "__main__":
    set_webhook()

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
else:
    # Gunicorn ishga tushirganda webhook o'rnatiladi
    set_webhook()
