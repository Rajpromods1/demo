import time
import threading
import os
import cloudscraper
from flask import Flask

# --- FLASK WEB SERVER ---
app = Flask(__name__)

# --- GLOBAL VARIABLES ---
total_predictions = 0
total_wins = 0
total_losses = 0
history = []

# API URL
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def fetch_live_data():
    try:
        # Normal requests ki jagah CloudScraper ka use kar rahe hain
        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        })
        
        response = scraper.get(API_URL, timeout=15)
        
        if response.status_code != 200:
            return None, None, f"Blocked by Site! HTTP Status: {response.status_code}"
            
        try:
            data = response.json()
        except ValueError:
            return None, None, "Site is sending HTML/Captcha instead of JSON."
        
        # Exact keys for your API
        period_number = data['data'][0]['issueNumber']
        actual_result = data['data'][0]['result'] 
        
        return period_number, int(actual_result), None
        
    except KeyError as e:
        return None, None, f"Data format mismatch. Missing Key: {e}"
    except Exception as e:
        return None, None, str(e)

def run_system():
    global total_predictions, total_wins, total_losses, history
    
    sequence = ["Big", "Big", "Big", "Small", "Small", "Small"]
    step_index = 0
    last_period = None
    
    print("✅ Background System Started!")
    
    while True:
        prediction = sequence[step_index % 6]
        period_number, actual_result, error_msg = fetch_live_data()
        
        if error_msg:
            history.insert(0, f"⚠️ Error: {error_msg}")
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

            record = f"Period: {period_number} | Pred: {prediction} | Actual: {actual_result} | Status: {status}"
            history.insert(0, record)
            last_period = period_number
            step_index += 1 
            
        time.sleep(30) 

# --- WEBSITE INTERFACE ---
@app.route('/')
def home():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot Live Stats</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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

def start_background_task():
    thread = threading.Thread(target=run_system)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    start_background_task()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
