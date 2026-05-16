import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from captchasolver import solvecaptcha
from config import headless, browsertimeout

def bypassbrowser(url):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    driver = None
    try:
        driver = uc.Chrome(options=options)
        driver.get(url)
        wait = WebDriverWait(driver, browsertimeout)
        for attempt in range(60):
            current = driver.current_url
            if current != url and 'linkvertise' not in current and 'lootlabs' not in current and 'adf.ly' not in current:
                return current
            time.sleep(1)
            try:
                if 'captcha' in driver.page_source.lower():
                    img = driver.find_element(By.XPATH, '//img[contains(@src,"captcha")]')
                    imgbytes = img.screenshot_as_png
                    captcha_text = solvecaptcha(imgbytes)
                    if captcha_text:
                        inputbox = driver.find_element(By.XPATH, '//input[@type="text"]')
                        inputbox.send_keys(captcha_text)
                        submit = driver.find_element(By.XPATH, '//button[@type="submit"]')
                        submit.click()
                        time.sleep(3)
                btns = driver.find_elements(By.XPATH, "//a[contains(text(),'Free Access') or contains(text(),'Continue') or contains(text(),'Skip') or contains(@class,'btn')]")
                for btn in btns:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        time.sleep(2)
                        break
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                if len(iframes) > 0:
                    driver.switch_to.frame(iframes[0])
                    closebtn = driver.find_element(By.XPATH, "//button[contains(text(),'Close')]")
                    closebtn.click()
                    driver.switch_to.default_content()
            except:
                pass
        final = driver.current_url
        if final != url:
            return final
        return None
    except Exception as e:
        return None
    finally:
        if driver:
            driver.quit()
