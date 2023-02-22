

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
        try:
            result = animepahe.start()
            for i in result[0]:
                result[1].remove_task(i['task'])
        except:
            pass
        answer = create_prompt("Do you want to continue?(Y/N)")
        if(answer != 'y'):
            break
