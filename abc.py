import os
from google import genai

# 1. Connect to the brain using your key
# Ensure your actual API key is placed inside the quotes below!
client = genai.Client(api_key='AIzaSyASyUtSBrBrIa3WHJAp9o1Eo3CbObTf1iU')

print("FRIDAY: All systems online and integrated, boss. Standing by.")

# 2. Start the infinite loop to keep her awake
while True:
    try:
        # Get your input
        user_message = input("\nYou: ")
        
        # Check if you want to close the connection
        if user_message.lower() in ['exit', 'quit', 'go to sleep', 'stand down']:
            print("\nFRIDAY: Copy that, boss. Systems powering down. Syncing logs to GitHub.")
            break
            
        # If not exiting, send the message to the AI
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
        )
        
        # Print her answer
        print(f"\nFRIDAY: {response.text}")
        
    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C without an ugly error crash
        print("\n\nFRIDAY: Session interrupted manually. Standing down.")
        break