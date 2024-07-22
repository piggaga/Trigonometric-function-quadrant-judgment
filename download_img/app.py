import os
import base64
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm.rich import tqdm
import threading

def fetch_image(img_url, folder_path, headers, img_idx, downloaded_urls):
    try:
        if img_url in downloaded_urls:
            print(f'圖片已經下載過: {img_url}')
            return
        
        if img_url.startswith('data:image'):
            base64_str = img_url.split(',')[1]
            img_data = base64.b64decode(base64_str)
            img_name = f'image_{img_idx}.png'
        else:
            img_response = requests.get(img_url, headers=headers)
            img_response.raise_for_status()
            content_type = img_response.headers.get('Content-Type', '')
            if 'image/png' in content_type:
                img_ext = '.png'
            elif 'image/jpeg' in content_type:
                img_ext = '.jpg'
            else:
                img_ext = '.png'
            img_name = os.path.basename(img_url).replace('/', '_').replace('?', '_') + img_ext
            img_data = img_response.content
        
        img_path = os.path.join(folder_path, img_name)
        with open(img_path, 'wb') as img_file:
            img_file.write(img_data)
        
        downloaded_urls.add(img_url)
        print(f'下載圖片: {img_name}')
    except Exception as e:
        print(f'無法下載圖片 {img_url}: {e}')

def fetch_images(url, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        img_tags = soup.find_all('img')
        total_images = len(img_tags)

        downloaded_urls = set()
        with tqdm(total=total_images, desc="下載圖片") as pbar:
            threads = []
            for idx, img_tag in enumerate(img_tags):
                img_src = img_tag.get('src')
                if not img_src:
                    pbar.update(1)
                    continue
                
                img_url = urljoin(url, img_src)
                thread = threading.Thread(target=fetch_image, args=(img_url, folder_path, headers, idx, downloaded_urls))
                thread.start()
                threads.append(thread)
                
                if len(threads) >= 10:
                    for thread in threads:
                        thread.join()
                    threads = []
                
                pbar.update(1)
            
            for thread in threads:
                thread.join()
        
        print(f'總共下載圖片數量: {len(downloaded_urls)}')
    except Exception as e:
        print(f'無法處理網站 {url}: {e}')

while True:
    website_url = input("輸入要抓取圖片的網站 URL: ")
    save_folder = 'images'

    fetch_images(website_url, save_folder)
    
    while True:
        continue_scraping = input("是否要抓取另一個網站的圖片? (y/n): ").strip().lower()
        if continue_scraping in ['y', 'n']:
            break
        print("無效的輸入，請輸入 'y' 或 'n'。")
    
    if continue_scraping != 'y':
        break

print("圖片抓取完成。")
