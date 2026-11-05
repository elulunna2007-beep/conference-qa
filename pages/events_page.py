from selenium.webdriver.common.by import By

from .base_page import BasePage


class EventsPage(BasePage):
    path = "/events/"
    CARDS = (By.CSS_SELECTOR, ".cards .card")
    SEARCH = (By.NAME, "q")

    def titles(self):
        self.find(self.CARDS)
        return [c.find_element(By.CSS_SELECTOR, "h3").text for c in self.driver.find_elements(*self.CARDS)]

    def search(self, text):
        self.type(self.SEARCH, text)
        self.click((By.CSS_SELECTOR, ".filters .btn"))
        return self
