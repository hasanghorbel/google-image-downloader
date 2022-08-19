import os
import time
import base64
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

search = input('what do you wanna search for : ')

def Get(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    time.sleep(3)
    thumbnails = driver.find_elements(By.CLASS_NAME, "Q4LuWd")
    image_urls = set()

    for thumbnail in thumbnails:
        try:
            thumbnail.click()
            time.sleep(3)
            images = driver.find_elements(By.CLASS_NAME, "n3VNCb")
            for img in images:
                if img.get_attribute('src'):
                    image_urls.add(img.get_attribute('src'))
        except:
            print(thumbnail)

    driver.close()
    return list(image_urls)


def Download(images):
    if not os.path.isdir('imgs'):
        os.makedirs('imgs')
    for index in range(len(images)):
        image_data = images[index]
        with open(f'imgs/{index}.jpg', 'wb') as handle:

            if image_data and 'http' in image_data:
                r = requests.get(image_data)
                if not r.ok:
                    print(r)
                else:
                    handle.write(r.content)

            elif image_data and 'data' in image_data:
                try:
                    _, data = image_data.split(',', 1)
                    plain_data = base64.b64decode(data)
                    handle.write(plain_data)
                except:
                    print(image_data)


def main(url):
    images = Get(url)
    print(f'found {len(images)} images\nBegin Downloading..')
    Download(images)


main(f'https://www.google.com/search?q={search}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjH7trNi7b5AhW2hP0HHRFYAYUQ_AUoAXoECAIQAw&biw=1536&bih=731&dpr=1.25')
