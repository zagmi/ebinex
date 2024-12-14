import whisper
import os, time, requests
from selenium.webdriver.common.by import By
from iykyk import WebDriver, NoSuchElementException


class Captcha:
    def __init__(self, conn: WebDriver):
        self.__driver = conn
        self.__model = whisper.load_model("base")
        self.fns = {
            2: self.__click_checkbox,
            3: self.__check_eval_status,
            4: self.__request_audio_version,
            5: self.__solve_audio_captcha,
        }

    def __click_checkbox(self):
        self.__driver.switch_to.default_content()
        self.__driver.switch_to.frame(self.__driver.find_element(By.XPATH, './/iframe[@title="reCAPTCHA"]'))
        self.__driver.find_element(By.ID, "recaptcha-anchor-label").click()

    def __check_eval_status(self):
        try:
            if self.__driver.find_element(By.XPATH, '//*[@id="recaptcha-anchor" and @aria-checked="true"]'):
                return True
        except NoSuchElementException:
            pass

        self.__driver.switch_to.default_content()
        return False

    def __request_audio_version(self):
        self.__driver.switch_to.default_content()
        self.__driver.switch_to.frame(
            self.__driver.find_element(By.XPATH, './/iframe[@title="recaptcha challenge expires in two minutes"]'))
        self.__driver.find_element(By.ID, "recaptcha-audio-button").click()

    def __solve_audio_captcha(self):
        text = self.__transcribe(self.__driver.find_element(By.ID, "audio-source").get_attribute("src"))
        self.__driver.find_element(By.ID, "audio-response").send_keys(text)
        self.__driver.find_element(By.ID, "recaptcha-verify-button").click()
        self.__driver.switch_to.default_content()

    def __transcribe(self, url: str):
        with open(".temp", "wb") as f:
            f.write(requests.get(url).content)
            result = self.__model.transcribe(f.name)

        try:
            os.remove(f.name)
        except FileNotFoundError:
            pass

        return result["text"].strip()

    def resolve(self):
        try:
            for sp, func in self.fns.items():
                if func() == True:
                    break
                time.sleep(sp)
            if not self.__check_eval_status():
                self.resolve()
        finally:
            self.__driver.switch_to.default_content()
