import os
import requests
from google import genai
from google.genai import types

# 🔴 CHANGE THIS to your actual n8n Test Webhook URL you copied!
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/friday-alert"

# 1. Define the actual function Python will run when FRIDAY requests it
def trigger_system_alert(alert_message: str) -> str:
    """Triggers an n8n automation workflow to handle a system alert."""
    payload = {"message": alert_message, "status": "active"}
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            return f"Success: n8n workflow triggered with message: '{alert_message}'"
        else:
            return f"Failed to trigger n8n. Status code: {response.status_code}"
    except Exception as e:
        return f"Error connecting to n8n: {str(e)}"

# 2. Map the tool so the Gemini client understands it
my_tools = [trigger_system_alert]

# 3. Connect to the brain
client = genai.Client(api_key='your-actual-api-key-here')

print("FRIDAY: Systems online. Automation bridges established. Ready, boss.")

while True:
    try:
        user_message = input("\nYou: ")
        
        if user_message.lower() in ['exit', 'quit', 'go to sleep']:
            print("\nFRIDAY: Standing down.")
            break
            
        # We pass the 'tools' list to the configuration here
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                tools=my_tools,
                temperature=0.5
            )
        )
        
        print(f"\nFRIDAY: {response.text}")
        
    except KeyboardInterrupt:
        print("\n\nFRIDAY: Session interrupted.")
        breakpython abc.py