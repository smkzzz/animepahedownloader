from pushbullet import Pushbullet
from bs4 import BeautifulSoup
import pickle
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os.path
import requests
import os
from AnilistPython import Anilist
from rich.console import Console
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

anilist = Anilist()
options = Options()
options.headless = True
print("Initializing...")
driver = webdriver.Firefox(options=options)

api = 'o.lWFjbq7Kk20gVHVh9B5P1I5jjEzDTFqg'
pb = Pushbullet(api)

console = Console()
zoro = "100089880403782"

profiles = [{
    'account': "Luffy",
    'username': "luffyisthegreat",
},
    {'account': "Lkkkl",
     'username': "100090546784542",
     },
    {'account': "Not Luffy",
     'username': "100090322033128",
     },
    {'account': "Hhhhh",
     'username': "100090079102746",
     },
]


def getLinks(url, li, ep):
    driver.get(url)
    time.sleep(3)
    html_content = driver.page_source

    soup = BeautifulSoup(html_content, "html5lib")
    links = soup.findAll("div", {'class': li})  # 'x78zum5 x1q0g3np x1n2onr6'
    perm = []
    for i in links:
        a = i.find('a')['href']
        if "events" in a:
            ok = a.split("?")[1]
            ok = ok.split("&")[0]
            id = ok.replace("post_id=", "")
            a = a.split("?")[0]+f"?view=permalink&id={id}"

        else:
            a = a.split("?")[0]
        a = a.replace("videos", "posts")
        try:
            episode = int(i.find(
                'span', {'class': ep}).text)  # 'x1lliihq x6ikm8r x10wlt62 x1n2onr6 x1j85h84'
            perm.append({'episode': episode, 'link': a})
        except:
            pass
    perm = sorted(perm, key=lambda x: x['episode'])

    return perm


def login():
    console.print(
        "[red]Entering [blue]https://mbasic.facebook.com/[/blue][/red]")
    driver.get("https://mbasic.facebook.com/")
    console.print("[red]Sleeping for 3secs[/red]")
    time.sleep(3)
    console.print("[red]Entering email & pass[/red]")
    email = driver.find_element(by=By.NAME, value="email")
    password = driver.find_element(by=By.NAME, value="pass")
    email.send_keys(zoro)
    password.send_keys("bilatka123")
    password.send_keys(Keys.RETURN)
    console.print("[red]Sleeping for 3secs[/red]")
    time.sleep(3)
    console.print("[red]Saving Zoro's cookies.[/red]")
    # save cookies
    driver.get("https://www.facebook.com/")
    pickle.dump(driver.get_cookies(), open("zoro.pkl", "wb"))


def checkCookies(name):
    console.print("[yellow]Checking cookies.")
    return os.path.isfile(name)


def loadCookies(name):
    console.print("[yellow]Loading cookies.")
    cookies = pickle.load(open(name, "rb"))
    driver.get("https://www.facebook.com/")
    for cookie in cookies:
        driver.add_cookie(cookie)


def selectProfile():
    while True:
        try:
            console.print("[pink]Which Profile?: [/pink]")
            for e, i in enumerate(profiles):
                print(f"{e+1}. Profile: {i['account']}")
            bogo = int(input("Select: "))
            id = profiles[bogo - 1]['username']
            return id
        except:
            print("Invalid input")


def sendInfo(info, rsp, response):

    print("Sending information")
    pb.push_note(" ", info)
    year = rsp['starting_time'].split("/")[2]
    pb.push_note(year, f" · {rsp['season']}")
    print("Sending cover image")
    with open("cover.jpg", "wb") as f:
        f.write(response.content)
        file_data = ""

    with open("cover.jpg", "rb") as pic:
        file_data = pb.upload_file(pic, "cover.jpg")
        pb.push_file(**file_data)


def askInfo(id):
    query = input("Enter anime: ")
    rsp = anilist.get_anime(query, manual_select=True, )
    response = requests.get(rsp['cover_image'].replace('medium', 'large'))
    desc = rsp['desc'].replace('<br>', '').replace(
        '<i>', '').replace('</i>', '')
    console.print("[red]Waiting for the page to load")
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".xtoi2st"))
        )
    except:
        console.print("[red]Error page not loaded.")
    console.print("[yellow]Fetching 1-13 links")
    first = getLinks(f"https://www.facebook.com/{id}/allactivity?activity_history=false&category_key=COMMENTSCLUSTER&manage_mode=false&should_load_landing_page=false", 'x78zum5 x1q0g3np x1n2onr6',
                     'x1lliihq x6ikm8r x10wlt62 x1n2onr6 x1j85h84')
    second = []
    if(int(rsp['airing_episodes']) > 13):
        console.print("[red]Switch profile for the Second half: ")
        removeCookies()
        loadCookies("zoro.pkl")
        id = selectProfile()
        switchProfile(id)
        time.sleep(1)
        console.print("[yellow]Fetching 13 > links")
        second = getLinks(f"https://www.facebook.com/{id}/allactivity?activity_history=false&category_key=COMMENTSCLUSTER&manage_mode=false&should_load_landing_page=false", 'x78zum5 x1q0g3np x1n2onr6',
                          'x1lliihq x6ikm8r x10wlt62 x1n2onr6 x1j85h84')
    console.print(f"[red]Total links found: {len(first) + len(second)} [/red]")
    all = first
    if second is not None:
        all = first + second
    link = ""
    for i in all:
        link += f"\n\nEpisode {i['episode']}: {i['link']}"
    title = rsp['name_romaji'] if rsp['name_english'] is None else rsp['name_english']
    info = f"Title: { title}\nType: {rsp['airing_format']} \nEpisodes: {rsp['airing_episodes']}\nStatus: {rsp['airing_status']}\nScore: {rsp['average_score']}\nAired:{rsp['starting_time'] }-{ rsp['ending_time']}\nGenre: {', '.join(rsp['genres'])}\nSeason: {rsp['season']}\n\nSynopsis\n{desc}\n\n\nFollow for more: https://www.facebook.com/gojoseenpai/\n\n\nLinks: {link}"
    sendInfo(info, rsp, response)
    removeCookies()


def switchProfile(id):
    console.print(f"[red]Switching to user {id}[/red]")
    driver.get(f"https://www.facebook.com/{id}")
    try:
        console.print(f"[pink]Waiting for the element {id}[/pink]")
        switch = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.x1sxyh0:nth-child(2)"))
        )
        console.print(f"[pink]Switching! ✅ {id}[/pink]")
        switch.click()
    except:
        print("Not found")
        switch = driver.find_element(
            By.CSS_SELECTOR, ".xlhe6ec > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)")
        switch.click()
    time.sleep(2)


def removeCookies():
    console.print("[red]Removing cookies.")
    driver.delete_all_cookies()


def main():
    cookie = "zoro.pkl"
    if(not checkCookies(cookie)):
        login()
    while True:
        loadCookies(cookie)
        driver.get("https://www.facebook.com/")
        id = selectProfile()
        switchProfile(id)
        askInfo(id)
        y = input("Do you want to continue?(Y/N): ")
        if(y == 'n'):
            break


if __name__ == "__main__":
    main()
