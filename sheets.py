import os
import json
import datetime
import gspread
from google.oauth2.service_account import Credentials

# ✅ إعداد صلاحيات الوصول المطلوبة
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"  # ← دي اللي كانت ناقصة
]

# ✅ تحميل بيانات الاعتماد من Environment Variable
creds_dict = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(creds)

# ✅ إنشاء شيت جديد حسب الشهر الحالي
def get_or_create_sheet():
    now = datetime.datetime.now()
    sheet_title = f"Expenses - {now.strftime('%Y-%m')}"

    try:
        sh = gc.open(sheet_title)
    except gspread.SpreadsheetNotFound:
        sh = gc.create(sheet_title)

        # ✨ مشاركة الشيت مع إيميلك الشخصي علشان يظهر في Google Drive عندك
        sh.share("amrmashaly935@gmail.com", perm_type="user", role="writer")  # ← غيّري الإيميل ده لو حابة

        worksheet = sh.get_worksheet(0)
        worksheet.update('A1:C1', [["Date", "Amount", "Description"]])
    
    return sh.get_worksheet(0)

# ✅ تسجيل المصروف في الشيت
def log_expense(date, amount, description):
    worksheet = get_or_create_sheet()
    worksheet.append_row([date, amount, description])
