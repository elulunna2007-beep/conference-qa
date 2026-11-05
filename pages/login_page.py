from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class LoginPage(BasePage):
    path = "/login/"
    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "password")
    SUBMIT = (By.CSS_SELECTOR, ".form-card form button")
    FORM_ERROR = (By.CSS_SELECTOR, ".form-error")

    def login(self, username, password):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)
        return self

    def login_ok(self, username, password):
        """Вход и ожидание, пока уйдём со страницы входа."""
        self.login(username, password)
        self.wait.until(EC.url_changes(self.base_url + self.path))
        return self

    def error(self):
        return self.text(self.FORM_ERROR)

    def validation_message(self, locator):
        """Подсказка браузера у поля (когда поле пустое и required)."""
        return self.find(locator).get_attribute("validationMessage")
