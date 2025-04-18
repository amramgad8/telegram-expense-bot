import os
import re
import json
from datetime import datetime
import openai
from dotenv import load_dotenv

# تحميل المفاتيح من .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# ---------- التحليل العادي (Regex) ----------
def parse_expense_regex(message: str) -> dict:
    amount_match = re.search(r"\d+", message)
    amount = int(amount_match.group()) if amount_match else None

    description = re.sub(r"\d+", "", message).strip(" -:،") if amount else message.strip()
    date = datetime.now().strftime("%Y-%m-%d")

    return {
        "amount": amount,
        "description": description,
        "date": date
    }


# ---------- التحليل الذكي باستخدام GPT ----------
def parse_expense_gpt(message: str) -> dict:
    prompt = f"""
    استخرج المبلغ والوصف والتاريخ (لو موجود) من الجملة التالية:
    "{message}"
    
    وارجعهم في شكل JSON يحتوي على:
    - amount: رقم فقط
    - description: وصف بسيط
    - date: تاريخ أو null لو مش مذكور
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        text = response.choices[0].message["content"]
        result = json.loads(text)

        # لو التاريخ مش موجود أو null نخلي تاريخ اليوم
        if not result.get("date"):
            result["date"] = datetime.now().strftime("%Y-%m-%d")

        # تأكيد أن المبلغ رقم
        result["amount"] = int(result["amount"]) if result.get("amount") else None

        return result

    except Exception as e:
        print("❌ خطأ من GPT:", e)
        return {
            "amount": None,
            "description": "",
            "date": datetime.now().strftime("%Y-%m-%d")
        }


# ---------- الدالة الرئيسية الموحدة ----------
def parse_expense(message: str) -> dict:
    result = parse_expense_regex(message)

    if result["amount"] is None:
        result = parse_expense_gpt(message)

    return result
