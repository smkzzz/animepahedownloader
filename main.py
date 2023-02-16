

import os
import time
import pickle
from Driver import Driver
from utils import *
from helpers.animepahe import AnimePahe
os.system("cls")
driver = Driver()
animepahe = AnimePahe(driver.getDriver())
if __name__ == '__main__':
    while True:
        animepahe.start()
        answer = create_prompt("Do you want to continue?(Y/N)")
        if(answer != 'y'):
            break
