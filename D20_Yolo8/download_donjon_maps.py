import os
import time
import uuid
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === 下载配置 ===
DOWNLOAD_FOLDER = os.path.abspath("donjon_maps_forTest")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

NUM_MAPS = 30           # 要下载几张地图
WAIT_SECONDS = 3        # 下载后等待时间（秒）

# === 设置 Chrome ===
options = Options()
prefs = {
    "download.default_directory": DOWNLOAD_FOLDER,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")  # 可加这行启用无头浏览器

# === 创建 driver ===
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def wait_for_download(before_files):
    """等待 PNG 下载完成"""
    for _ in range(WAIT_SECONDS * 5):
        time.sleep(1)
        after = os.listdir(DOWNLOAD_FOLDER)
        new_files = [f for f in after if f not in before_files and f.endswith(".png")]
        if new_files:
            return new_files[0]
    return None

# === 主循环 ===
for i in range(NUM_MAPS):
    uuids = uuid.uuid4()
    print(f"📥 [{i+1}/{NUM_MAPS}] Generating dungeon map... {uuids}")

    try:
        driver.get("https://donjon.bin.sh/d20/dungeon/")
        wait = WebDriverWait(driver, 10)

        # 点击 Random Dungeon
        rand_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Random Dungeon"]')))
        rand_btn.click()
        time.sleep(1)

        # 点击 Construct Dungeon
        construct_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Construct Dungeon"]')))
        construct_btn.click()
        time.sleep(1)

        download_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Download   ▶"]')))
        download_btn.click()
        time.sleep(1)

        # 点击 PNG 下载
        png_btn = wait.until(EC.element_to_be_clickable((By.XPATH,  '//input[@value="Download Map"]')))
        before = os.listdir(DOWNLOAD_FOLDER)
        png_btn.click()
        time.sleep(5)

        # 等待下载完成
        new_file = wait_for_download(before)
        if new_file:
            new_name = f"dungeon_{uuids}.png"
            shutil.move(os.path.join(DOWNLOAD_FOLDER, new_file), os.path.join(DOWNLOAD_FOLDER, new_name))
            print(f"✅ Saved: {new_name}")
        else:
            print("⚠️ Timeout: PNG not saved.")

    except Exception as e:
        print(f"❌ Error on map {i+1}: {e}")

driver.quit()
print(f"🎉 Done! Maps saved in: {DOWNLOAD_FOLDER}")
