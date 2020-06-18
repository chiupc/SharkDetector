import requests
import json

def send_volume_alert(message):
    url = "https://a4aug8grul.execute-api.ap-southeast-1.amazonaws.com/default/volume-alert"
    
    payload = {"messageText":message}
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    return response