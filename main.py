import requests
import time
import threading
import os
from flask import Flask

# --- FLASK WEB SERVER ---
app = Flask(__name__)

# --- GLOBAL VARIABLES ---
total_predictions = 0
total_wins = 0
total_losses = 0
history = [] # Ab isme unlimited history save hogi

# API URL
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def fetch_live_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=10)
        data = response.json()
        
        # Note: Agar API structure alag hua toh yahan KeyError aayega
        period_number = data['data'][0]['issueNumber']
        actual_result = data['data'][0]['result'] 
        
        return period_number, int(actual_result), None
    except Exception as e:
        # Agar koi error aaya toh string return karenge taaki page pe dikhe
        return None, None, str(e)

def run_system():
    global total_predictions, total_wins, total_losses, history
    
    sequence = ["Big", "Big", "Big", "Small", "Small", "Small"]
    step_index = 0
    last_period = None # Duplicate entry rokne ke liye
    
    print("✅ Background System Started!")
    
    while True:
        prediction = sequence[step_index % 6]
        period_number, actual_result, error_msg = fetch_live_data()
        
        if error_msg:
            # Agar API theek se kaam nahi kar rahi
            history.insert(0, f"⚠️ API Error: {error_msg}")
        elif period_number and period_number != last_period:
            status = "Wait/Pending"
            
            if actual_result is not None:
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
            
            # History list mein add karein (Ab koi pop() nahi hai, sab save hoga)
            history.insert(0, record)
            last_period = period_number
            step_index += 1 # Agle step pe jao
            
        time.sleep(30) # 30 seconds wait for next period

# --- WEBSITE INTERFACE ---
@app.route('/')
def home():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot Live Stats</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Page ab automatically har 30 seconds mein refresh hoga -->
        <meta http-equiv="refresh" content="30"> 
    </head>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f9;">
        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #333;">📊 Live Bot Statistics</h2>
            <hr>
            <h3><b>Total Predictions:</b> {total_predictions}</h3>
            <h3 style="color: green;"><b>Total Wins:</b> {total_wins}</h3>
            <h3 style="color: red;"><b>Total Losses:</b> {total_losses}</h3>
            <hr>
            <h3 style="color: #333;">🕒 Complete History</h3>
            
            <!-- Scrollbox banaya hai taaki 10k history aane par page kharab na ho -->
            <div style="height: 400px; overflow-y: auto; background: #fafafa; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                <ul style="line-height: 1.8; margin: 0; padding-left: 20px;">
    """
    
    if not history:
        html += "<li>Waiting for first result... Fetching from API.</li>"
    else:
        for item in history:
            if "WIN" in item:
                html += f"<li style='color: green;'><b>{item}</b></li>"
            elif "LOSS" in item:
                html += f"<li style='color: red;'><b>{item}</b></li>"
            elif "Error" in item:
                html += f"<li style='color: orange;'><b>{item}</b></li>"
            else:
                html += f"<li>{item}</li>"

    html += """
                </ul>
            </div>
            <br>
            <p><small><i>🔄 Page is auto-refreshing every 30 seconds.</i></small></p>
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
