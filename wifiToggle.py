#!/usr/bin/env python3
import os
import sys
import time
import requests
from collections import deque
from datetime import datetime

#disables SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Runtime configuration
ROUTER_URL = os.getenv("ROUTER_URL", "https://192.168.50.1").rstrip("/")
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "8")) 
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "10")) 
STOP_THRESHOLD = float(os.getenv("STOP_THRESHOLD", "1.0"))
MOVE_THRESHOLD = float(os.getenv("MOVE_THRESHOLD", "1.0"))
STOP_SAMPLES = int(os.getenv("STOP_SAMPLES", "5"))
MOVE_SAMPLES = int(os.getenv("MOVE_SAMPLES", "3"))

#API paths
PATH_LOGIN = "/api/login"
PATH_LOCATION = "/api/info.location"
PATH_AP = "/api/cmd.ap"

class PeplinkApi:
    def __init__(self, base):
        self.base = base
        self.session = requests.Session()
        self.session.verify = False
    
    def post(self, api_endpoint, data):
        url = f"{self.base}{api_endpoint}"
        response = self.session.post(url,json=data,timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def fetch(self, api_endpoint):
        url = f"{self.base}{api_endpoint}"
        response = self.session.get(url, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()

#Check is the api response is ok, if not print the payload and exit
def validate_api_response(payload, where):
    if payload.get("stat") != "ok":
        print(f"{where} failed:", payload)
        raise SystemExit(1)
    return payload.get("response", payload)

#Get device speed from the response, return None if not available or invalid
def get_speed(info):
    try:
        return float(info["location"]["speed"])
    except (KeyError, TypeError, ValueError):
        return None
    
def main():
    api = PeplinkApi(ROUTER_URL)

    if not PASSWORD:
        print("PASSWORD is required", file=sys.stderr)
        raise SystemExit(1)

    #Login
    login = api.post(PATH_LOGIN, {"username": USERNAME, "password": PASSWORD})
    validate_api_response(login, "login")
    print("login ok")

    #AP control
    def toggle_ap(enabled: bool):
        payload = api.post(PATH_AP, {"enable": bool(enabled)})
        validate_api_response(payload, "cmd.ap")

    last_ap_state = None
    stop_window = deque(maxlen=STOP_SAMPLES)
    move_window = deque(maxlen=MOVE_SAMPLES)

    #Main logic
    while True:
        info = validate_api_response(api.fetch(PATH_LOCATION), "info.location")
        speed = get_speed(info)

        if speed is not None:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Speed: {speed}", flush=True)
            stop_window.append(speed)
            move_window.append(speed)

        should_enable  = len(stop_window) == STOP_SAMPLES and all(speed < STOP_THRESHOLD for speed in stop_window)
        should_disable = len(move_window) == MOVE_SAMPLES and all(speed >= MOVE_THRESHOLD for speed in move_window)

        action = None
        if should_disable and (last_ap_state is None or last_ap_state is True):
            toggle_ap(False)
            last_ap_state = False
            action = "ap_disable"
        elif should_enable and (last_ap_state is None or last_ap_state is False):
            toggle_ap(True)
            last_ap_state = True
            action = "ap_enable"

        if action:
            state = "enabled" if last_ap_state else "disabled"
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} AP {state}", flush=True)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
