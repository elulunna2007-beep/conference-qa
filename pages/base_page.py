from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 10


class BasePage:
    """Общие действия всех страниц. Ожидания только явные (WebDriverWait), пауз sleep нет."""
    path = "/"

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, TIMEOUT)

    def open(self, path=None):
        self.driver.get(self.base_url + (path or self.path))
        return self

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def text(self, locator):
        return self.find(locator).text

    def wait_url_contains(self, part):
        self.wait.until(EC.url_contains(part))

    def present(self, locator):
        return len(self.driver.find_elements(*locator)) > 0

    def select(self, locator, visible_text):
        from selenium.webdriver.support.ui import Select
        Select(self.find(locator)).select_by_visible_text(visible_text)

    # блоки, которые есть на каждой странице
    LOGOUT = (By.CSS_SELECTOR, ".nav .link-button")
    MESSAGE = (By.CSS_SELECTOR, ".msg")

    def logged_in_as(self):
        """Текст кнопки выхода «Выйти (логин)» или None, если не вошли."""
        els = self.driver.find_elements(*self.LOGOUT)
        return els[0].text if els else None

    def logout(self):
        self.click(self.LOGOUT)
        self.wait.until(EC.invisibility_of_element_located(self.LOGOUT))
