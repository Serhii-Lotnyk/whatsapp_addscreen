import os
import time
import logging
import mss
import mss.tools
from screeninfo import get_monitors
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# === НАСТРОЙКИ ===
group_name = "Хмарки"  # Название группы WhatsApp
screenshot_filename = "screenshot.png"
screenshot_interval = 600  # Интервал между скринами в секундах (600 = 10 минут)
log_file = "whatsapp_screenshot_bot.log"

# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

print("Запуск скрипта...")
logging.info("Скрипт запущен.")

# === НАСТРОЙКА ПУТИ К chromedriver И ПРОФИЛЯ ===
CHROMEDRIVER_PATH = os.path.join(os.getcwd(), "chromedriver.exe")
PROFILE_DIR = os.path.join(os.getcwd(), "chrome_profile")
os.makedirs(PROFILE_DIR, exist_ok=True)

# === ЗАПУСК БРАУЗЕРА И ОТКРЫТИЕ WHATSAPP WEB ===
try:
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://web.whatsapp.com")
    logging.info("Открыт WhatsApp Web.")
except Exception as e:
    logging.error(f"Ошибка запуска браузера: {e}")
    exit()

print("Сканируй QR-код в браузере и нажми Enter здесь...")
input("Нажми Enter после входа...")

# === ОТКРЫТИЕ ГРУППЫ ===
def open_group(name):
    try:
        wait = WebDriverWait(driver, 30)
        search_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[contains(@contenteditable,"true") and @data-tab="3"]')))
        print("Ввожу название группы для поиска...")
        search_box.click()
        search_box.clear()
        search_box.send_keys(name)
        time.sleep(2)
        search_box.send_keys(Keys.ENTER)
        time.sleep(4)
        logging.info(f"Открыта группа: {name}")
        print(f"Группа '{name}' открыта.")
    except Exception as e:
        logging.error(f"Не удалось открыть группу '{name}': {e}")
        print(f"[ОШИБКА] Не удалось открыть группу: {e}")

open_group(group_name)

# === ОСНОВНОЙ ЦИКЛ: СКРИНШОТ И ОТПРАВКА ===
while True:
    try:
        logging.info("Создание скриншота второго экрана...")
        print("Создание скриншота второго экрана...")

        monitors = get_monitors()
        if len(monitors) < 2:
            logging.warning("Второй монитор не найден. Пропуск итерации.")
            print("[!] Второй монитор не найден. Пропуск...")
            time.sleep(screenshot_interval)
            continue

        second = monitors[1]
        monitor_region = {
            "left": second.x,
            "top": second.y,
            "width": second.width,
            "height": second.height
        }

        with mss.mss() as sct:
            img = sct.grab(monitor_region)
            mss.tools.to_png(img.rgb, img.size, output=screenshot_filename)

        logging.info("Скриншот сохранён.")
        print("Скриншот сохранён.")

        # Нажать кнопку прикрепления
        print("Ищу кнопку прикрепления (плюс или скрепка)...")
        clip_xpath = '//span[@data-icon="plus"] | //span[@data-icon="clip"]'
        clip_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, clip_xpath))
        )
        clip_button.click()
        logging.info("Кнопка прикрепления нажата.")
        print("Кнопка прикрепления нажата.")
        time.sleep(1)

        # Загрузка файла скриншота
        print("Загружаю скриншот...")
        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//input[@type="file" and @accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
            ))
        )
        file_input.send_keys(os.path.abspath(screenshot_filename))
        logging.info("Файл прикреплён.")
        print("Файл прикреплён.")
        time.sleep(3)

        # Нажать кнопку отправки
        print("Ищу кнопку отправки...")
        send_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        send_button.click()
        logging.info("Скриншот отправлен.")
        print("Скриншот отправлен.")

    except Exception as e:
        logging.error(f"Ошибка при отправке: {e}")
        print(f"[ОШИБКА] {e}")

    logging.info(f"Ожидание {screenshot_interval // 60} минут до следующего скриншота...")
    print(f"Ожидание {screenshot_interval // 60} минут до следующего скриншота...\n")
    time.sleep(screenshot_interval)
