#!/usr/bin/env python3
import os
import sys
from collections import deque
import datetime
import asyncio
import aiohttp

#disables SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Runtime configuration
ROUTER_URL = os.getenv("ROUTER_URL", "https://192.168.50.1").rstrip("/") #Base URL of the router's web interface (default "https://192.168.50.1")
USERNAME = os.getenv("USERNAME", "admin") # Router's admin username (default "admin")
PASSWORD = os.getenv("PASSWORD", "") # Router's admin password (required)
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "8")) #Maximum time (seconds) to wait for router API responses
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "10")) #Seconds between GPS checks (default 10)
STOP_THRESHOLD = float(os.getenv("STOP_THRESHOLD", "1.0")) #Speed below this enables WiFi (default 1.0)
MOVE_THRESHOLD = float(os.getenv("MOVE_THRESHOLD", "1.0")) #Speed at/above this disables WiFi (default 1.0)
STOP_SAMPLES = int(os.getenv("STOP_SAMPLES", "5")) #How many stationary readings before enabling (default 5)
MOVE_SAMPLES = int(os.getenv("MOVE_SAMPLES", "3")) #How many movement readings before disabling (default 3)

#API paths
PATH_LOGIN = "/api/login"
PATH_LOCATION = "/api/info.location"
PATH_AP = "/api/cmd.ap"

class PeplinkApi:
    def __init__(self, base, session):
        self.base = base
        self.session = session

    def validate(self, payload, where):
        if payload.get("stat") != "ok":
            print(f"{where} failed:", payload)
            raise SystemExit(1)
        return payload.get("response", payload)

    async def post(self, api_endpoint, data):
        url = f"{self.base}{api_endpoint}"
        async with self.session.post(url, json=data, timeout=HTTP_TIMEOUT, ssl=False) as response:
            response.raise_for_status()
            return await response.json()

    async def get(self, api_endpoint):
        url = f"{self.base}{api_endpoint}"
        async with self.session.get(url, timeout=HTTP_TIMEOUT, ssl=False) as response:
            response.raise_for_status()
            return await response.json()

    async def login(self, username, password):
        payload = await self.post(PATH_LOGIN, {"username": username, "password": password})
        return self.validate(payload, "login")

#Get device speed from the response, return None if not available or invalid
def get_speed(info):
    try:
        return float(info["location"]["speed"])
    except (KeyError, TypeError, ValueError):
        return None

#Get current timestamp as YYYY-MM-DD HH:MM:SS
def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def main():
    if not PASSWORD:
        print("PASSWORD is required", file=sys.stderr)
        raise SystemExit(1)

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        api = PeplinkApi(ROUTER_URL, session)

        await api.login(USERNAME, PASSWORD)
        print("login ok")

        async def toggle_ap(enabled: bool):
            payload = await api.post(PATH_AP, {"enable": bool(enabled)})
            api.validate(payload, "cmd.ap")

        last_ap_state = None
        stop_window = deque(maxlen=STOP_SAMPLES)
        move_window = deque(maxlen=MOVE_SAMPLES)

        while True:
            info = api.validate(await api.get(PATH_LOCATION), "info.location")
            speed = get_speed(info)

            if speed is not None:
                print(f"{now()} Speed: {speed}", flush=True)
                stop_window.append(speed)
                move_window.append(speed)

            should_enable = len(stop_window) == STOP_SAMPLES and all(s < STOP_THRESHOLD for s in stop_window)
            should_disable = len(move_window) == MOVE_SAMPLES and all(s >= MOVE_THRESHOLD for s in move_window)

            if should_disable and (last_ap_state is None or last_ap_state is True):
                await toggle_ap(False)
                last_ap_state = False
                print(f"{now()} AP disabled", flush=True)
            elif should_enable and (last_ap_state is None or last_ap_state is False):
                await toggle_ap(True)
                last_ap_state = True
                print(f"{now()} AP enabled", flush=True)

            await asyncio.sleep(POLL_INTERVAL)

asyncio.run(main())