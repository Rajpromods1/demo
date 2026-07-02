import requests
import time
import threading
import os
from flask import Flask

# --- FLASK WEB SERVER (Render ko on rakhne ke liye) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running 24/7 on Render!"

# --- AAPKA MAIN SYSTEM LOGIC ---
# API URL
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def fetch_live_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=10)
        data = response.json()
        
        # Note: 'issueNumber' aur 'result' ki exact key API ke hisaab se adjust karein
        period_number = data['data'][0]['issueNumber']
        actual_result = data['data'][0]['result'] 
        
        return period_number, int(actual_result)
    except Exception as e:
        print(f"API Error: {e}")
        return None, None

def run_system():
    sequence = ["Big", "Big", "Big", "Small", "Small", "Small"]
    step_index = 0
    
    print("✅ Background System Started! Sequence Reset to First BIG.")
    
    while True:
        prediction = sequence[step_index % 6]
        period_number, actual_result = fetch_live_data()
        
        if period_number:
            status = "Wait/Pending"
            
            if actual_result is not None:
                # Logic: Big = 5 to 9 | Small = 0 to 4
                if (prediction == "Big" and actual_result >= 5) or (prediction == "Small" and actual_result < 5):
                    status = "🟢 WIN"
                else:
                    status = "🔴 LOSS"

            print(f"Period: {period_number} | Prediction: {prediction} | Actual: {actual_result} | Status: {status}")
        
        step_index += 1
        time.sleep(30) # 30 seconds wait for next period

# --- BACKGROUND THREAD SETUP ---
def start_background_task():
    thread = threading.Thread(target=run_system)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    # 1. Background mein betting sequence start karna
    start_background_task()
    
    # 2. Flask web server start karna (PORT bind karna zaroori hai Render ke liye)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
