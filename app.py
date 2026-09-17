import streamlit as st
import datetime
import json
import os
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# Page Configuration & Hebrew RTL Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="מירוץ בוז'ולה 2026 - ניהול עומסים 8 ק״מ",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

rtl_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    direction: rtl;
    text-align: right;
    font-family: 'Rubik', sans-serif !important;
}

div[data-testid="stSidebar"] {
    direction: rtl;
    text-align: right;
}

.stTabs [data-baseweb="tab-list"] {
    direction: rtl;
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    font-size: 1rem;
    font-weight: 600;
    padding: 10px 18px;
}

.status-badge-green {
    background-color: #d1fae5;
    color: #065f46;
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 700;
    display: inline-block;
}

.status-badge-yellow {
    background-color: #fef3c7;
    color: #92400e;
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 700;
    display: inline-block;
}

.status-badge-red {
    background-color: #fee2e2;
    color: #991b1b;
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 700;
    display: inline-block;
}

.countdown-number {
    font-size: 2.2rem;
    font-weight: 800;
    color: #2563eb;
    line-height: 1;
}

.countdown-label {
    font-size: 0.78rem;
    color: #64748b;
    text-transform: uppercase;
}
</style>
"""
st.markdown(rtl_css, unsafe_allow_html=True)

RACE_DATETIME = datetime.datetime(2026, 10, 23, 7, 0, 0)
DATA_FILE = "achilles_data.json"

DEFAULT_WORKOUTS = [
  {
    "id": "w1-1",
    "week": 1,
    "dayName": "יום ד'",
    "dateStr": "16.09.2026",
    "isoDate": "2026-09-16",
    "type": "spin",
    "typeName": "ספינינג נפח + FBW 1",
    "title": "ספינינג נפח Zone 2 (45 דק') + אימון כוח FBW 1 (דגש סולאוס)",
    "desc": "45 דקות רכיבה רציפה בדופק אירובי נמוך/בינוני (Zone 2, סל\"ד 85–90) בישיבה מלאה עם מיקום פדל במרכז כף הרגל. מיד בסיום: אימון כוח FBW 1 (סולאוס בישיבה, סקווט, לחיצת חזה, חתירה, נשיאת מזוודה ואיזומטרי).",
    "focusTag": "ביסוס סובלנות וחיזוק השרשרת",
    "status": "pending",
    "notes": "",
    "isRun": False,
    "strengthSessionId": "w1-1",
    "fbwType": "fbw1"
  },
  {
    "id": "w1-2",
    "week": 1,
    "dayName": "יום ו'",
    "dateStr": "18.09.2026",
    "isoDate": "2026-09-18",
    "type": "run",
    "typeName": "Run/Walk מקוטעת",
    "title": "ריצה מקוטעת 5.5–6 ק\"מ (4 דק' ריצה / 1 דק' הליכה מהירה)",
    "desc": "חימום: החזקה איזומטרית 2 סטים של 45 שניות. גוף האימון: חזרות של 4 דקות ריצה קלה בקדנס 175 צעדים/דקה ומעבר ל-1 דקה הליכה מהירה. סה\"כ נפח: 5.5 עד 6 ק\"מ.",
    "focusTag": "הסתגלות אלסטית מבוקרת",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w1-3",
    "week": 1,
    "dayName": "יום א'",
    "dateStr": "20.09.2026",
    "isoDate": "2026-09-20",
    "type": "spin",
    "typeName": "ספינינג אינטרוולים + FBW 2",
    "title": "ספינינג אינטרוולים VO2max (5x4 דק') + אימון כוח FBW 2 (דדליפט וגסטרוקנמיוס)",
    "desc": "חימום 10 דק'. 5 אינטרוולים של 4 דקות בעצימות גבוהה (Zone 4/5) עם 2.5 דקות שחרור. ישיבה מלאה, פדל במרכז הרגל. לאחר מכן: אימון כוח FBW 2 (RDL, עליות עקב בעמידה, לאנג' אחורי, לחיצת כתפיים, חתירה בהטיה וגשר אגן).",
    "focusTag": "עומס קרדיווסקולרי וכוח שרשרת אחורית",
    "status": "pending",
    "notes": "",
    "isRun": False,
    "strengthSessionId": "w1-3",
    "fbwType": "fbw2"
  },
  {
    "id": "w1-4",
    "week": 1,
    "dayName": "יום ב'",
    "dateStr": "21.09.2026",
    "isoDate": "2026-09-21",
    "type": "run",
    "typeName": "ריצה קלה Run/Walk",
    "title": "ריצה קלה 5 ק\"מ (4 דק' ריצה / 1 דק' הליכה)",
    "desc": "ריצת התאוששות קלילה במקטעים של 4 דק' ריצה ו-1 דק' הליכה. דגש על צעדים קלים ושקטים. בסיום: 3 סטים של החזקה איזומטרית ל-45 שניות.",
    "focusTag": "נפח קל ובדיקת תגובת גיד 24h",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w2-1",
    "week": 2,
    "dayName": "יום ד'",
    "dateStr": "23.09.2026",
    "isoDate": "2026-09-23",
    "type": "spin",
    "typeName": "ספינינג + FBW 1",
    "title": "ספינינג נפח 50 דק' + אימון כוח FBW 1 (HSR סולאוס)",
    "desc": "50 דקות רכיבת Zone 2 רציפה בישיבה. לאחר מכן: ביצוע אימון כוח FBW 1 (דגש מיוחד על 4 סטים של עליות עקב בישיבה עם מוט לסולאוס בקצב 3-0-3).",
    "focusTag": "חיזוק מכני ממוקד לסולאוס",
    "status": "pending",
    "notes": "",
    "isRun": False,
    "strengthSessionId": "w2-1",
    "fbwType": "fbw1"
  },
  {
    "id": "w2-2",
    "week": 2,
    "dayName": "יום ו'",
    "dateStr": "25.09.2026",
    "isoDate": "2026-09-25",
    "type": "run",
    "typeName": "ריצה מקוטעת ארוכה",
    "title": "ריצה מקוטעת ארוכה 6.5 ק\"מ (6 דק' ריצה / 1 דק' הליכה)",
    "desc": "הארכת מקטע הריצה הרציפה ל-6 דקות, ומעבר ל-1 דקה הליכה מהירה. סה\"כ נפח: 6.5 ק\"מ. שמירה על קדנס מהיר וקבוע (170–180 צעדים/דקה). בסיום שחרור ומעקב נוקשות בוקר למחרת.",
    "focusTag": "התקדמות נפח ספציפי",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w2-3",
    "week": 2,
    "dayName": "יום א'",
    "dateStr": "27.09.2026",
    "isoDate": "2026-09-27",
    "type": "spin",
    "typeName": "ספינינג סף + FBW 2",
    "title": "ספינינג סף (4x5 דק' בקצב תחרותי) + אימון כוח FBW 2",
    "desc": "10 דק' חימום. 4 מקטעים של 5 דקות בעצימות סף אנאירובי (Sweet Spot, Zone 4) עם 3 דק' התאוששות. ישיבה בלבד, קדנס 90 RPM. לאחר מכן: אימון כוח FBW 2.",
    "focusTag": "סיבולת מהירות וסף נשימתי",
    "status": "pending",
    "notes": "",
    "isRun": False,
    "strengthSessionId": "w2-3",
    "fbwType": "fbw2"
  },
  {
    "id": "w2-4",
    "week": 2,
    "dayName": "יום ב'",
    "dateStr": "28.09.2026",
    "isoDate": "2026-09-28",
    "type": "run",
    "typeName": "ריצה קלה Run/Walk",
    "title": "ריצה קלה 5 ק\"מ (5 דק' ריצה / 1 דק' הליכה)",
    "desc": "5 ק\"מ קלים במתכונת 5 דק' ריצה ו-1 דק' הליכה. ריצה קלה לחלוטין ללא מאמץ נשימתי, עם נחיתת מרכז כף רגל (Midfoot).",
    "focusTag": "שמירה על סובלנות רקמתית",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w3-1",
    "week": 3,
    "dayName": "יום ד'",
    "dateStr": "30.09.2026",
    "isoDate": "2026-09-30",
    "type": "spin",
    "typeName": "ספינינג נפח + FBW 1",
    "title": "ספינינג נפח 45 דק' + אימון כוח FBW 1",
    "desc": "45 דקות רכיבת התאוששות אירובית מתונה (Zone 2) בסל\"ד נוח (85–90). לאחר מכן אימון כוח FBW 1 מלא לשמירה על כוח בסיסי.",
    "focusTag": "התאוששות אקטיבית וכוח",
    "status": "pending",
    "notes": "",
    "isRun": False,
    "strengthSessionId": "w3-1",
    "fbwType": "fbw1"
  },
  {
    "id": "w3-2",
    "week": 3,
    "dayName": "יום ו'",
    "dateStr": "02.10.2026",
    "isoDate": "2026-10-02",
    "type": "run",
    "typeName": "ריצת פריצת רציפות",
    "title": "ריצת פריצת רציפות 6.5–7 ק\"מ (1 ק\"מ חימום, 4 ק\"מ ריצה רציפה בקצב יעד, שחרור)",
    "desc": "אימון מפתח להסתגלות רציפה: 1 ק\"מ חימום קל משולב הליכה. 4 ק\"מ ריצה רציפה מלאה בקצב תחרות יעד (ללא עצירה להליכה אם הכאב מתחת ל-3). שחרור 1.5–2 ק\"מ קלים.",
    "focusTag": "מבחן רציפות לעומס אלסטי",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w3-3",
    "week": 3,
    "dayName": "יום א'",
    "dateStr": "04.10.2026",
    "isoDate": "2026-10-04",
    "type": "spin",
    "typeName": "ספינינג אינטרוולים + FBW 2",
    "title": "ספינינג אינטרוולים (5x3.5 דק') + אימון כוח FBW 2",
    "desc": "חימום 10 דק'. 5 מקטעי אינטרוול של 3.5 דקות בעצימות גבוהה עם 2 דק' התאוששות. שחרור 10 דק'. לאחר מכן אימון כוח FBW 2.",
    "focusTag": "עצימות אנאירובית ודופק גבוה",
    "status": "pending",
    "notes": "",
    "isRun": False,
    "strengthSessionId": "w3-3",
    "fbwType": "fbw2"
  },
  {
    "id": "w3-4",
    "week": 3,
    "dayName": "יום ב'",
    "dateStr": "05.10.2026",
    "isoDate": "2026-10-05",
    "type": "run",
    "typeName": "ריצה קלה",
    "title": "ריצה קלה 4.5 ק\"מ",
    "desc": "ריצה קלה ומשוחררת (ניתן לשלב 1 דק' הליכה באמצע במידת הצורך). דגש מלא על תחושת קלות ברגליים וקדנס גבוה.",
    "focusTag": "התאוששות פעילה לקראת שבוע שיא",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w4-1",
    "week": 4,
    "dayName": "יום ד'",
    "dateStr": "07.10.2026",
    "isoDate": "2026-10-07",
    "type": "spin",
    "typeName": "ספינינג + FBW 1 מקוצר",
    "title": "ספינינג קל/בינוני 40 דק' + FBW 1 מקוצר (שמירת כוח)",
    "desc": "רכיבת Zone 2 מתונה להזרמת דם. בסיום: 2 סטים בלבד לכל תרגיל ב-FBW 1 לשמירה על טונוס שרירי ללא גרימת עייפות מצטברת לקראת אימון השיא.",
    "focusTag": "שמירה על טונוס שרירי",
    "status": "pending",
    "notes": "",
    "isRun": False,
    "strengthSessionId": "w4-1",
    "fbwType": "fbw1"
  },
  {
    "id": "w4-2",
    "week": 4,
    "dayName": "יום ו'",
    "dateStr": "09.10.2026",
    "isoDate": "2026-10-09",
    "type": "run",
    "typeName": "אימון שיא תחרותי",
    "title": "אימון השיא – 7 ק\"מ (1 ק\"מ חימום, 5 ק\"מ רציפים בקצב מירוץ, 1 ק\"מ שחרור)",
    "desc": "סימולציית המירוץ העיקרית: 1 ק\"מ חימום Run/Walk. 5 ק\"מ רציפים בקצב תחרות מתוכנן. 1 ק\"מ ריצת שחרור איטית מאוד. מעקב הדוק של מודל 24 שעות בבוקר שבת!",
    "focusTag": "סימולציית שיא והסתגלות עומס מקסימלית",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w4-3",
    "week": 4,
    "dayName": "יום א'",
    "dateStr": "11.10.2026",
    "isoDate": "2026-10-11",
    "type": "spin",
    "typeName": "ספינינג אינטרוולים קצר",
    "title": "ספינינג אינטרוולים קצר (4x2.5 דק') + FBW 2 קל (2 סטים)",
    "desc": "אינטרוולים חדים וקצרים לשמירה על חדות נוירו-מוסקולרית ללא עייפות. לאחר מכן: FBW 2 בעומס מתון (2 סטים בלבד) לקראת כניסה לטייפר.",
    "focusTag": "חדות עצבית לקראת הטייפר",
    "status": "pending",
    "notes": "",
    "isRun": False,
    "strengthSessionId": "w4-3",
    "fbwType": "fbw2"
  },
  {
    "id": "w4-4",
    "week": 4,
    "dayName": "יום ב'",
    "dateStr": "12.10.2026",
    "isoDate": "2026-10-12",
    "type": "run",
    "typeName": "ריצת שחרור קלה",
    "title": "ריצת שחרור קלה 4 ק\"מ (Run/Walk)",
    "desc": "ריצת התאוששות קלילה (4 דק' ריצה / 1 דק' הליכה). הורדת סטרס מוחלטת מהגיד לקראת כניסה לטייפר.",
    "focusTag": "סגירת שבוע שיא ומעבר לטייפר",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w5-1",
    "week": 5,
    "dayName": "יום ד'",
    "dateStr": "14.10.2026",
    "isoDate": "2026-10-14",
    "type": "spin",
    "typeName": "ספינינג קליל + איזומטרי",
    "title": "ספינינג קליל 30 דק' + 4 סטים החזקה איזומטרית (ללא הרמת משקולות כבדות)",
    "desc": "30 דקות סיבוב רגליים קליל בהתנגדות נמוכה (Zone 1/2) להזרמת דם. בטייפר: הפסקת אימוני כוח כבדים, ביצוע החזקות איזומטריות בלבד לשמירה על גיד שקט.",
    "focusTag": "התחלת טייפר והתאוששות קולגן",
    "status": "pending",
    "notes": "",
    "isRun": False
  },
  {
    "id": "w5-2",
    "week": 5,
    "dayName": "יום ו'",
    "dateStr": "16.10.2026",
    "isoDate": "2026-10-16",
    "type": "run",
    "typeName": "ריצת שיוף וחדות",
    "title": "ריצת שיוף 3.5–4 ק\"מ עם 3 מקטעים של 100 מ' בקצב מירוץ",
    "desc": "ריצה קלה ונעימה (3.5 ק\"מ). בסיום: 3 מתגברות נינוחות של 100 מטר בקצב מירוץ לשמירה על חדות צעד, עם התאוששות הליכה מלאה ביניהן.",
    "focusTag": "שיוף מהירות וטייפר",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w5-3",
    "week": 5,
    "dayName": "יום א'",
    "dateStr": "18.10.2026",
    "isoDate": "2026-10-18",
    "type": "spin",
    "typeName": "ספינינג פתיחת רגליים",
    "title": "ספינינג פתיחת רגליים קל 20 דק'",
    "desc": "רכיבה קצרצרה וקלילה (20 דק') רק כדי להזרים דם ולשחרר נוקשות. ללא כל מאמץ נשימתי. 3 סטים החזקה איזומטרית בסיום.",
    "focusTag": "רענון רגליים",
    "status": "pending",
    "notes": "",
    "isRun": False
  },
  {
    "id": "w5-4",
    "week": 5,
    "dayName": "יום ב'",
    "dateStr": "19.10.2026",
    "isoDate": "2026-10-19",
    "type": "run",
    "typeName": "ריצה אחרונה בהחלט",
    "title": "ריצה אחרונה בהחלט – 2.5 ק\"מ קלילים",
    "desc": "2.5 ק\"מ קלים מאוד בקצב איטי. מטרתה הבלעדית היא תחושת ביטחון וקלילות. בסיום מתיחות קלות לירך הקדמית והאחורית בלבד.",
    "focusTag": "טייפר סופי",
    "status": "pending",
    "notes": "",
    "isRun": True
  },
  {
    "id": "w5-5",
    "week": 5,
    "dayName": "ימים ג'–ה'",
    "dateStr": "20–22.10.2026",
    "isoDate": "2026-10-20",
    "type": "rest",
    "typeName": "מנוחה מלאה + איזומטרי",
    "title": "ג'–ה' (20–22.10): אפס ריצה, מנוחה והחזקות איזומטריות בלבד",
    "desc": "3 ימי מנוחה מוחלטת מאימונים אירוביים. בצע רק 3 סטים של החזקה איזומטרית 45 שניות ביום לשמירה על ויסות כאב ומניעת התנוונות קולגן. מילוי מאגרי פחמימות ושתייה.",
    "focusTag": "הגנה מקסימלית על הגיד ומילוי מאגרים",
    "status": "pending",
    "notes": "",
    "isRun": False
  },
  {
    "id": "w5-6",
    "week": 5,
    "dayName": "יום ו' (23.10)",
    "dateStr": "23.10.2026",
    "isoDate": "2026-10-23",
    "type": "race",
    "typeName": "🏁 יום המירוץ!",
    "title": "יום המירוץ! 8 ק\"מ בוז'ולה ישראל (הנחיות חימום איזומטרי 35 דק' לפני הזינוק)",
    "desc": "זינוק ב-07:00! לו\"ז מדויק: ב-06:25 בצע 4 סטים של החזקה איזומטרית ל-45 שניות להשגת אפקט שיכוך כאב. בריצה: קדנס 175 צעדים/דקה, נחיתת מרכז כף רגל, וחלוקת כוחות חכמה. בהצלחה!",
    "focusTag": "הגשמת המטרה בבטחה",
    "status": "pending",
    "notes": "",
    "isRun": True
  }
]
DEFAULT_LOGS = [
  {
    "id": "log-1",
    "date": "2026-09-16",
    "stiffness": 4,
    "morningPain": 2.0,
    "postPain": 2.0,
    "sharpPain": False,
    "notes": "פתיחת תוכנית. גיד רגוע ושקט, נוקשות קלה שנעלמה תוך דקות ספורות."
  }
]
FBW_PROGRAMS = {
  "fbw1": {
    "title": "אימון כוח FBW 1 (דגש סולאוס בישיבה, סקווט, לחיצת חזה)",
    "subtitle": "ממוקד בידוד סולאוס (HSR), פיתוח כוח דחיפה בסיסי ויציבות ליבה ואגן",
    "exercises": [
      {
        "id": "fbw1-ex1",
        "name": "עליות עקב בישיבה עם מוט / משקולת (Seated Soleus Calf Raise)",
        "equipment": "ספסל + מוט (או משקולת יד כבדה על הברכיים)",
        "target": "שריר הסולאוס (Soleus) והחלק העמוק של גיד אכילס",
        "prescription": "4 סטים x 8–10 חזרות | קצב 3-0-3 (3 שנ' עלייה, 3 שנ' ירידה) | מנוחה: 90 שנ'",
        "cues": "שב על ספסל עם ברכיים כפופות ב-90 מעלות. הנח את המוט או המשקולת מעל הברכיים (עם מגבת/ריפוד). הרם את העקבים לאט ומבוקר, החזק שיא כיווץ לשנייה, ורד לאט במשך 3 שניות מלאות. ביצוע על רצפה ישרה ללא מדרגה!",
        "defaultSets": 4
      },
      {
        "id": "fbw1-ex2",
        "name": "גובלט סקווט עם קטלבל / סקווט עם מוט (Goblet / Barbell Squat)",
        "equipment": "קטלבל או מוט על הגב",
        "target": "ארבע-ראשי (Quadriceps), ישבן (Gluteus Maximus), זוקפי גב וליבה",
        "prescription": "3–4 סטים x 8–10 חזרות | קצב 2-1-2 | מנוחה: 90 שנ'",
        "cues": "החזק קטלבל צמוד לחזה או מוט יציב על הגב. רד בעומק מבוקר תוך שמירה על עקבים צמודים לקרקע ועמוד שדרה ניטרלי. עלה בכוח דרך מרכז כף הרגל.",
        "defaultSets": 3
      },
      {
        "id": "fbw1-ex3",
        "name": "לחיצת חזה על ספסל עם מוט או משקולות יד (Barbell / DB Bench Press)",
        "equipment": "ספסל שטוח + מוט או זוג משקולות יד",
        "target": "חזה גדול (Pec Major), דלתואיד קדמי, תלת-ראשי (Triceps)",
        "prescription": "3–4 סטים x 8–10 חזרות | קצב 2-0-1 | מנוחה: 90 שנ'",
        "cues": "הורד את המשקל באופן מבוקר אל קו החזה התחתון תוך כיווץ שכמות ונעילת רגליים ברצפה. דחף בעוצמה למעלה עד יישור מבוקר של המרפקים.",
        "defaultSets": 3
      },
      {
        "id": "fbw1-ex4",
        "name": "חתירה במסור עם משקולת יד בהישענות על ספסל (Single-Arm DB Row)",
        "equipment": "משקולת יד + ספסל",
        "target": "רחב גבי (Latissimus Dorsi), מעוינים, טרפז אמצעי וכופפי מרפק",
        "prescription": "3 סטים x 10–12 חזרות לכל צד | מנוחה: 60 שנ'",
        "cues": "הנח ברך ויד תומכת על הספסל, גו מקביל לקרקע. משוך את המשקולת לכיוון המותן/כיס אחורי ללא סיבוב אגן, וכווץ את השכמה בסיום.",
        "defaultSets": 3
      },
      {
        "id": "fbw1-ex5",
        "name": "נשיאת מזוודה עם קטלבל (Kettlebell Suitcase Carry)",
        "equipment": "קטלבל כבד (ביד אחת)",
        "target": "מייצבי אגן (Gluteus Medius), שרירי הליבה האלכסוניים (Obliques), קרסול",
        "prescription": "3 סטים x 35–40 שניות הליכה לכל צד | מנוחה: 60 שנ'",
        "cues": "החזק קטלבל ביד אחת ולך בצעדים מדודים בקו ישר. שמור על גו זקוף לחלוטין ואל תאפשר למשקל להטות את הגוף הצידה (Anti-lateral flexion).",
        "defaultSets": 3
      },
      {
        "id": "fbw1-ex6",
        "name": "החזקות איזומטריות לגיד אכילס (Achilles Mid-Range Isometric Holds)",
        "equipment": "משקל גוף או אחיזת משקולת יד",
        "target": "קומפלקס אכילס-סולאוס-תאומים",
        "prescription": "3–4 סטים x 45 שניות | מנוחה: 60 שנ'",
        "cues": "עמוד על שתי הרגליים (או רגל אחת לפי רמת כאב) בעלייה קלה של העקבים על משטח ישר. החזק סטטי ב-70% כוח לשיכוך כאב וויסות עצבי.",
        "defaultSets": 3
      }
    ]
  },
  "fbw2": {
    "title": "אימון כוח FBW 2 (דגש דדליפט רומני, עליות עקב בעמידה, ספליט)",
    "subtitle": "ממוקד שרשרת אחורית, כוח חד-רגלי למניעת א-סימטריה, ועומס תאומים מבוקר",
    "exercises": [
      {
        "id": "fbw2-ex1",
        "name": "דדליפט רומני עם מוט או משקולות יד (Barbell / DB Romanian Deadlift - RDL)",
        "equipment": "מוט או זוג משקולות יד כבדות",
        "target": "המסטרינגס (Hamstrings), ישבן גדול (Gluteus Maximus), זוקפי גב",
        "prescription": "3–4 סטים x 8–10 חזרות | קצב 3-1-1 | מנוחה: 90 שנ'",
        "cues": "עמוד ברוחב אגן. בצע הטיית אגן לאחור (Hip Hinge) עם ברכיים כפופות קלות ורכות. רד עד מתחת לברכיים תוך מתיחה חזקה בהמסטרינגס, ועלה דרך כיווץ הישבן.",
        "defaultSets": 4
      },
      {
        "id": "fbw2-ex2",
        "name": "עליות עקב בעמידה עם משקולות יד על משטח ישר (Standing DB Calf Raise)",
        "equipment": "זוג משקולות יד / קטלבלס",
        "target": "שריר התאומים (Gastrocnemius) וחלק אחורי של הגיד",
        "prescription": "3–4 סטים x 10–12 חזרות | קצב 3-1-3 (3 שנ' עלייה, 1 החזקה, 3 ירידה)",
        "cues": "עמידה עם ברכיים ישרות לחלוטין ומשקולות לצדי הגוף. עלה על כריות הבהונות באיטיות, החזק שיא כיווץ לשנייה אחת ורד במשך 3 שניות. רצפה ישרה בלבד!",
        "defaultSets": 3
      },
      {
        "id": "fbw2-ex3",
        "name": "לאנג' לאחור / ספליט סקווט עם משקולות יד (DB Reverse Lunge / Split Squat)",
        "equipment": "זוג משקולות יד (וספסל לבולגרי במידת הרצון)",
        "target": "ארבע-ראשי, גלוטאוס מקסימוס ומדיוס, שרירי ייצוב כף הרגל",
        "prescription": "3 סטים x 8–10 חזרות לכל רגל | מנוחה: 75 שנ'",
        "cues": "קח צעד יציב לאחור ורד בניצב לקרקע עד שהברך האחורית כמעט נוגעת ברצפה. דחף דרך מרכז ועקב הרגל הקדמית. מחזק כוח חד-רגלי ומאזן א-סימטריה.",
        "defaultSets": 3
      },
      {
        "id": "fbw2-ex4",
        "name": "לחיצת כתפיים בעמידה או בישיבה עם משקולות יד / קטלבל (DB/KB Overhead Press)",
        "equipment": "משקולות יד או קטלבל (וספסל)",
        "target": "שרירי הכתף (דלתואיד), טרפז, תלת-ראשי ושרירי הליבה",
        "prescription": "3 סטים x 8–10 חזרות | מנוחה: 90 שנ'",
        "cues": "שמור על בטן וזקופים נעולים. דחף את המשקולות מעל הראש בקו ישר עד נעילה מבוקרת, ללא הקשתת יתר של הגב התחתון.",
        "defaultSets": 3
      },
      {
        "id": "fbw2-ex5",
        "name": "חתירה בהטיית גו עם מוט (Barbell Bent-Over Row)",
        "equipment": "מוט אולימפי / מוט משקולות",
        "target": "גב עליון, רחב גבי, מעוינים וזוקפים",
        "prescription": "3 סטים x 8–10 חזרות | מנוחה: 90 שנ'",
        "cues": "הטה גו בכ-45–60 מעלות עם ברכיים רכות. אחיזה ברוחב כתפיים. משוך את המוט בצמוד לירכיים עד מגע בטבור וכווץ שכמות.",
        "defaultSets": 3
      },
      {
        "id": "fbw2-ex6",
        "name": "גשר אגן חד-רגלי עם קטלבל / משקולת (Single-Leg Glute Bridge with KB)",
        "equipment": "קטלבל או משקולת מונחת על הירך",
        "target": "ישבן גדול (Gluteus Maximus), זוקפי אגן והמסטרינגס",
        "prescription": "3 סטים x 10–12 חזרות לכל רגל | מנוחה: 60 שנ'",
        "cues": "שכב על הגב, רגל אחת כפופה עם עקב ברצפה, רגל שנייה מורמת. דחף את האגן למעלה בקו ישר תוך כיווץ מקסימלי של הישבן, מבלי לתת לאגן לצנוח.",
        "defaultSets": 3
      }
    ]
  }
}
STRENGTH_SESSIONS_META = [
  {
    "id": "w1-1",
    "name": "שבוע 1 - יום ד' (16.09.2026)",
    "program": "fbw1",
    "label": "שבוע 1 - ד' 16.09 (FBW 1)"
  },
  {
    "id": "w1-3",
    "name": "שבוע 1 - יום א' (20.09.2026)",
    "program": "fbw2",
    "label": "שבוע 1 - א' 20.09 (FBW 2)"
  },
  {
    "id": "w2-1",
    "name": "שבוע 2 - יום ד' (23.09.2026)",
    "program": "fbw1",
    "label": "שבוע 2 - ד' 23.09 (FBW 1)"
  },
  {
    "id": "w2-3",
    "name": "שבוע 2 - יום א' (27.09.2026)",
    "program": "fbw2",
    "label": "שבוע 2 - א' 27.09 (FBW 2)"
  },
  {
    "id": "w3-1",
    "name": "שבוע 3 - יום ד' (30.09.2026)",
    "program": "fbw1",
    "label": "שבוע 3 - ד' 30.09 (FBW 1)"
  },
  {
    "id": "w3-3",
    "name": "שבוע 3 - יום א' (04.10.2026)",
    "program": "fbw2",
    "label": "שבוע 3 - א' 04.10 (FBW 2)"
  },
  {
    "id": "w4-1",
    "name": "שבוע 4 - יום ד' (07.10.2026)",
    "program": "fbw1",
    "label": "שבוע 4 - ד' 07.10 (FBW 1 - שיא 2 סטים)"
  },
  {
    "id": "w4-3",
    "name": "שבוע 4 - יום א' (11.10.2026)",
    "program": "fbw2",
    "label": "שבוע 4 - א' 11.10 (FBW 2 - שיא 2 סטים)"
  },
  {
    "id": "free-fbw1",
    "name": "אימון חופשי / נוסף (FBW 1)",
    "program": "fbw1",
    "label": "אימון חופשי - FBW 1"
  },
  {
    "id": "free-fbw2",
    "name": "אימון חופשי / נוסף (FBW 2)",
    "program": "fbw2",
    "label": "אימון חופשי - FBW 2"
  }
]

def load_app_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "workouts": DEFAULT_WORKOUTS,
        "logs": DEFAULT_LOGS,
        "strengthSessions": {}
    }

def save_app_data():
    data = {
        "workouts": st.session_state.workouts,
        "logs": st.session_state.logs,
        "strengthSessions": st.session_state.strengthSessions
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "workouts" not in st.session_state:
    saved = load_app_data()
    st.session_state.workouts = saved.get("workouts", DEFAULT_WORKOUTS)
    st.session_state.logs = saved.get("logs", DEFAULT_LOGS)
    st.session_state.strengthSessions = saved.get("strengthSessions", {})
    st.session_state.activeStrengthSessionId = "w1-1"

def calc_tendon_status(pain, stiffness, sharp):
    if sharp or pain > 4 or stiffness > 20:
        return "red", "התלקחות / רגישות יתר (Red) - המר ריצה בספינינג ואיזומטרי", "status-badge-red"
    if pain == 4 or (10 <= stiffness <= 20):
        return "yellow", "עומס גבולי (Yellow) - שמור נפח, הימנע מהארכת אינטרוולים", "status-badge-yellow"
    return "green", "תקין (Green) - המשך לפי התוכנית המתוכננת", "status-badge-green"

latest_log = st.session_state.logs[-1] if st.session_state.logs else None
if latest_log:
    current_status, current_status_desc, badge_cls = calc_tendon_status(
        latest_log.get("morningPain", 0),
        latest_log.get("stiffness", 0),
        latest_log.get("sharpPain", False)
    )
else:
    current_status, current_status_desc, badge_cls = "green", "תקין (Green)", "status-badge-green"

# Header
col_head1, col_head2 = st.columns([2.5, 1.5])
with col_head1:
    st.markdown("<span style='color: #ef4444; font-weight:700;'>🏁 יעד תחרותי ראשי | 8 ק״מ</span>", unsafe_allow_html=True)
    st.title("מירוץ בוז'ולה ישראל 2026")
    st.caption("מערכת ניהול עומסים, תוכנית ריצה-ספינינג ואימוני כוח FBW מותאמים לגיד אכילס")

with col_head2:
    now = datetime.datetime.now()
    diff = RACE_DATETIME - now
    if diff.total_seconds() > 0:
        days = diff.days
        hours = diff.seconds // 3600
        mins = (diff.seconds // 60) % 60
        st.markdown(f"""
        <div style="background: #0f172a; color: white; padding: 14px 18px; border-radius: 12px; text-align: center;">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">זינוק בעוד:</div>
            <div style="display: flex; justify-content: center; gap: 14px; margin-top: 6px;">
                <div><div class="countdown-number" style="color:#38bdf8;">{days:02d}</div><div class="countdown-label">ימים</div></div>
                <div><div class="countdown-number" style="color:#38bdf8;">{hours:02d}</div><div class="countdown-label">שעות</div></div>
                <div><div class="countdown-number" style="color:#38bdf8;">{mins:02d}</div><div class="countdown-label">דקות</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

col_s1, col_s2 = st.columns([1.5, 2.5])
with col_s1:
    st.markdown(f"**סטטוס גיד 24 שעות:** <span class='{badge_cls}'>{current_status_desc}</span>", unsafe_allow_html=True)
with col_s2:
    st.markdown("**תאריך מירוץ:** יום שישי, 23 באוקטובר 2026 | שעת זינוק: 07:00")

st.divider()

# Navigation
tab_sched, tab_strength, tab_track, tab_runwalk, tab_protocols = st.tabs([
    "📅 תוכנית 5 שבועות",
    "💪 אימוני כוח FBW 1 & 2",
    "🩺 ניטור גיד יומי (24h)",
    "⏱️ עוזר ריצה Run/Walk ודגשים",
    "📖 פרוטוקולים והנחיות קליניות"
])

# TAB 1
with tab_sched:
    total_workouts = len(st.session_state.workouts)
    completed_workouts = len([w for w in st.session_state.workouts if w["status"] in ["completed", "modified"]])
    progress_pct = int((completed_workouts / total_workouts) * 100) if total_workouts else 0

    st.progress(progress_pct / 100.0, text=f"הושלמו או הותאמו {completed_workouts} מתוך {total_workouts} אימונים מתוזמנים ({progress_pct}%)")

    if current_status == "red":
        st.error("⚠️ התרעת עומס אדומה פעילה: הגיד ברגישות יתר. מומלץ להמיר את אימון הריצה הקרוב בספינינג Zone 2 (45 דק') והחזקות איזומטריות (45 שנ').")

    week_filter = st.radio("סנן לפי שבוע:", ["כל 5 השבועות", "שבוע 1", "שבוע 2", "שבוע 3", "שבוע 4 (שיא)", "שבוע 5 (טייפר ומירוץ)"], horizontal=True)
    week_map = {"שבוע 1": 1, "שבוע 2": 2, "שבוע 3": 3, "שבוע 4 (שיא)": 4, "שבוע 5 (טייפר ומירוץ)": 5}
    target_week = week_map.get(week_filter, None)

    filtered_workouts = [w for w in st.session_state.workouts if target_week is None or w["week"] == target_week]

    for w in filtered_workouts:
        with st.expander(f"{w['dayName']} ({w['dateStr']}) | {w['title']} [{w['status']}]", expanded=(w['status'] == 'pending')):
            col_w1, col_w2 = st.columns([3, 1])
            with col_w1:
                st.markdown(f"**סוג אימון:** `{w['typeName']}` | **מיקוד:** `{w['focusTag']}`")
                st.write(w["desc"])
                
                if current_status == "red" and w.get("isRun") and w["status"] == "pending":
                    st.warning("⚠️ מומלץ להמיר אימון ריצה זה לספינינג ואיזומטרי עקב התרעת כאב.")
                    if st.button(f"המר אימון לאופניים + איזומטרי ({w['id']})"):
                        w["title"] = "ספינינג מותאם 45 דק' + 4 סטים החזקה איזומטרית (עומס אדום)"
                        w["desc"] = "האימון הומר לספינינג נפח Zone 2 רציף בישיבה בלבד (פדל במרכז הרגל) + 4 סטים של 45 שניות החזקה איזומטרית."
                        w["status"] = "modified"
                        w["isRun"] = False
                        save_app_data()
                        st.rerun()

            with col_w2:
                status_opts = ["pending", "completed", "modified", "skipped"]
                status_labels = {"pending": "טרם בוצע", "completed": "בוצע ✓", "modified": "הותאם", "skipped": "דולג"}
                current_idx = status_opts.index(w["status"]) if w["status"] in status_opts else 0
                new_status = st.selectbox("סטטוס ביצוע:", status_opts, index=current_idx, format_func=lambda x: status_labels[x], key=f"status_{w['id']}")
                if new_status != w["status"]:
                    w["status"] = new_status
                    save_app_data()
                    st.rerun()

                new_notes = st.text_input("הערות אימון:", value=w.get("notes", ""), key=f"note_{w['id']}")
                if new_notes != w.get("notes", ""):
                    w["notes"] = new_notes
                    save_app_data()

                if w.get("strengthSessionId"):
                    st.info(f"🏋️ כולל אימון כוח {w.get('fbwType', '').upper()}")

# TAB 2
with tab_strength:
    st.subheader("🏋️ תוכנית אימוני כוח לכל הגוף (FBW 1 & FBW 2)")
    st.caption("ציוד: מוט, משקולות יד, ספסל, קטלבל. כל מועד אימון נשמר כרשומה נפרדת וספציפית.")

    session_choices = [s["id"] for s in STRENGTH_SESSIONS_META]
    session_labels = {s["id"]: s["name"] for s in STRENGTH_SESSIONS_META}

    sel_session_id = st.selectbox(
        "בחר מועד אימון כוח לתיעוד ולמעקב:",
        session_choices,
        format_func=lambda x: session_labels[x],
        index=session_choices.index(st.session_state.activeStrengthSessionId) if st.session_state.activeStrengthSessionId in session_choices else 0
    )
    st.session_state.activeStrengthSessionId = sel_session_id

    current_meta = next((s for s in STRENGTH_SESSIONS_META if s["id"] == sel_session_id), STRENGTH_SESSIONS_META[0])
    current_fbw_key = current_meta["program"]
    prog = FBW_PROGRAMS[current_fbw_key]

    if sel_session_id not in st.session_state.strengthSessions:
        st.session_state.strengthSessions[sel_session_id] = {
            "sessionId": sel_session_id,
            "program": current_fbw_key,
            "completed": False,
            "exercises": {}
        }
    current_session_data = st.session_state.strengthSessions[sel_session_id]

    col_btn1, col_btn2 = st.columns([2, 2])
    with col_btn1:
        st.markdown(f"**מתעד עבור:** `{current_meta['name']}` | **תוכנית:** `{prog['title']}`")
    with col_btn2:
        if st.button("✅ סמן אימון כוח זה כ'בוצע' בלוח הראשי", type="primary"):
            current_session_data["completed"] = True
            for wk in st.session_state.workouts:
                if wk.get("strengthSessionId") == sel_session_id:
                    wk["status"] = "completed"
            save_app_data()
            st.success("אימון הכוח סומן כבוצע וסונכרן עם לוח 5 השבועות!")
            st.rerun()

    st.write(f"*{prog['subtitle']}*")
    st.divider()

    is_week4 = sel_session_id in ["w4-1", "w4-3"]
    for ex in prog["exercises"]:
        st.markdown(f"#### {ex['name']}")
        st.markdown(f"**שרירי יעד:** {ex['target']} | **ציוד:** `{ex['equipment']}`")
        st.caption(f"מרשם: {ex['prescription']} | דגש: {ex['cues']}")

        num_sets = 2 if is_week4 else ex["defaultSets"]
        if ex["id"] not in current_session_data["exercises"]:
            current_session_data["exercises"][ex["id"]] = [{"weight": "", "reps": "", "done": False} for _ in range(num_sets)]

        ex_sets = current_session_data["exercises"][ex["id"]]
        while len(ex_sets) < num_sets:
            ex_sets.append({"weight": "", "reps": "", "done": False})

        cols = st.columns(num_sets)
        for s_idx in range(num_sets):
            with cols[s_idx]:
                st.markdown(f"**סט {s_idx + 1}**")
                w_val = st.text_input("משקל (ק'ג)", value=ex_sets[s_idx].get("weight", ""), key=f"w_{sel_session_id}_{ex['id']}_{s_idx}")
                r_val = st.text_input("חזרות", value=ex_sets[s_idx].get("reps", ""), key=f"r_{sel_session_id}_{ex['id']}_{s_idx}")
                d_val = st.checkbox("בוצע ✓", value=ex_sets[s_idx].get("done", False), key=f"d_{sel_session_id}_{ex['id']}_{s_idx}")
                ex_sets[s_idx]["weight"] = w_val
                ex_sets[s_idx]["reps"] = r_val
                ex_sets[s_idx]["done"] = d_val

        st.markdown("---")

    if st.button("💾 שמור נתוני אימון זה"):
        save_app_data()
        st.success("הנתונים נשמרו בהצלחה!")

    with st.expander("📊 השוואת עומס והתקדמות שבועית (Progressive Overload Table)"):
        st.write("ריכוז משקלי עבודה וחזרות עבור תוכנית זו על פני השבועות:")
        comp_sessions = ["w1-1", "w2-1", "w3-1", "w4-1"] if current_fbw_key == "fbw1" else ["w1-3", "w2-3", "w3-3", "w4-3"]
        table_rows = []
        for ex in prog["exercises"]:
            row = {"תרגיל": ex["name"]}
            for s_id in comp_sessions:
                s_data = st.session_state.strengthSessions.get(s_id, {})
                s_ex = s_data.get("exercises", {}).get(ex["id"], [])
                logged = [f"{s.get('weight')}kg×{s.get('reps')}" for s in s_ex if s.get("weight") and s.get("reps")]
                row[s_id] = " | ".join(logged) if logged else "-"
            table_rows.append(row)
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

# TAB 3
with tab_track:
    st.subheader("🩺 ניטור גיד יומי - מודל 24 שעות")
    st.caption("הערכה יומית קבועה של כאב ונוקשות בוקר לקביעת סבילות עומס הגיד")

    col_t1, col_t2 = st.columns([1.5, 2])

    with col_t1:
        st.markdown("### 📝 הזנת דיווח יומי")
        with st.form("tendon_form"):
            log_date = st.date_input("תאריך דיווח:", datetime.date.today())
            stiffness = st.slider("משך נוקשות בוקר (דקות):", 0, 60, 5, help="מתחת ל-10 דק' תקין, מעל 20 דק' מצביע על התלקחות")
            morning_pain = st.slider("רמת כאב בוקר בגיד (0–10):", 0.0, 10.0, 2.0, 0.5)
            post_pain = st.slider("רמת כאב לאחר אימון (0–10):", 0.0, 10.0, 2.0, 0.5)
            sharp_pain = st.checkbox("האם מופיע כאב חד בצליעה או בהליכה יומיומית?")
            notes = st.text_input("הערות קליניות:", placeholder="לדוגמה: תחושה קלה שנעלמה במקלחת")
            
            calc_st, calc_desc, _ = calc_tendon_status(morning_pain, stiffness, sharp_pain)
            st.info(f"סטטוס צפוי: **{calc_desc}**")
            
            submitted = st.form_submit_button("שמור דיווח יומי")
            if submitted:
                date_str = str(log_date)
                existing = next((item for item in st.session_state.logs if item["date"] == date_str), None)
                new_entry = {
                    "id": f"log-{int(datetime.datetime.now().timestamp())}",
                    "date": date_str,
                    "stiffness": stiffness,
                    "morningPain": morning_pain,
                    "postPain": post_pain,
                    "sharpPain": sharp_pain,
                    "notes": notes
                }
                if existing:
                    st.session_state.logs[st.session_state.logs.index(existing)] = new_entry
                else:
                    st.session_state.logs.append(new_entry)
                save_app_data()
                st.success("הדיווח נשמר בהצלחה!")
                st.rerun()

    with col_t2:
        st.markdown("### 📈 מגמת מדדים וספי רגישות (Chart)")
        if st.session_state.logs:
            df_logs = pd.DataFrame(st.session_state.logs).sort_values("date")
            fig = go.Figure()
            fig.add_hline(y=3, line_dash="dash", line_color="#10b981", annotation_text="סף בטיחות יעד (≤ 3)", annotation_position="top left")
            fig.add_trace(go.Scatter(x=df_logs["date"], y=df_logs["morningPain"], mode="lines+markers", name="כאב בוקר (0–10)", line=dict(color="#2563eb", width=3)))
            fig.add_trace(go.Scatter(x=df_logs["date"], y=df_logs["stiffness"], mode="lines+markers", name="נוקשות בוקר (דקות)", line=dict(color="#9333ea", width=2, dash="dot")))
            fig.update_layout(title="מעקב כאב ונוקשות בוקר לאורך זמן", height=320, margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### היסטוריית דיווחים")
        if st.session_state.logs:
            st.dataframe(pd.DataFrame(st.session_state.logs)[["date", "morningPain", "stiffness", "postPain", "notes"]], use_container_width=True)

# TAB 4
with tab_runwalk:
    st.subheader("⏱️ מחשבון מקטעי Run/Walk ודגשים ביומכניים")
    
    col_rw1, col_rw2 = st.columns([1.5, 2])
    with col_rw1:
        st.markdown("### פרופיל אינטרוולים מומלץ")
        preset = st.selectbox("בחר פרופיל אימון:", [
            "שבוע 1: 4 דק' ריצה / 1 דק' הליכה (8 חזרות - סה'כ 40 דק')",
            "שבוע 2: 6 דק' ריצה / 1 דק' הליכה (7 חזרות - סה'כ 49 דק')",
            "שבוע 2 קל: 5 דק' ריצה / 1 דק' הליכה (6 חזרות)",
            "שבוע 4 שיא: 10 דק' ריצה / 1 דק' הליכה (4 חזרות)",
            "מותאם אישית"
        ])
        st.info("💡 שילוב הליכה של 1 דקה מאפשר התאוששות ויסקו-אלסטית של הגיד, מקטין את עומס הסטרס המצטבר ומסייע בשמירה על צעדים שקטים.")

    with col_rw2:
        st.markdown("### 👟 דגשי ריצה ביומכניים להגנה על גיד אכילס")
        st.markdown("""
        * **⚡ קדנס מוגבר (170–180 צעדים בדקה):** קיצור אורך הצעד מפחית בכ-15–20% את אימפולס הבלימה (Braking impulse) ואת מומנט הכפיפה הגבית בקרסול.
        * **🎯 נחיתת מרכז כף רגל (Midfoot strike):** הימנע מנחיתה קיצונית על כריות הבהונות (Forefoot), המעמיסה ישירות על הסולאוס וגיד אכילס כקפיץ אלסטי יתר על המידה.
        * **🤫 נחיתה שקטה (Soft Landing):** הקשב לנחיתת הרגל שלך. נחיתה ללא קול חבטה מקטינה את קצב עליית העומס (Loading Rate).
        """)

# TAB 5
with tab_protocols:
    st.subheader("📖 פרוטוקולים קליניים והנחיות לגיד")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("""
        #### 1. פרוטוקול החזקות איזומטריות (Rio & Cook)
        * **מינון:** 4–5 סטים של 45 שניות החזקה סטטית, 2 דקות מנוחה ביניהם.
        * **עצימות:** כ-70% ממאמץ מרבי (MVC).
        * **מטרה:** שיכוך כאב (Analgesia) הנמשך 45–60 דקות ללא עומס אלסטי. מבוצע לפני ריצה ובימי מנוחה.
        
        #### 2. אימון כוח איטי כבד לסולאוס (HSR)
        * **מינון:** 4 סטים של 8–10 חזרות בישיבה (ברך כפופה ב-90°).
        * **קצב:** 3 שניות עלייה (קונצנטרי), 3 שניות ירידה (אקסצנטרי).
        * **משטח ישר בלבד:** ללא ירידה מתחת למדרגה!
        """)
    with col_p2:
        st.markdown("""
        #### 3. כיוונון ספינינג מותאם אכילס
        * **מיקום פדל:** במרכז כף הרגל (Midfoot) כדי לאפס את זרוע המומנט בקרסול ולהוריד עומס מהגיד.
        * **ישיבה בלבד:** איסור על רכיבה בעמידה למניעת עומס דורסיפלקסיה חד.
        
        #### 4. לו"ז יום המירוץ (23.10.2026)
        * **T-35 דקות לזינוק:** ביצוע 4 סטים של החזקה איזומטרית ל-45 שניות.
        * **סיום:** הליכת שחרור קלה. הימנע לחלוטין ממתיחות עקב אגרסיביות.
        """)

    st.divider()
    st.subheader("💾 גיבוי ושחזור נתונים (Data Export / Import)")
    data_str = json.dumps({
        "workouts": st.session_state.workouts,
        "logs": st.session_state.logs,
        "strengthSessions": st.session_state.strengthSessions
    }, ensure_ascii=False, indent=2)
    
    st.download_button("📤 הורד גיבוי נתונים מלא (JSON)", data=data_str, file_name="achilles_training_backup.json", mime="application/json")


if __name__ == "__main__":
    from streamlit.web import cli as stcli
    import sys
    if not st.runtime.exists():
        sys.argv = ["streamlit", "run", __file__]
        sys.exit(stcli.main())
