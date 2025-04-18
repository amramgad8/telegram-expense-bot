import os
import json
import re
from dotenv import load_dotenv
from parser import parse_expense  # تستخدم regex + GPT مع بعض
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# تحميل المتغيرات من .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# تحميل بيانات من config.json
def load_config():
    if not os.path.exists("config.json"):
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump({
                "budget": 0,
                "remaining": 0,
                "expenses": []
            }, f, indent=4, ensure_ascii=False)

    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)

# حفظ بيانات في config.json
def save_config(data):
    with open("config.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# أمر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بيك! ابعتلي مصاريفك أو فويس، وأنا هسجلها 🧾")

# استقبال الرسائل النصية
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    config = load_config()

    # تحديد الميزانية
    if "ميزانية" in text or "معايا" in text:
        amount_match = re.search(r"\d+", text)
        if amount_match:
            budget = int(amount_match.group())
            config["budget"] = budget
            config["remaining"] = budget
            config["expenses"] = []
            save_config(config)
            reply = f"✅ تم تحديد الميزانية الشهرية: {budget} جنيه"
        else:
            reply = "❌ معرفتش أستخرج الميزانية، ابعتلي مثلًا: معايا 2000 جنيه"

    # طلب معرفة المصروف الكلي أو المتبقي
    elif "صرف" in text and "كام" in text:
        total_spent = config["budget"] - config["remaining"]
        reply = (
            f"📊 إجمالي المصروفات لحد دلوقتي: {total_spent} جنيه\n"
            f"💰 المتبقي من الميزانية: {config['remaining']} جنيه"
        )

    else:
        # محاولة تحليل الرسالة كمصروف (Regex + GPT)
        result = parse_expense(text)
        if result["amount"] is not None:
            config["expenses"].append(result)
            config["remaining"] -= result["amount"]
            save_config(config)

            reply = (
                f"✔️ تم تسجيل المصروف:\n"
                f"📆 التاريخ: {result['date']}\n"
                f"💸 المبلغ: {result['amount']} جنيه\n"
                f"📝 الوصف: {result['description']}\n\n"
                f"💰 المتبقي من الميزانية: {config['remaining']} جنيه"
            )
        else:
            reply = "❌ معرفتش أستخرج المبلغ، ابعتلي الجملة بصيغة واضحة زي: صرفت 100 على لبس"

    await update.message.reply_text(reply)

# تشغيل البوت
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🤖 البوت شغال... افتح تليجرام وجرب تبعتله رسالة!")
app.run_polling()
