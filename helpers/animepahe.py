from config import *
import os
from parsers.animepahe import AnimePaheParser
from utils import *
from downloader import Downloader
import pickle


class AnimePahe():
    def __init__(self, driver):
        self.driver = driver
        self.animepahe_parser = AnimePaheParser(driver)
        self.token = self.getTokenFromFile() if os.path.isfile(
            'token.txt') else self.getToken()
        self.anime_details = {
            'session': None,
            'anime_name': None,
            'avail_qualities': None,
            'source': None
        }
    """ GET TOKEN FROM A FILE IF IT EXIST"""

    def getTokenFromFile(self):
        with open('token.txt', "r") as f:
            token = f.read()
        return token
    """ GET TOKEN MANUALLY FROM KWIK"""

    def getToken(self):
        token = None
        os.system("cls")
        while token is None:
            token = self.animepahe_parser.getKwikToken()
            os.system("cls")
        with open('token.txt', "w") as f:
            f.write(token)
        return token
    """ INITIALIZE NEW SESSION """

    def getNewSession(self):
        os.remove('kwik.pkl')
        os.remove('token.txt')
        self.driver.get("https://kwik.cx/f/mIqErRexBOS8")
        pickle.dump(self.driver.get_cookies(), open("kwik.pkl", "wb"))
        self.animepahe_parser = AnimePaheParser(self.driver)
        self.token = self.getToken()
    """ GET ALL LINKS FROM THE ANIME AND DOWNLOAD IT """

    def getAllLinks(self, episodes):
        token = self.token
        slSource = self.anime_details['source']
        anime_name = self.anime_details['anime_name']
        total = []
        links = ""
        os.system("cls")
        session = self.anime_details['session']

        with progress:

            scarping = progress.add_task(
                "[blue]Scraping download links...", total=len(episodes))
            for i, e in enumerate(episodes):

                link = self.animepahe_parser.getEpisodeLink(session,
                                                            e['session'], slSource['quality'], slSource['audio'], slSource['fansub'])

                if link is not dict:
                    link = self.animepahe_parser.getDefault(session,
                                                            e['session'])
                ads = link['kwik_pahewin']
                kwik = self.animepahe_parser.getKwikLink(ads)

                download_link = self.animepahe_parser.getLink(kwik.replace(
                    "cx/f", "cx/d"), kwik, anime_name+f" Episode {e['episode']}.mp4", token, self.animepahe_parser.getCookie())
                if download_link is None:
                    create_msg(
                        "Updating", "Session expired, updating session...", TEXT_MSG_COLOR[0])
                    self.getNewSession()
                    token = self.token
                    download_link = self.animepahe_parser.getLink(kwik.replace(
                        "cx/f", "cx/d"), kwik, anime_name+f" Episode {e['episode']}.mp4", token, self.animepahe_parser.getCookie())

                links += f'{download_link.replace(" ","_")}\n\n'
                total.insert(
                    i, {'episode': e['episode'], 'url': download_link})
                progress.update(scarping, advance=1)
            progress.remove_task(scarping)
        # push = pb.push_note(
        #     anime_name, f"Here are the links of {anime_name}: {links} ")
        return total
    """ INITIALIZATION OF THE APPLICATION """

    def start(self):
        query = create_prompt("Search anime")
        os.system("cls")
        results = create_loading(
            ":mag_right: Searching for", TEXT_MSG_COLOR[1], self.animepahe_parser.search, query)
        if(results is None):
            create_msg('Error', "No anime found. 😥", TEXT_MSG_COLOR[3])
            return
        display_results(results)
        try:
            selected = int(create_prompt("Select anime: "))
        except:
            create_msg("Error", "Please input an integer.", TEXT_MSG_COLOR[3])
        if(selected == - 1):
            return ""
        if(selected > len(results) or selected == 0):
            create_msg("Error", "Invalid input", TEXT_MSG_COLOR[3])
            return ""
        self.anime_details['session'] = results[selected - 1]['session']
        self.anime_details['name'] = results[selected -
                                             1]['title'].replace(":", "").replace("*", "")
        os.system("cls")
        details = create_loading(":mag_right: Searching for anime details...",
                                 TEXT_MSG_COLOR[1], self.animepahe_parser.getDetails, self.anime_details['session'])
        if details[2] != "":
            self.anime_details['anime_name'] = details[2]
        else:
            self.anime_details['anime_name'] = results[selected -
                                                       1]['title'].replace(":", "").replace("*", "")

        createDirectory(self.anime_details['anime_name'])
        start, end = [1, 1]
        if(details[0] + details[1] != 2):
            """ ONLY STOPS WHEN THE INPUT IS CORRECT """
            while True:
                start = int(create_prompt("Enter start of episode: "))
                if(start < details[0]):
                    create_msg(
                        "Error", f"Start of episode must start at {details[0]}.")
                    continue
                break
            while True:
                end = int(create_prompt(
                    f"Enter end of episode ({details[1]}): "))
                if(end > details[1]):
                    create_msg(
                        "Error", f"End of episode must not be greater than {details[1]}.")
                    continue
                break
        os.system("cls")
        """ GET THE AVAILABLE QUALITIES OF THE ANIME """
        episodes = create_loading(":sparkles: Fetching available qualities", LOADING,
                                  self.animepahe_parser.getEpisodes, self.anime_details['session'], start, end)
        self.anime_details['avail_qualities'] = self.animepahe_parser.getQualities(
            self.anime_details['session'], episodes[0]['session'])
        displayQualities(self.anime_details['avail_qualities'])
        quality = None

        while True:
            quality = int(create_prompt("Select quality/source: "))
            if(quality > len(self.anime_details['avail_qualities']) or quality == 0):
                create_msg("Error", "Invalid input.", TEXT_MSG_COLOR[3])
                continue
            break
        self.anime_details['source'] = self.anime_details['avail_qualities'][quality - 1]
        a = self.anime_details['anime_name'].replace(":", "").replace("/", "")
        a = a.replace("/", "").replace("\\", "")
        print(a)
        """ STARTS THE DOWNLOAD AND DISPLAYS IT """
        dl = Downloader(self.getAllLinks(episodes),
                        a, f"downloads/{a}", 2).start()

        create_msg(
            "Success", f"All episodes of {self.anime_details['anime_name']} has been downloaded.", TEXT_MSG_COLOR[0])
        return dl
