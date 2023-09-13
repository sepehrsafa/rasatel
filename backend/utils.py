import requests


def send_goip_sms(url, username, password, line, message, phone_number):
    url = f"{url}/goip/sendsms/"

    data = {
        "auth": {"username": username, "password": password},
        "goip_line": line,
        "number": phone_number,
        "content": message,
    }

    try:
        return True
        response = requests.post(url, json=data)
        print(response.json())
        return response.json()
    except Exception as e:
        # logging.error(f"Failed to send SMS. Error: {e}")
        print(e)
        return {"result": "FAILURE", "reason": str(e)}
