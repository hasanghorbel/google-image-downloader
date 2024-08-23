import os
import time
import base64
import argparse

import requests
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchWindowException,
                                        TimeoutException)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import ProtocolError
from webdriver_manager.chrome import ChromeDriverManager

REQUEST_HEADER = {
    'User-Agent': 'python-requests/2.31.0',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': '*/*',
    'Connection': 'keep-alive',
}

CLICKABLE_IMG_CLASS = "czzyk.XOEbc"
IMG_CLASS = "sFlh5c.FyHeAf.iPVvYb"

def Get(search_key, num_images):
    try:
        url = f'https://www.google.com/search?q={search_key.replace(" ", "+")}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjH7trNi7b5AhW2hP0HHRFYAYUQ_AUoAXoECAIQAw&biw=1536&bih=731&dpr=1.25'

        driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install()))
        driver.get(url)
        time.sleep(3)
        thumbnails = driver.find_elements(By.CLASS_NAME, CLICKABLE_IMG_CLASS)
        image_urls = list()
        timeout = 60

    except NoSuchWindowException:
        print("error: search window not found!!!")
        return list()

    i = 0
    skips = 0
    while (i != num_images) and (skips != 15):
        try:
            element_clickable = EC.element_to_be_clickable(thumbnails[i+skips])
            WebDriverWait(driver, timeout).until(element_clickable).click()
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, IMG_CLASS))
            WebDriverWait(driver, timeout).until(element_present)
            img = driver.find_element(By.CLASS_NAME, IMG_CLASS)
            image_urls.append(img.get_attribute('src'))
            i += 1

        except TimeoutException:
            print("\nerror: this image couldn't load: ")
            print(thumbnails[i+skips].get_attribute('src'))
            skips += 1

        except ElementClickInterceptedException:
            print("\nerror: couldn't click this image: ")
            print(thumbnails[i+skips].get_attribute('src'))
            skips += 1

        except NoSuchWindowException:
            print("\nerror: search window not found!!!")
            return image_urls

        except ProtocolError:
            print("\nerror: search window not found!!!")
            return image_urls

    driver.close()
    return list(image_urls)


def Download(images):
    skips = 0
    if not os.path.isdir('imgs'):
        os.makedirs('imgs')
    for index in range(1, len(images)+1):
        image_data = images[index-1]
        skip = False
        with open(f'imgs/{index-skips}.jpg', 'wb') as handle:
            print("Downloading image n°", index)
            if image_data and 'http' in image_data:
                r = requests.get(image_data, headers=REQUEST_HEADER)
                if not r.ok:
                    skip = True
                else:
                    handle.write(r.content)

            elif image_data and 'data' in image_data:
                try:
                    _, data = image_data.split(',', 1)
                    plain_data = base64.b64decode(data)
                    handle.write(plain_data)
                except:
                    skip = True

        if skip:
            print("couldn't download: \n", image_data)
            os.remove(f'imgs/{index-skips}.jpg')
            skips += 1


def main():
    parser = argparse.ArgumentParser(description='Scrape Google Images')
    parser.add_argument('-s', '--search', default='cat',
                        type=str, help='search key')
    parser.add_argument('-n', '--num_images', default=5,
                        type=int, help='num images to dwonload')
    args = parser.parse_args()
    print("\nFetching Data")
    images = Get(args.search, args.num_images)
    print(f'\nfound {len(images)} images\n\nBegin Downloading..\n')
    Download(images)
    print("\nFinished Downloading.")


if __name__ == '__main__':
    main()
