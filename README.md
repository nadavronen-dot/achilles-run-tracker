# 🏃 מערכת ניהול עומסים ותוכנית אימונים 8 ק"מ (מירוץ בוז'ולה 2026)
### מותאמת אישית לטנדינופתיה של גיד אכילס (Reactive-on-Chronic Achilles Tendinopathy)

מערכת אינטראקטיבית לניהול עומסים, מעקב כאב יומי לפי מודל 24 השעות, תוכנית ריצה-ספינינג ל-5 שבועות ואימוני כוח FBW 1 ו-FBW 2 עם תיעוד משקלים וחזרות.

---

## 🚀 הפעלה מהירה מקומית (Local Run on Mac)

1. פתח את הטרמינל בתיקיית הפרויקט:
   ```bash
   cd "/Users/nadavronen/Documents/אישי/אימונים וספורט/achilles-run-tracker"
   ```

2. התקן את הספריות הנדרשות:
   ```bash
   pip install -r requirements.txt
   ```

3. הפעל את אפליקציית הסטרימליט:
   ```bash
   streamlit run app.py
   ```
   הדפדפן ייפתח אוטומטית בכתובת `http://localhost:8501`.

---

## 🌐 פריסה אונליין חינם (Streamlit Community Cloud + GitHub)
כדי שהאפליקציה תהיה זמינה לך בנייד (iPhone/Android) מכל מקום 24/7:

1. צור מאגר חדש (New Repository) ב-GitHub בשם: `achilles-run-tracker`.
2. חבר את המאגר המקומי ודחוף את הקוד (Push):
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/achilles-run-tracker.git
   git push -u origin main
   ```
3. היכנס אל [share.streamlit.io](https://share.streamlit.io) (התחבר עם חשבון ה-GitHub שלך).
4. לחץ על **New app**, בחר את המאגר `achilles-run-tracker`, ענף `main`, קובץ ראשי `app.py`, ולחץ **Deploy!**.
5. בתוך פחות מדקה תקבל קישור אונליין קבוע (למשל: `https://achilles-run-tracker.streamlit.app`) שתוכל לשמור במסך הבית בטלפון כאפליקציה לכל דבר!

---

## 📱 שימוש אופליין מלא (ללא אינטרנט כלל)
בתיקיית `מעקבים אישיים` קיים בנוסף קובץ HTML עצמאי:
`achilles_training_app.html`
הקובץ פועל באופן מלא גם ללא רשת, ללא שרת וללא תלויות חיצוניות.
