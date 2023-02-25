from bs4 import BeautifulSoup
import requests 

from PIL import Image
from clint.textui import progress
from time import sleep
import random
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
import requests
# make chrome log requests
import json
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import wget
import sys
from selenium.webdriver.chrome.service import Service
import os 
import string
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import asyncio
import aiohttp  # pip install aiohttp
import aiofiles  # pip install aiofiles


def get_link(url):
    capabilities = DesiredCapabilities.CHROME
    # capabilities["loggingPrefs"] = {"performance": "ALL"}  # chromedriver < ~75
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+
    ser = Service(r"C:\\Users\\alik2\\Desktop\\kino_bot\\scrapper\\chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=C:\\Users\\alik2\\Desktop\\kino_bot\\sel_profile")
#    options.add_argument('--no-sandbox') 
#    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ser, options=options, 
        desired_capabilities=capabilities,
    )
    driver.get(url)

    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    headers={'User-Agent': user_agent}

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.content, "html.parser")

    years = soup.find_all("td", class_="l")

    movie_name = soup.find("div", class_="b-post__title").text 
    description = soup.find("div", class_="b-post__description_text").text 
    movie_poster = soup.find("div", class_="b-sidecover").find("a").get("href")

    for i in years:
        i = i.parent.text
        if i.replace(" ", '').split(":")[0] == 'Рейтинги':
            if 'Кинопоиск' in i.replace(" ", '').split(":")[2]:
                imdb_rate = i.replace(" ", '').split(":")[2].split("Кинопоиск")[0]
                kinopoisk_rate = i.replace(" ", '').split(":")[3]
            else:
                imdb_rate = i.replace(" ", '').split(":")[2]
                kinopoisk_rate = 'None'
        elif i.replace(" ", '').split(":")[0] == 'Датавыхода':
            year = i.split(":")[1]
            print(year)

        elif i.replace(" ", '').split(":")[0] == 'Страна':
            country = i.split(":")[1]
        elif i.replace(" ", '').split(":")[0] == 'Жанр':
            genre = i.replace(" ", '').split(":")[1]
    s = driver.find_element(By.XPATH, '//*[@id="cdnplayer"]')
    s.click()
    sleep(2)
    logs_raw = driver.get_log("performance")
    for i in logs_raw:
        try:
            if json.loads(i['message'])['message']['params']['response']['url']:
                if 'mp4:hls' in json.loads(i['message'])['message']['params']['response']['url']:
                    driver.close()
                    print(json.loads(i['message'])['message']['params']['response']['url'].split(":hls")[0])
                    ALL = [json.loads(i['message'])['message']['params']['response']['url'].split(":hls")[0], year, movie_name, country, genre, description, imdb_rate, kinopoisk_rate, movie_poster]
                    print(ALL)
                    return ALL
        except:
            pass



def bar_progress(current, total, width=80):
    progress_message = "Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total)
  # Don't use print() as it will print in new line every time.
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()

#Now use this like below,

 

def get_movie(url):
    url = get_link(url)
    save_path = f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}.mp4"
    save_path_2 = f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}.png"
    print(url)
    print(save_path)
    wget.download(url[0], save_path, bar=bar_progress)
    wget.download(url[8], save_path_2)
    url.append(os.path.abspath(save_path))
    url.append(os.path.abspath(save_path_2))
    return url



def get_anime(url): 
    software_names = [SoftwareName.CHROME.value]
    returner = []
    series = []
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=10)
    user_agent = user_agent_rotator.get_random_user_agent()
    headers={'User-Agent': user_agent}
    r = requests.get(url, headers=headers)
    print(r)
    soup = BeautifulSoup(r.content, "html.parser")
    save_path_2 = f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}.jpg"
    r = requests.get(soup.find("div", class_="all_anime_title").get('style').split("'")[1], headers=headers)
    print(r)
    with open(save_path_2, "wb") as f:
        f.write(r.content)
    #wget.download(soup.find("div", class_="all_anime_title").get('style').split("'")[1], save_path_2)
    returner.append(os.path.abspath(save_path_2))
    for i in soup.find("div", class_="under_video_additional the_hildi").text.split("."):
        if i.split(":")[0] == "\r\n\r\nЖанры":
            genre = i.split(":")[1]
            returner.append(genre)
        elif i.split(":")[0] == "Год выпуска":
            year = i.split(":")[1].split("Аниме")[1]
            returner.append(year)

    description = soup.find("p", class_="under_video uv_rounded_bottom the_hildi").text
    returner.append(description)
    anime_name = None
    for i in soup.find_all("a", class_="short-btn"):
        r = requests.get(f'https://jut.su{i.get("href")}', headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        if anime_name == None:
            anime_name = soup.find("span", itemprop="name").text.replace("1 серия", "").replace('Смотреть', '')
            returner.append(anime_name)
        link = soup.find("video", class_="video-js vjs-default-skin vjs-16-9").find("source", label="720p").get("src")
        save_path = f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}.mp4"
        r = requests.get(link, headers=headers, stream=True)
        with open(save_path, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
                if chunk:
                    f.write(chunk)
                    f.flush()
        series.append(os.path.abspath(save_path))
    return returner, series



'''def get_serial(name):
    capabilities = DesiredCapabilities.CHROME
    # capabilities["loggingPrefs"] = {"performance": "ALL"}  # chromedriver < ~75
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+
    ser = Service(r"C:\\Users\\alik2\\Desktop\\kino_bot\\scrapper\\chromedriver.exe")
    options = webdriver.ChromeOptions()
#    options.add_argument('--no-sandbox') 
#    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ser, options=options, 
        desired_capabilities=capabilities,
    )
    driver.get("https://rezka.ag/")
    s = driver.find_element(By.CLASS_NAME, 'b-search__field')
    s.send_keys(name)
    sleep(2)
    ss = driver.find_element(By.CLASS_NAME, "b-search__section_list")
    print(ss.get_attribute('innerHTML'))
    items = ss.find_elements(By.TAG_NAME, "a")
    print(items)
    for i in items:
        get_movie(i.get_attribute("href"))
get_serial("Ночная смена")'''

def get_serial(url):
    capabilities = DesiredCapabilities.CHROME
    # capabilities["loggingPrefs"] = {"performance": "ALL"}  # chromedriver < ~75
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+
    ser = Service(r"C:\\Users\\alik2\\Desktop\\kino_bot\\scrapper\\chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=C:\\Users\\alik2\\Desktop\\kino_bot\\sel_profile")
#    options.add_argument('--no-sandbox') 
#    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ser, options=options, 
        desired_capabilities=capabilities,
    )
    driver.get(url)
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    headers={'User-Agent': user_agent}

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.content, "html.parser")

    years = soup.find_all("td", class_="l")

    movie_name = soup.find("div", class_="b-post__title").text 
    description = soup.find("div", class_="b-post__description_text").text 
    movie_poster = soup.find("div", class_="b-sidecover").find("a").get("href")
    r = requests.get(movie_poster, headers=headers)
    save_path_2 = f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}.png"
    with open(save_path_2, "wb") as f:
        f.write(r.content)
    for i in years:
        i = i.parent.text
        if i.replace(" ", '').split(":")[0] == 'Рейтинги':
            if 'Кинопоиск' in i.replace(" ", '').split(":")[2]:
                imdb_rate = i.replace(" ", '').split(":")[2].split("Кинопоиск")[0]
                kinopoisk_rate = i.replace(" ", '').split(":")[3]
            else:
                imdb_rate = i.replace(" ", '').split(":")[2]
                kinopoisk_rate = 'None'
        elif i.replace(" ", '').split(":")[0] == 'Датавыхода':
            year = i.split(":")[1]
            print(year)

        elif i.replace(" ", '').split(":")[0] == 'Страна':
            country = i.split(":")[1]
        elif i.replace(" ", '').split(":")[0] == 'Жанр':
            genre = i.replace(" ", '').split(":")[1]
    episode = driver.find_elements(By.CLASS_NAME, "b-simple_episode__item")
    urls = []
    for i in episode:
        i.click()
        s = i.find_element(By.XPATH, '//*[@id="cdnplayer"]')
        s.click()
        sleep(2)
        logs_raw = driver.get_log("performance")
        urls.append(get_log(logs_raw))
    driver.close()
    ALL = [download_files_from_report(urls), year, movie_name, country, genre, description, imdb_rate, kinopoisk_rate, os.path.abspath(save_path_2)]
    return ALL 

def get_log(logs_raw):
    for i in logs_raw:
        try:
            if json.loads(i['message'])['message']['params']['response']['url']:
                if 'mp4:hls' in json.loads(i['message'])['message']['params']['response']['url']:
                    return json.loads(i['message'])['message']['params']['response']['url'].split(":hls")[0]
        except:
            pass


REPORTS_FOLDER = "reports"

def download_files_from_report(urls):
    sema = asyncio.BoundedSemaphore(5)
    path = {}
    async def fetch_file(url):
        fname = url.split("/")[-1]
        async with sema, aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                assert resp.status == 200
                data = await resp.read()

        async with aiofiles.open(
            os.path.join(fname), "wb"
        ) as outfile:
            await outfile.write(data)
        if path:
            path[list(path.keys())[-1]+1] = os.path.abspath(fname)
        else:
            path[1] = os.path.abspath(fname)
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(fetch_file(url)) for url in urls]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    return path


