
import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# =========================================================
# FOYDALANUVCHI HOLATLARI
# =========================================================

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
    except Exception as e:
        print("Telegram error:", e)
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
        print("BOT_TOKEN yoki RENDER_EXTERNAL_URL mavjud emas.")
        return

    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"

    result = telegram(
        "setWebhook",
        {
            "url": webhook_url,
            "drop_pending_updates": True
        }
    )

    print("Webhook:", result)


# =========================================================
# YANGI FOYDALANUVCHI
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
        "evidence_text": [],

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
        "Men iste’molchi huquqlari bo‘yicha amaliy yo‘l-yo‘riq "
        "beruvchi yordamchiman.\n\n"
        "Muammoingizni aniqlaymiz, mavjud hujjat va dalillarni "
        "hisobga olamiz, so‘ng tegishli qonuniy yo‘lni tushuntiramiz.\n\n"
        "Quyidagi menyudan kerakli bo‘limni tanlang:",
        main_keyboard()
    )


# =========================================================
# MAHSULOT MUAMMOSI BOSHLANISHI
# =========================================================

def start_product_problem(chat_id):
    new_user(chat_id)

    data = user_data[chat_id]

    data["section"] = "product"
    data["step"] = "product"

    send_message(
        chat_id,
        "🛒 Mahsulot muammosi\n\n"
        "Muammoingizni to‘g‘ri aniqlash uchun bir nechta "
        "savol beraman.\n\n"
        "1️⃣ Qanday mahsulot sotib oldingiz?\n\n"
        "Masalan: muzlatgich, televizor, telefon, mebel va hokazo."
    )


# =========================================================
# MAHSULOT SAVOL-JAVOBLARI
# =========================================================

def product_question(chat_id, text):

    data = get_user(chat_id)
    step = data.get("step")

    # =====================================================
    # 1. MAHSULOT
    # =====================================================

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


    # =====================================================
    # 2. XARID SANASI
    # =====================================================

    if step == "purchase_date":

        data["purchase_date"] = text
        data["step"] = "problem"

        send_message(
            chat_id,
            "3️⃣ Mahsulotda qanday muammo yuzaga keldi?\n\n"
            "Muammoni imkon qadar batafsil yozing.\n\n"
            "Masalan: “Muzlatgichni olganimdan 10 kun o‘tib "
            "sovutmay qo‘ydi.”"
        )
        return


    # =====================================================
    # 3. MUAMMO
    # =====================================================

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


    # =====================================================
    # 4. SOTUVCHIGA MUROJAAT
    # =====================================================

    if step == "seller_contacted":

        if text == "✅ Ha":

            data["seller_contacted"] = True
            data["step"] = "seller_response"

            send_message(
                chat_id,
                "5️⃣ Savdo tashkiloti sizga qanday javob berdi?\n\n"
                "Javobni yozing.\n\n"
                "Agar yozma javob bo‘lsa, keyin uni hujjat "
                "sifatida yuborishingiz mumkin."
            )
            return

        if text == "❌ Yo‘q":

            data["seller_contacted"] = False
            data["step"] = "service_contacted"

            send_message(
                chat_id,
                "6️⃣ Mahsulot ishlab chiqaruvchisi yoki uning "
                "servis xizmatiga murojaat qilganmisiz?",
                yes_no_keyboard()
            )
            return

        send_message(
            chat_id,
            "Iltimos, quyidagi tugmalardan birini tanlang.",
            yes_no_keyboard()
        )
        return


    # =====================================================
    # 5. SOTUVCHI JAVOBI
    #
    # MUHIM:
    # Bu bosqichda foydalanuvchi ISTALGAN MATNNI yozishi mumkin.
    # Hech qanday tugma talab qilinmaydi.
    # =====================================================

    if step == "seller_response":

        # Har qanday oddiy matn qabul qilinadi.
        # Masalan:
        # "Ta’mirlab beramiz dedi."
        # "Pulni qaytarmaymiz dedi."
        # "Servisga olib boring dedi."

        data["seller_response"] = text
        data["step"] = "service_contacted"

        send_message(
            chat_id,
            "6️⃣ Mahsulot ishlab chiqaruvchisi yoki uning "
            "servis xizmatiga murojaat qilganmisiz?",
            yes_no_keyboard()
        )
        return


    # =====================================================
    # 6. SERVISGA MUROJAAT
    # =====================================================

    if step == "service_contacted":

        if text == "✅ Ha":

            data["service_contacted"] = True
            data["step"] = "service_response"

            send_message(
                chat_id,
                "7️⃣ Servis xizmati qanday xulosa yoki javob berdi?\n\n"
                "Javobni imkon qadar batafsil yozing.\n\n"
                "Masalan:\n"
                "• zavod nuqsoni;\n"
                "• foydalanuvchi aybi;\n"
                "• ta’mirlash kerak;\n"
                "• ehtiyot qism almashtiriladi;\n"
                "• nuqson aniqlanmadi;\n"
                "• boshqa xulosa."
            )
            return

        if text == "❌ Yo‘q":

            data["service_contacted"] = False
            data["step"] = "receipt"

            send_message(
                chat_id,
                "8️⃣ Kassa yoki tovar cheki mavjudmi?",
                yes_no_keyboard()
            )
            return

        send_message(
            chat_id,
            "Iltimos, quyidagi tugmalardan birini tanlang.",
            yes_no_keyboard()
        )
        return


    # =====================================================
    # 7. SERVIS JAVOBI
    #
    # Bu ham oddiy matn qabul qiladi.
    # =====================================================

    if step == "service_response":

        data["service_response"] = text
        data["step"] = "receipt"

        send_message(
            chat_id,
            "8️⃣ Kassa yoki tovar cheki mavjudmi?",
            yes_no_keyboard()
        )
        return


    # =====================================================
    # 8. CHEK
    # =====================================================

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


    # =====================================================
    # 9. KAFOLAT
    # =====================================================

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
            "🔟 Mahsulotni muddatli to‘lov yoki kredit asosida "
            "olganmisiz?",
            yes_no_keyboard()
        )
        return


    # =====================================================
    # 10. KREDIT / MUDDATLI TO‘LOV
    # =====================================================

    if step == "installment":

        if text == "✅ Ha":

            data["installment"] = True
            data["step"] = "contract"

            send_message(
                chat_id,
                "📄 Muddatli to‘lov/kredit shartnomasi mavjud bo‘lsa, "
                "shu yerga yuboring.\n\n"
                "Agar hozir yubormoqchi bo‘lmasangiz, "
                "«⏭ O‘tkazib yuborish»ni bosing.",
                skip_keyboard()
            )
            return

        if text == "❌ Yo‘q":

            data["installment"] = False
            data["step"] = "evidence"

            send_message(
                chat_id,
                "📎 Endi mavjud bo‘lsa, qo‘shimcha dalillarni "
                "yuborishingiz mumkin:\n\n"
                "🧾 chek yoki xaridni tasdiqlovchi boshqa dalil\n"
                "🛡 kafolat taloni / texnik hujjat\n"
                "📄 servis xulosasi\n"
                "📸 mahsulot yoki nuqson fotosi/video\n"
                "📝 sotuvchining yozma javobi yoki yozishmalar\n\n"
                "Tayyor bo‘lgach «🏁 Yakunlash»ni bosing.",
                finish_keyboard()
            )
            return

        send_message(
            chat_id,
            "Iltimos, quyidagi tugmalardan birini tanlang.",
            yes_no_keyboard()
        )
        return


    # =====================================================
    # 11. SHARTNOMA
    # =====================================================

    if step == "contract":

        if text in ["⏭ O‘tkazib yuborish", "O‘tkazib yuborish"]:

            data["contract"] = None
            data["step"] = "evidence"

            send_message(
                chat_id,
                "📎 Qo‘shimcha dalillarni yuborishingiz mumkin.\n\n"
                "Masalan:\n"
                "🧾 chek\n"
                "🛡 kafolat hujjati\n"
                "📄 servis xulosasi\n"
                "📸 foto/video\n"
                "📝 sotuvchi bilan yozishmalar.\n\n"
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


    # =====================================================
    # 12. QO‘SHIMCHA DALILLAR
    # =====================================================

    if step == "evidence":

        if text == "🏁 Yakunlash":

            finish_case(chat_id)
            return

        if text == "🏠 Bosh menyu":

            start_bot(chat_id)
            return

        # Matnli dalil yoki qo‘shimcha izoh
        data["evidence_text"].append(text)

        send_message(
            chat_id,
            "✅ Ma’lumot saqlandi.\n\n"
            "Yana dalil yoki ma’lumot yuborishingiz mumkin.\n"
            "Tayyor bo‘lsangiz «🏁 Yakunlash»ni bosing.",
            finish_keyboard()
        )
        return


    # =====================================================
    # NOMA’LUM HOLAT
    # =====================================================

    send_message(
        chat_id,
        "Bu bosqich uchun ma’lumotni tushunmadim.\n\n"
        "Iltimos, savolga javob bering yoki "
        "«🏠 Bosh menyu»ni tanlang."
    )


# =========================================================
# FAYL QABUL QILISH
# =========================================================

def handle_document(chat_id, document):

    data = get_user(chat_id)

    fi
```
