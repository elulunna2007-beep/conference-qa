from selenium.webdriver.common.by import By

from .base_page import BasePage


class RegisterPage(BasePage):
    path = "/register/"
    FIELDS = {"username": (By.NAME, "username"), "email": (By.NAME, "email"), "phone": (By.NAME, "phone"),
              "password1": (By.NAME, "password1"), "password2": (By.NAME, "password2")}
    SUBMIT = (By.CSS_SELECTOR, ".form-card form button")

    def fill(self, **values):
        for name, value in values.items():
            self.type(self.FIELDS[name], value)
        return self

    def submit(self):
        self.click(self.SUBMIT)
        return self

    def register(self, username, email, phone, password):
        return self.fill(username=username, email=email, phone=phone, password1=password, password2=password).submit()

    def errors(self):
        """Все тексты ошибок под полями."""
        return [e.text for e in self.driver.find_elements(By.CSS_SELECTOR, ".errorlist li")]
