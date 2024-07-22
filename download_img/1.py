import os
import requests
from bs4 import BeautifulSoup

class ImageScraper:
    def __init__(self, url, download_folder):
        self.url = url
        self.download_folder = download_folder
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def download_image(self, img_url):
        response = requests.get(img_url)
        if response.status_code == 200:
            img_name = os.path.join(self.download_folder, img_url.split('/')[-1])
            with open(img_name, 'wb') as f:
                f.write(response.content)

    def scrape_images(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for img_tag in soup.find_all('img'):
            img_url = img_tag.get('src')
            if img_url:
                if not img_url.startswith('http'):
                    img_url = self.url + img_url
                self.download_image(img_url)

# 示例用法
if __name__ == "__main__":
    website_url = 'https://www.instagram.com/chia__yiii/'  # 替換為你要爬取的網站 URL
    download_folder = 'images'

    scraper = ImageScraper(website_url, download_folder)
    scraper.scrape_images()
