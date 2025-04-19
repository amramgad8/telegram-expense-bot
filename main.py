import os
import json
import re
from dotenv import load_dotenv
from parser import parse_expense  # تستخدم regex + GPT مع بعض
from sheets import log_expense  # ✅ جديد
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# تحميل المتغيرات من .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

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

def save_config(data):
    with open("config.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بيك! ابعتلي مصاريفك أو فويس، وأنا هسجلها 🧾")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    config = load_config()

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

    elif "صرف" in text and "كام" in text:
        total_spent = config["budget"] - config["remaining"]
        reply = (
            f"📊 إجمالي المصروفات لحد دلوقتي: {total_spent} جنيه\n"
            f"💰 المتبقي من الميزانية: {config['remaining']} جنيه"
        )

    else:
        result = parse_expense(text)
        if result["amount"] is not None:
            config["expenses"].append(result)
            config["remaining"] -= result["amount"]
            save_config(config)

            # ✅ تسجيل في Google Sheet
            log_expense(result["date"], result["amount"], result["description"])

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

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🤖 البوت شغال... افتح تليجرام وجرب تبعتله رسالة!")
app.run_polling()
