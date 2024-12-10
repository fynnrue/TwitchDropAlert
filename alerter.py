import time
import requests
import winsound
from bs4 import BeautifulSoup

URL = "https://twitch.facepunch.com/"

box_status = {}

done = {0, 1, 4}

def check_online_status():
    global box_status
    
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    
    boxes = soup.find_all("div", class_="drop-box")
    
    changes_detected = False
    
    for i, box in enumerate(boxes):
        is_live = "is-live" in box.get("class", [])
        
        if i in box_status:
            if box_status[i] != is_live and i not in done:
                print(f"Änderung bei Box {i}: {'Online' if is_live else 'Offline'}")
                box_status[i] = is_live
                if is_live and i not in done:
                    changes_detected = True
        else:
            box_status[i] = is_live

        if is_live and i not in done:
            print(f"Box {i} ist online.")
    
    if changes_detected:
        winsound.MessageBeep()
        time.sleep(0.5)
        winsound.MessageBeep()
        time.sleep(0.5)
        winsound.MessageBeep()
        time.sleep(0.5)

def main():

    print("Monitoring gestartet... Drücken Sie STRG+C zum Beenden.")
    try:
        while True:
            print(time.strftime("%H:%M", time.localtime()))
            check_online_status()
            print()
            time.sleep(300)
    except KeyboardInterrupt:
        print("Überwachung beendet.")

if __name__ == "__main__":
    main()
