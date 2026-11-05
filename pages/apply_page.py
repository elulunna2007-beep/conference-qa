from selenium.webdriver.common.by import By

from .base_page import BasePage


class ApplyPage(BasePage):
    ROOM = (By.NAME, "room")
    PAYMENT = (By.NAME, "payment")
    COMMENT = (By.NAME, "comment")
    SUBMIT = (By.CSS_SELECTOR, ".form-card form button")

    def open_for(self, event_id):
        return self.open("/events/%d/apply/" % event_id)

    def apply(self, room="Малый зал", payment="Банковская карта", comment=""):
        self.select(self.ROOM, room)
        self.select(self.PAYMENT, payment)
        self.type(self.COMMENT, comment or "Автотест")
        self.click(self.SUBMIT)
        return self
