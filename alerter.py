import time
import requests
from selenium.webdriver import Edge
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

box_status = {}
done = {0, 1, 4, 8}
priority_list = [8, 9, 2, 5, 7, 6, 10, 11, 3]  # Prio Liste
view_time = {0: 100, 1: 100, 2: 0, 3: 0, 4: 100, 5: 0, 6: 0, 7: 0, 8: 100, 9: 99.8, 10: 0, 11: 0}  # Prozentualer Fortschritt der Drops
current_stream = None
driver = None
stream_start_time = {}
WATCH_INTERVAL = 0.2
DROP_DURATION = 120

def get_priority(index):
    try:
        return priority_list.index(index)
    except ValueError:
        return float('inf')

def percent_to_minutes(percent):
    return (percent / 100) * DROP_DURATION

def minutes_to_percent(minutes):
    return (minutes / DROP_DURATION) * 100

def login_to_twitch():
    global driver

    service = Service("./geckodriver.exe")

    options = webdriver.FirefoxOptions()
    options.set_preference("media.volume_scale", "0.0")

    if not driver:
        driver = Edge(options=options, service=service)

    driver.get("https://www.twitch.tv/login")

    time.sleep(2)

    username_field = driver.find_element(By.ID, "login-username")
    password_field = driver.find_element(By.ID, "password-input")

    with open("login-data.txt", "r") as file:
        lines = file.readlines()
        username = lines[0].strip()
        password = lines[1].strip()

    username_field.send_keys(username)
    password_field.send_keys(password)

    password_field.send_keys(Keys.RETURN)

    time.sleep(5)

    return driver

def open_stream(url, stream_index):
    global driver, stream_start_time

    driver.get(url)

    stream_start_time[stream_index] = time.time()

def check_online_status():
    global box_status, current_stream, view_time

    response = requests.get("https://twitch.facepunch.com/")
    soup = BeautifulSoup(response.text, "html.parser")
    boxes = soup.find_all("div", class_="drop-box")
    best_priority = float('inf')
    best_streamer_url = None
    best_drop_index = None

    for i, box in enumerate(boxes):
        is_live = "is-live" in box.get("class", [])
        box_status[i] = is_live

        if not is_live or i in done or view_time[i] >= 100:
            continue

        streamer_link = box.find("a", class_="streamer-info")["href"]

        drop_priority = get_priority(i)
        if drop_priority < best_priority:
            best_priority = drop_priority
            best_streamer_url = streamer_link
            best_drop_index = i

    if best_streamer_url and (current_stream != best_drop_index or view_time[best_drop_index] < 100):
        if current_stream != best_drop_index:
            print(f"Neuer bevorzugter Stream: {best_streamer_url} (Drop {best_drop_index} - Prio {best_priority} - {view_time[best_drop_index]:.2f}%)")
            open_stream(best_streamer_url, best_drop_index)
            current_stream = best_drop_index
    elif current_stream is not None and view_time[current_stream] >= 100:
        print(f"Drop {current_stream} abgeschlossen. Schließe Stream.")

        current_stream = None

def update_view_time():
    global current_stream, view_time, stream_start_time

    if current_stream is not None:
        current_time = time.time()
        start_time = stream_start_time.get(current_stream, current_time)

        elapsed_minutes = (current_time - start_time) / 60
        if elapsed_minutes >= WATCH_INTERVAL:
            added_percent = minutes_to_percent(WATCH_INTERVAL)
            current_percent = view_time[current_stream]
            new_percent = min(100, current_percent + added_percent)

            view_time[current_stream] = new_percent
            stream_start_time[current_stream] = current_time

            print(f"Drop {current_stream}: {new_percent:.2f}% abgeschlossen.")
            if new_percent >= 100:
                print(f"Drop {current_stream} abgeschlossen!")
                done.add(current_stream)

def main():
    print("Monitoring gestartet... Drücken Sie STRG+C zum Beenden.")
    login_to_twitch()
    try:
        while True:
            print(time.strftime("%H:%M", time.localtime()))
            check_online_status()
            update_view_time()
            print()
            time.sleep(WATCH_INTERVAL * 60)
    except KeyboardInterrupt:
        print("Monitoring beendet.")

if __name__ == "__main__":
    main()
