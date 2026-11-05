from selenium.webdriver.common.by import By

from .base_page import BasePage


class ManagePage(BasePage):
    path = "/manage/"
    CARDS = (By.CSS_SELECTOR, ".app-list .app-card")
    TITLE = (By.CSS_SELECTOR, "h1")

    def cards(self):
        return self.driver.find_elements(*self.CARDS)

    def count_text(self):
        return self.text((By.CSS_SELECTOR, ".meta"))
