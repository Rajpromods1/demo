import requests
import time
import threading
import os
from flask import Flask

# --- FLASK WEB SERVER ---
app = Flask(__name__)

# --- GLOBAL VARIABLES (Stats save karne ke liye) ---
total_predictions = 0
total_wins = 0
total_losses = 0
history = []

# API URL
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def fetch_live_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=10)
        data = response.json()
        
        # Note: 'issueNumber' aur 'result' API ke mutabiq
        period_number = data['data'][0]['issueNumber']
        actual_result = data['data'][0]['result'] 
        
        return period_number, int(actual_result)
    except Exception as e:
        print(f"API Error: {e}")
        return None, None

def run_system():
    global total_predictions, total_wins, total_losses, history
    
    sequence = ["Big", "Big", "Big", "Small", "Small", "Small"]
    step_index = 0
    
    print("✅ Background System Started!")
    
    while True:
        prediction = sequence[step_index % 6]
        period_number, actual_result = fetch_live_data()
        
        if period_number:
            status = "Wait/Pending"
            
            if actual_result is not None:
                # Sirf tabhi count badhaye jab result aa jaye
                total_predictions += 1
                
                # Logic: Big = 5 to 9 | Small = 0 to 4
                if (prediction == "Big" and actual_result >= 5) or (prediction == "Small" and actual_result < 5):
                    status = "🟢 WIN"
                    total_wins += 1
                else:
                    status = "🔴 LOSS"
                    total_losses += 1

            # Log record banaye
            record = f"Period: {period_number} | Pred: {prediction} | Actual: {actual_result} | Status: {status}"
            print(record) # Render Logs ke liye
            
            # Website pe dikhane ke liye History list mein add karein (Sirf last 10 dikhayenge)
            history.insert(0, record)
            if len(history) > 10:
                history.pop()
        
        step_index += 1
        time.sleep(30) # 30 seconds wait for next period

# --- WEBSITE INTERFACE PAR STATS DIKHANE KE LIYE ---
@app.route('/')
def home():
    # Simple HTML Page jo live data dikhayega
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot Live Stats</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f9;">
        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #333;">📊 Live Bot Statistics</h2>
            <hr>
            <h3><b>Total Predictions:</b> {total_predictions}</h3>
            <h3 style="color: green;"><b>Total Wins:</b> {total_wins}</h3>
            <h3 style="color: red;"><b>Total Losses:</b> {total_losses}</h3>
            <hr>
            <h3 style="color: #333;">🕒 Recent History (Last 10)</h3>
            <ul style="line-height: 1.8;">
    """
    
    if not history:
        html += "<li>Waiting for first result... Please refresh after 30 seconds.</li>"
    else:
        for item in history:
            # Color fix for list items
            if "WIN" in item:
                html += f"<li style='color: green;'><b>{item}</b></li>"
            elif "LOSS" in item:
                html += f"<li style='color: red;'><b>{item}</b></li>"
            else:
                html += f"<li>{item}</li>"

    html += """
            </ul>
            <br>
            <p><small><i>🔄 Refresh the page to see the latest data.</i></small></p>
        </div>
    </body>
    </html>
    """
    return html

# --- BACKGROUND THREAD SETUP ---
def start_background_task():
    thread = threading.Thread(target=run_system)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    start_background_task()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
