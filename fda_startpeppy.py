#!/usr/bin/env python
import os
import subprocess
from subprocess import Popen
import time
from datetime import datetime
import requests
import json
# --- Configuration ---
LMS_IP = "localhost"  # Replace with your Logitech Media Server IP address
LMS_WEB_PORT = 9000      # Replace with your LMS web port (usually 9000 or 80)
# This is the MAC address of your Squeezelite player
# You found this as '2c:cf:67:64:0e:b5' in your curl output
SQUEEZELITE_PLAYER_ID = "2c:cf:67:64:0e:b5"

prevstat = "OFF"
proc=None
def get_squeezelite_info():
    """
    Connects to Logitech Media Server (LMS) JSON-RPC API to get
    Squeezelite player information (Title, Album, Artist, Play Status).
    """
    url = f"http://{LMS_IP}:{LMS_WEB_PORT}/jsonrpc.js"
    
    # We'll request status with specific tags to try and get more info
    # 'l' for playlist info, 'a' for artist, 't' for title, 'm' for album
    # Note: LMS might not always return all tags if the info isn't available (e.g., when stopped)
    payload = {
        "method": "slim.request",
        "params": [SQUEEZELITE_PLAYER_ID, ["status", "-", 1, "tags:latm"]]
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Extracting data from the 'result' dictionary
        result = data.get('result', {})

        # Player Play Status
        play_status = result.get('mode', 'unknown') # 'play', 'pause', 'stop'

        # Current Track Information
        # Using .get() with a default value to avoid KeyError if a field is missing
        title = result.get('current_title', 'N/A')
        album = result.get('album', 'N/A')
        artist = result.get('artist', 'N/A') # May be 'N/A' if not returned by status command directly

        # Fallback to remoteMeta if direct fields are not found (often present even when stopped)
        remote_meta = result.get('remoteMeta', {})
        if title == 'N/A' and remote_meta:
            title = remote_meta.get('title', 'N/A')
        if album == 'N/A' and remote_meta:
            album = remote_meta.get('album', 'N/A')
        # Artist is less reliably in remoteMeta from 'status' command, but good to check
        if artist == 'N/A' and remote_meta:
            artist = remote_meta.get('artist', 'N/A')
        return {
            "title": title,
            "album": album,
            "artist": artist,
            "play_status": play_status
        }

    except requests.exceptions.Timeout:
        print(f"Error: Request to LMS timed out after 5 seconds.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to LMS at {LMS_IP}:{LMS_WEB_PORT}. Is it running?")
        print(f"Details: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP request to LMS failed with status {e.response.status_code}.")
        print(f"Details: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON response from LMS. Is the port correct?")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def graph_monitor():

    global prevstat
    global proc
    progname = "/home/dietpi/PeppyMeter/peppymeter.py"
    #progname = "DISPLAY=:0 python3 /home/dietpi/PeppyMeter/peppymeter.py"
    #progname = "python3 /home/dietpi/PeppyMeter/peppymeter.py"
    #song = moodeCurrentSong()
    #print(song['state'])
    #print(prevstat)
    player_info = get_squeezelite_info()
    

    if player_info is not None:
     print(player_info['play_status'])	
     if player_info['play_status'] == "play":
       if prevstat == "OFF":
          prevstat = "ON"
          time.sleep(30)
          print(prevstat, " - ", progname )
          #subprocess.run(["sudo", "python3", progname])
          #subprocess.run(["sudo","export" , "DISPLAY=:0"])
          #subprocess.Popen(["sudo", "python3", progname])
          proc= subprocess.Popen(["python3", progname])
          #proc = subprocess.Popen([progname], shell=True) 
       if proc is not None and proc.poll() is not None:
          print("Zombie") 
          proc.wait()
          proc = None
          player_info = get_squeezelite_info()
          if player_info['play_status'] == 'play':
             time.sleep(60)
             proc= subprocess.Popen(["python3", progname])
     elif  (player_info['play_status'] == "pause" or player_info['play_status'] == "stop") and prevstat == "ON":
        #print("must pause")
        prevstat = "OFF"
        subprocess.run(["sudo", "pkill","-f","peppymeter.py"])
       
     else:
        prevstat = "OFF"
#       print(prevstat)
#    print(prevstat)

def main():
    global x
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print ("Inizio programma - ", dt_string)
    while True:
        graph_monitor()
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
