"""
Garmin Connect Sync Module for Achilles Tendinopathy Load Management
Fetches latest activity (Running / Cycling / Strength) from Garmin Connect,
extracts distance, duration, HR zones, and critical running cadence (SPM).
"""

import os
import json
import datetime
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError
)

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "garmin_credentials.json")
LATEST_ACTIVITY_FILE = os.path.join(os.path.dirname(__file__), "garmin_latest.json")

def load_saved_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_credentials(email, password):
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump({"email": email, "password": password}, f, ensure_ascii=False, indent=2)

def fetch_latest_activity(email=None, password=None):
    """
    Connects to Garmin Connect and fetches the single latest activity.
    Returns parsed activity dictionary with Achilles rehab metrics.
    """
    if not email or not password:
        creds = load_saved_credentials()
        if creds:
            email = creds.get("email")
            password = creds.get("password")
        else:
            return {"success": False, "error": "נדרש מייל וסיסמה לחשבון Garmin Connect."}

    try:
        client = Garmin(email, password)
        client.login()
        
        # Save credentials locally once validated
        save_credentials(email, password)
        
        # Fetch latest 3 activities to find the most relevant one
        activities = client.get_activities(0, 3)
        if not activities:
            return {"success": False, "error": "לא נמצאו פעילויות אחרונות בחשבון Garmin."}

        act = activities[0]
        
        # Extract fields
        activity_type = act.get("activityType", {}).get("typeKey", "running").lower()
        start_time_str = act.get("startTimeLocal", "")
        duration_sec = act.get("duration", 0)
        distance_meters = act.get("distance", 0)
        avg_hr = act.get("averageHR", 0)
        max_hr = act.get("maxHR", 0)
        avg_speed_mps = act.get("averageSpeed", 0)
        
        # Cadence: Garmin often returns steps per minute (or double steps for running)
        # In Garmin API, averageRunningCadenceInStepsPerMinute is usually provided
        avg_cadence = act.get("averageRunningCadenceInStepsPerMinute")
        if not avg_cadence:
            # Fallback for cycling or other cadence fields
            avg_cadence = act.get("averageBikeCadenceInRevPerMinute") or act.get("averageCadence", 0)

        dist_km = round(distance_meters / 1000.0, 2) if distance_meters else 0.0
        minutes = int(duration_sec // 60)
        seconds = int(duration_sec % 60)
        duration_formatted = f"{minutes}:{seconds:02d}"
        
        pace_formatted = "0:00"
        if dist_km > 0 and duration_sec > 0:
            sec_per_km = duration_sec / dist_km
            pace_min = int(sec_per_km // 60)
            pace_sec = int(sec_per_km % 60)
            pace_formatted = f"{pace_min}:{pace_sec:02d} דק'/ק\"מ"

        # Cadence Clinical Assessment (170-180 SPM target for Achilles tendon protection)
        cadence_status = "unknown"
        cadence_feedback = ""
        if avg_cadence:
            avg_cadence = int(round(avg_cadence))
            if avg_cadence >= 170 and avg_cadence <= 185:
                cadence_status = "optimal"
                cadence_feedback = f"מצוין! קדנס ממוצע {avg_cadence} צעדים/דקה נמצא בטווח האופטימלי (170–180) להפחתת עומס בלימה מאכילס."
            elif avg_cadence < 170:
                cadence_status = "low"
                cadence_feedback = f"קדנס ממוצע {avg_cadence} צעדים/דקה. מומלץ לקצר מעט את אורך הצעד ולהגביר קצב ל-175 SPM להורדת מומנט כפיפה בקרסול."
            else:
                cadence_status = "high"
                cadence_feedback = f"קדנס ממוצע {avg_cadence} צעדים/דקה. קצב צעדים מהיר מאוד."

        parsed = {
            "success": True,
            "activityId": act.get("activityId"),
            "activityName": act.get("activityName", "אימון Garmin"),
            "activityType": activity_type,
            "isRun": "run" in activity_type,
            "isCycling": "cycl" in activity_type or "bike" in activity_type,
            "startTime": start_time_str,
            "date": start_time_str.split(" ")[0] if start_time_str else str(datetime.date.today()),
            "distanceKm": dist_km,
            "durationFormatted": duration_formatted,
            "durationSeconds": int(duration_sec),
            "pace": pace_formatted,
            "avgHr": int(avg_hr) if avg_hr else None,
            "maxHr": int(max_hr) if max_hr else None,
            "avgCadence": avg_cadence,
            "cadenceStatus": cadence_status,
            "cadenceFeedback": cadence_feedback,
            "calories": act.get("calories", 0)
        }

        # Cache locally
        with open(LATEST_ACTIVITY_FILE, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)

        return parsed

    except GarminConnectAuthenticationError:
        return {"success": False, "error": "שגיאת אימות: שם משתמש או סיסמה שגויים ב-Garmin Connect."}
    except GarminConnectTooManyRequestsError:
        return {"success": False, "error": "יותר מדי בקשות ל-Garmin Connect. אנא המתן מספר דקות."}
    except GarminConnectConnectionError:
        return {"success": False, "error": "שגיאת חיבור לשרתי Garmin. ודא חיבור אינטרנט פעיל."}
    except Exception as e:
        return {"success": False, "error": f"שגיאה בעת סנכרון עם גרמין: {str(e)}"}

if __name__ == "__main__":
    import sys
    print("Testing garmin_sync module...")
    creds = load_saved_credentials()
    if creds:
        print(f"Found saved credentials for {creds.get('email')}. Attempting fetch...")
        res = fetch_latest_activity()
        print("Result:", res)
    else:
        print("No saved credentials yet. Ready for interactive login.")
