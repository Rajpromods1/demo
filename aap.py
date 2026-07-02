import requests
import time
import sys

# API URL
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def fetch_live_data():
    """API se live period aur result fetch karne ka function"""
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        
        # Note: 'data' ke andar jo actual keys hain (jaise 'issueNumber', 'result'), 
        # wo API ke JSON structure par depend karegi. Aapko yaha wo keys dalni hongi.
        # Example format:
        period_number = data['data'][0]['issueNumber'] 
        actual_result = data['data'][0]['result'] 
        
        return period_number, actual_result
    except Exception as e:
        print(f"API Error: {e}")
        return None, None

def run_system():
    # Sequence Set kar di: 3 Big, 3 Small
    sequence = ["Big", "Big", "Big", "Small", "Small", "Small"]
    step_index = 0  # Hamesha 0 se start hoga (yani 1st Big se)

    print("✅ System Started! Sequence Reset to First BIG.")
    
    try:
        while True:
            # 1. Prediction nikalna
            prediction = sequence[step_index % 6]
            
            # 2. API se live data lena
            period_number, actual_result = fetch_live_data()
            
            if period_number:
                # 3. Win ya Loss check karna (Dummy logic, adjust according to actual API return)
                status = "Wait/Pending"
                if actual_result:
                    if (prediction == "Big" and actual_result >= 5) or (prediction == "Small" and actual_result < 5):
                        status = "🟢 WIN"
                    else:
                        status = "🔴 LOSS"

                print(f"Period: {period_number} | Prediction: {prediction} | Actual: {actual_result} | Status: {status}")
            
            # Agle step par move karna
            step_index += 1
            
            # 30 seconds wait karna agle period ke liye
            time.sleep(30)
            
    except KeyboardInterrupt:
        # Jab user manual stop kare
        print("\n🛑 System Manually Stopped by User.")
        sys.exit()

if __name__ == "__main__":
    run_system()
