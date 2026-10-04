import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Foydalanuvchi holatlari
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
# FOYDALANUVCHI HOLATI
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
# MAHSULOT SAVOL-JAVOB TIZIMI
# =========================================================

def product_question(chat_id, text):
    data = get_user(chat_id)
    step = data.get("step")

    # -----------------------------------------------------
    # 1. MAHSULOT
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 2. XARID SANASI
    # -----------------------------------------------------

    if step == "purchase_date":
        data["purchase_date"] = text
        data["step"] = "problem"

        send_message(
            chat_id,
            "3️⃣ Mahsulotda qanday muammo yuzaga keldi?\n\n"
            "Muammoni imkon qadar batafsil yozing."
        )
        return

    # -----------------------------------------------------
    # 3. MUAMMO
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 4. SOTUVCHIGA MUROJAAT
    # -----------------------------------------------------

    if step == "seller_contacted":

        if text == "✅ Ha":
            data["seller_contacted"] = True
            data["step"] = "seller_response"

            send_message(
                chat_id,
                "5️⃣ Savdo tashkiloti sizga qanday javob berdi?\n\n"
                "Javobni yozing.\n\n"
                "Agar yozma javob bo‘lsa, keyin uni hujjat sifatida "
                "yuborishingiz mumkin."
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

    # -----------------------------------------------------
    # 5. SOTUVCHI JAVOBI
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 6. SERVISGA MUROJAAT
    # -----------------------------------------------------

    if step == "service_contacted":

        if text == "✅ Ha":
            data["service_contacted"] = True
            data["step"] = "service_response"

            send_message(
                chat_id,
                "7️⃣ Servis xizmati qanday xulosa yoki javob berdi?\n\n"
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

    # -----------------------------------------------------
    # 7. SERVIS JAVOBI
    # -----------------------------------------------------

    if step == "service_response":

        data["service_response"] = text
        data["step"] = "receipt"

        send_message(
            chat_id,
            "8️⃣ Kassa yoki tovar cheki mavjudmi?",
            yes_no_keyboard()
        )
        return

    # -----------------------------------------------------
    # 8. CHEK
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 9. KAFOLAT
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 10. KREDIT / MUDDATLI TO‘LOV
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 11. SHARTNOMA
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 12. QO‘SHIMCHA DALILLAR
    # -----------------------------------------------------

    if step == "evidence":

        if text == "🏁 Yakunlash":
            finish_case(chat_id)
            return

        if text == "🏠 Bosh menyu":
            start_bot(chat_id)
            return

        # Oddiy matnli dalil / izoh
        data["evidence_text"].append(text)

        send_message(
            chat_id,
            "✅ Ma’lumot saqlandi.\n\n"
            "Yana dalil yoki ma’lumot yuborishingiz mumkin.\n"
            "Tayyor bo‘lsangiz «🏁 Yakunlash»ni bosing.",
            finish_keyboard()
        )
        return

    # -----------------------------------------------------
    # NOMA’LUM HOLAT
    # -----------------------------------------------------

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

    file_id = document.get("file_id")

    if not file_id:
        return

    step = data.get("step")

    # Kredit / muddatli to‘lov shartnomasi
    if step == "contract":

        data["contract"] = file_id
        data["step"] = "evidence"

        send_message(
            chat_id,
            "✅ Shartnoma qabul qilindi.\n\n"
            "Endi qo‘shimcha dalillarni yuborishingiz mumkin:\n\n"
            "🧾 chek\n"
            "🛡 kafolat hujjati\n"
            "📄 servis xulosasi\n"
            "📸 foto/video\n"
            "📝 sotuvchi bilan yozishmalar.\n\n"
            "Tayyor bo‘lgach «🏁 Yakunlash»ni bosing.",
            finish_keyboard()
        )
        return

    # Umumiy dalil
    if step == "evidence":

        data["evidence"].append({
            "type": "document",
            "file_id": file_id
        })

        send_message(
            chat_id,
            "✅ Hujjat qabul qilindi.\n\n"
            "Yana hujjat yoki dalil yuborishingiz mumkin.\n"
            "Tayyor bo‘lsangiz «🏁 Yakunlash»ni bosing.",
            finish_keyboard()
        )
        return

    send_message(
        chat_id,
        "📎 Hujjat qabul qilindi, ammo hozirgi bosqichda "
        "uni biriktirish talab qilinmaydi."
    )


# =========================================================
# FOTO QABUL QILISH
# =========================================================

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

    if data.get("step") in ["contract", "evidence"]:

        if data.get("step") == "contract":
            data["step"] = "evidence"

        send_message(
            chat_id,
            "✅ Foto qabul qilindi.\n\n"
            "Yana dalil yuborishingiz mumkin yoki "
            "«🏁 Yakunlash»ni bosing.",
            finish_keyboard()
        )
        return

    send_message(
        chat_id,
        "✅ Foto qabul qilindi."
    )


# =========================================================
# VIDEO QABUL QILISH
# =========================================================

def handle_video(chat_id, video):

    data = get_user(chat_id)

    file_id = video.get("file_id")

    if not file_id:
        return

    data["evidence"].append({
        "type": "video",
        "file_id": file_id
    })

    if data.get("step") == "contract":
        data["step"] = "evidence"

    send_message(
        chat_id,
        "✅ Video qabul qilindi.\n\n"
        "Yana dalil yuborishingiz mumkin yoki "
        "«🏁 Yakunlash»ni bosing.",
        finish_keyboard()
    )


# =========================================================
# YAKUNIY TAHLIL
# =========================================================

def analyze_case(data):

    product = data.get("product", "")
    problem = data.get("problem", "")

    product_low = product.lower()
    problem_low = problem.lower()

    text = (
        "🔎 MUROJAAT BO‘YICHA DASTLABKI YO‘L-YO‘RIQ\n\n"
        f"🛒 Mahsulot: {product}\n"
        f"📅 Xarid sanasi: {data.get('purchase_date')}\n\n"
        f"📝 Muammo: {problem}\n\n"
    )

    # =====================================================
    # VAKOLATNI DASTLABKI ANIQLASH
    # =====================================================

    housing_words = [
        "uy",
        "kvartira",
        "xonadon",
        "quruvchi",
        "qurilish",
        "novostroy",
        "yangi uy",
        "uy-joy",
        "uy joy",
        "kadastr",
        "yer uchastkasi"
    ]

    if any(word in product_low or word in problem_low
           for word in housing_words):

        text += (
            "🏠 VAKOLAT BO‘YICHA ESLATMA\n\n"
            "Siz ko‘rsatgan holatda uy-joy, qurilish, yer yoki "
            "kadastr munosabatlariga oid masala bo‘lishi mumkin.\n\n"
            "Bunday holat oddiy chakana tovar nizosi bo‘lmasligi "
            "mumkin. Masalaning aniq mazmuniga qarab tegishli "
            "vakolatli tashkilotga yoki sudga murojaat qilish "
            "masalasi ko‘rib chiqiladi.\n\n"
        )

    crime_words = [
        "firibgar",
        "firibgarlik",
        "aldadi",
        "o‘g‘irladi",
        "o'g'irladi",
        "jinoyat",
        "pulimni olib",
        "soxta hujjat"
    ]

    if any(word in problem_low for word in crime_words):

        text += (
            "⚠️ MUHIM\n\n"
            "Agar holatda firibgarlik yoki boshqa jinoyat "
            "alomatlari mavjud deb hisoblasangiz, huquqni "
            "muhofaza qiluvchi organlarga murojaat qilish "
            "masalasini ham ko‘rib chiqing.\n\n"
        )

    # =====================================================
    # NUQSONLI TOVAR
    # =====================================================

    defect_words = [
        "buzildi",
        "nuqson",
        "ishlamayapti",
        "ishlamaydi",
        "sindi",
        "yaroqsiz",
        "nosoz",
        "defekt",
        "ishdan chiqdi",
        "kamchilik"
    ]

    if any(word in problem_low for word in defect_words):

        text += (
            "🛠 NUQSONLI TOVAR BO‘YICHA\n\n"
            "Siz ko‘rsatgan holat nuqsonli tovar bilan bog‘liq "
            "bo‘lishi mumkin.\n\n"
            "Iste’molchilarning huquqlarini himoya qilish "
            "to‘g‘risidagi Qonunning 13-moddasida nuqsonli "
            "tovar bo‘yicha iste’molchining bir qator talablari, "
            "jumladan almashtirish, nuqsonni bartaraf etish, "
            "narxni kamaytirish yoki shartnomani bekor qilish "
            "bilan bog‘liq huquqlar nazarda tutilgan.\n\n"
            "Aniq talab mahsulotdagi nuqson, kafolat muddati, "
            "xarid holati va mavjud dalillarga qarab belgilanadi.\n\n"
        )

    # =====================================================
    # SOTUVCHI HOLATI
    # =====================================================

    if data.get("seller_contacted") is False:

        text += (
            "🏪 SOTUVCHIGA MUROJAAT\n\n"
            "Siz savdo tashkilotiga hali murojaat qilmaganingizni "
            "ko‘rsatdingiz.\n\n"
            "Amaliy jihatdan avvalo sotuvchiga talabingizni "
            "aniq bayon qilgan holda murojaat qilish va "
            "murojaat qilinganini tasdiqlovchi dalilni saqlash "
            "tavsiya etiladi.\n\n"
        )

    elif data.get("seller_contacted") is True:

        text += (
            "🏪 SOTUVCHINING JAVOBI\n\n"
            f"{data.get('seller_response')}\n\n"
        )

    # =====================================================
    # SERVIS
    # =====================================================

    if data.get("service_contacted") is False:

        text += (
            "🔧 SERVIS\n\n"
            "Siz ishlab chiqaruvchi yoki servis xizmatiga "
            "murojaat qilmaganingizni ko‘rsatdingiz.\n\n"
            "Agar mahsulotning nuqsoni yoki uning kelib chiqish "
            "sababi bo‘yicha texnik masalani aniqlash zarur bo‘lsa, "
            "servis ko‘rigi yoki xulosasi muhim dalil bo‘lishi mumkin.\n\n"
        )

    elif data.get("service_contacted") is True:

        text += (
            "🔧 SERVIS XULOSASI\n\n"
            f"{data.get('service_response')}\n\n"
        )

    # =====================================================
    # HUJJATLAR
    # =====================================================

    text += "📎 HUJJATLAR VA DALILLAR\n\n"

    if data.get("receipt") is True:
        text += "🧾 Chek: mavjud\n"
    elif data.get("receipt") is False:
        text += (
            "🧾 Chek: mavjud emas deb ko‘rsatildi\n"
            "   Xaridni tasdiqlovchi boshqa dalillar bo‘lsa, "
            "ularni ham saqlash muhim.\n"
        )
    else:
        text += "🧾 Chek: ko‘rsatilmagan\n"

    if data.get("warranty") is True:
        text += "🛡 Kafolat hujjati: mavjud\n"
    elif data.get("warranty") is False:
        text += "🛡 Kafolat hujjati: mavjud emas deb ko‘rsatildi\n"
    else:
        text += "🛡 Kafolat hujjati: ko‘rsatilmagan\n"

    if data.get("installment") is True:
        text += "💳 Muddatli to‘lov/kredit: ha\n"

        if data.get("contract"):
            text += "📄 Shartnoma: qabul qilingan\n"
        else:
            text += "📄 Shartnoma: taqdim etilmagan\n"

    elif data.get("installment") is False:
        text += "💳 Muddatli to‘lov/kredit: yo‘q\n"

    # Dalillar soni
    evidence_count = len(data.get("evidence", []))
    text_evidence_count = len(data.get("evidence_text", []))

    text += (
        f"📸 Yuklangan fayl/foto/video: {evidence_count} ta\n"
        f"📝 Qo‘shimcha yozma ma’lumot: {text_evidence_count} ta\n\n"
    )

    # =====================================================
    # AMALIY TAVSIYA
    # =====================================================

    text += (
        "📌 KEYINGI QADAM\n\n"
    )

    if data.get("seller_contacted") is False:

        text += (
            "1. Savdo tashkilotiga yozma ravishda talabingizni "
            "bildiring.\n"
            "2. Murojaat nusxasi yoki yuborilganini tasdiqlovchi "
            "dalilni saqlang.\n"
            "3. Mahsulotga oid mavjud hujjat va dalillarni "
            "saqlab qo‘ying.\n"
        )

    elif data.get("seller_contacted") is True:

        text += (
            "1. Savdo tashkilotining javobini saqlang.\n"
            "2. Agar mahsulot nuqsonining sababi bo‘yicha "
            "texnik masala mavjud bo‘lsa, servis xulosasini "
            "olish foydali bo‘lishi mumkin.\n"
            "3. Mavjud barcha dalillarni bir joyga jamlang.\n"
        )

    if data.get("service_contacted") is False:

        text += (
            "4. Zarur bo‘lsa, ishlab chiqaruvchi yoki servis "
            "xizmatiga murojaat qilib, mahsulot holati bo‘yicha "
            "xulosa oling.\n"
        )

    text += (
        "\n⚖️ MUHIM\n\n"
        "Ushbu bot dastlabki amaliy huquqiy yo‘l-yo‘riq beradi. "
        "Bot avtomatik ravishda iste’molchini yoki sotuvchini "
        "aybdor deb e’lon qilmaydi.\n\n"
        "Yakuniy baho hujjatlar, shartnoma, mahsulot holati, "
        "servis yoki ekspertiza xulosasi va boshqa dalillarga "
        "bog‘liq bo‘lishi mumkin.\n\n"
        "Agar masala boshqa maxsus vakolatli davlat organi yoki "
        "sud vakolatiga kirsa, tegishli tartibda o‘sha organga "
        "yoki sudga murojaat qilish masalasi ko‘rib chiqiladi."
    )

    return text


# =========================================================
# ISHNI YAKUNLASH
# =========================================================

def finish_case(chat_id):

    data = get_user(chat_id)

    if data.get("section") != "product":

        start_bot(chat_id)
        return

    result = analyze_case(data)

    send_message(
        chat_id,
        result,
        main_keyboard()
    )

    new_user(chat_id)


# =========================================================
# STATIK BO‘LIMLAR
# =========================================================

def show_documents(chat_id):

    send_message(
        chat_id,
        "📎 Kerakli hujjatlar\n\n"
        "Muammoga qarab quyidagilar foydali bo‘lishi mumkin:\n\n"
        "🧾 kassa yoki tovar cheki yoki xaridni tasdiqlovchi "
        "boshqa dalil\n"
        "🛡 kafolat taloni / texnik hujjat\n"
        "📄 muddatli to‘lov yoki kredit shartnomasi\n"
        "🔧 servis xulosasi\n"
        "📝 sotuvchining yozma javobi\n"
        "📸 mahsulot yoki nuqson fotosi/video\n"
        "📑 boshqa tegishli hujjatlar.\n\n"
        "Qaysi hujjat kerakligi muammoning turiga qarab farq qiladi.",
        main_keyboard()
    )


def show_rights(chat_id):

    send_message(
        chat_id,
        "⚖️ Iste’molchi huquqlari\n\n"
        "Iste’molchi tovar va xizmatlar haqida to‘liq va "
        "ishonchli ma’lumot olish, sifatli va xavfsiz tovar "
        "olish, qonunchilikda nazarda tutilgan hollarda "
        "yetkazilgan zararni qoplashni talab qilish hamda "
        "o‘z huquqlarini himoya qilish uchun vakolatli davlat "
        "organlari va sudga murojaat qilish huquqiga ega.\n\n"
        "Nuqsonli tovar bo‘yicha Qonunning 13–17-moddalarida "
        "tegishli huquq va talablar nazarda tutilgan.\n\n"
        "📚 Asosiy manbalar:\n"
        "• “Iste’molchilarning huquqlarini himoya qilish "
        "to‘g‘risida”gi Qonun\n"
        "• VMning 2003-yil 13-fevraldagi 75-son qarori bilan "
        "tasdiqlangan Chakana savdo qoidalari.\n\n"
        "Aniq holat bo‘yicha yo‘l-yo‘riq olish uchun "
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

    # -----------------------------------------------------
    # VIDEO
    # -----------------------------------------------------

    if "video" in message:
        handle_video(chat_id, message["video"])
        return

    # -----------------------------------------------------
    # FOTO
    # -----------------------------------------------------

    if "photo" in message:
        handle_photo(chat_id, message["photo"])
        return

    # -----------------------------------------------------
    # HUJJAT
    # -----------------------------------------------------

    if "document" in message:
        handle_document(chat_id, message["document"])
        return

    text = message.get("text", "").strip()

    if not text:
        return

    # -----------------------------------------------------
    # START
    # -----------------------------------------------------

    if text == "/start":
        start_bot(chat_id)
        return

    # -----------------------------------------------------
    # BOSH MENYU
    # -----------------------------------------------------

    if text == "🏠 Bosh menyu":
        start_bot(chat_id)
        return

    # -----------------------------------------------------
    # ORQAGA
    # -----------------------------------------------------

    if text == "⬅️ Orqaga":

        data = get_user(chat_id)

        if data.get("section") == "product":

            # Orqaga bosilganda hozircha xavfsiz ravishda
            # mahsulot bo‘limini qayta boshlaymiz.
            start_product_problem(chat_id)

        else:
            start_bot(chat_id)

        return

    # -----------------------------------------------------
    # MAHSULOT MUAMMOSI
    # -----------------------------------------------------

    if text == "🛒 Mahsulot muammosi":
        start_product_problem(chat_id)
        return

    # -----------------------------------------------------
    # STATIK BO‘LIMLAR
    # -----------------------------------------------------

    if text == "📎 Kerakli hujjatlar":
        show_documents(chat_id)
        return

    if text == "⚖️ Huquqlarim":
        show_rights(chat_id)
        return

    if text == "📞 Aloqa":
        show_contact(chat_id)
        return

    # -----------------------------------------------------
    # PULNI QAYTARISH
    # O‘ZGARISHSIZ QOLDIRILDI
    # -----------------------------------------------------

    if text == "💰 Pulni qaytarish":

        send_message(
            chat_id,
            "💰 Pulni qaytarish masalasini to‘g‘ri aniqlash uchun "
            "avvalo mahsulot va muammo haqida ma’lumot olish kerak.\n\n"
            "🛒 Mahsulot muammosi bo‘limidan foydalaning.",
            main_keyboard()
        )
        return

    # -----------------------------------------------------
    # KAFOLAT
    # O‘ZGARISHSIZ QOLDIRILDI
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # YAKUNLASH
    # -----------------------------------------------------

    if text == "🏁 Yakunlash":

        data = get_user(chat_id)

        if data.get("section") == "product":

            finish_case(chat_id)

        else:

            start_bot(chat_id)

        return

    # -----------------------------------------------------
    # O‘TKAZIB YUBORISH
    # -----------------------------------------------------

    if text in ["⏭ O‘tkazib yuborish", "O‘tkazib yuborish"]:

        data = get_user(chat_id)

        if data.get("step") == "contract":

            data["contract"] = None
            data["step"] = "evidence"

            send_message(
                chat_id,
                "📎 Endi mavjud bo‘lsa, qo‘shimcha dalillarni "
                "yuborishingiz mumkin.\n\n"
                "Tayyor bo‘lgach «🏁 Yakunlash»ni bosing.",
                finish_keyboard()
            )

        else:

            send_message(
                chat_id,
                "Bu bosqichda o‘tkazib yuborish mavjud emas."
            )

        return

    # -----------------------------------------------------
    # MAHSULOT SAVOL-JAVOBLARI
    # -----------------------------------------------------

    data = get_user(chat_id)

    if data.get("section") == "product":

        product_question(chat_id, text)
        return

    # -----------------------------------------------------
    # NOMA’LUM BUYRUQ
    # -----------------------------------------------------

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

    set_webhook()
