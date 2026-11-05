"""Смоук-тесты портала: главная страница, вход, заявка, панель администратора, защита панели."""
import pytest
from selenium.webdriver.common.by import By

from pages.apply_page import ApplyPage
from pages.events_page import EventsPage
from pages.login_page import LoginPage
from pages.manage_page import ManagePage
from pages.register_page import RegisterPage

pytestmark = pytest.mark.smoke


def test_home_page_shows_events(driver, base_url):
    driver.get(base_url + "/")
    assert "Конференции.РФ" in driver.title
    titles = EventsPage(driver, base_url).open().titles()
    assert len(titles) == 9


def test_participant_login_opens_my_applications(driver, base_url):
    LoginPage(driver, base_url).open().login_ok("anna_k", "Konf-2026-user")
    page = ManagePage(driver, base_url).open("/applications/")
    assert page.text(page.TITLE) == "Мои заявки"
    assert len(page.cards()) >= 1


def test_new_user_can_apply_for_event(driver, base_url, new_login):
    RegisterPage(driver, base_url).open().register(new_login, new_login + "@example.com", "+7 916 000-11-22", "Smoke-parol-2026")
    ApplyPage(driver, base_url).open_for(5).apply(room="Онлайн-трансляция", payment="Банковская карта")
    page = ManagePage(driver, base_url)
    page.wait_url_contains("/applications/")
    assert "Заявка отправлена" in page.text(page.MESSAGE)
    assert page.text((By.CSS_SELECTOR, ".status")) == "новая"


def test_admin_moves_application_to_next_status(driver, base_url):
    LoginPage(driver, base_url).open().login_ok("admin", "Admin-2026-Konf")
    page = ManagePage(driver, base_url).open("/manage/?status=1")
    assert page.cards()
    page.click((By.CSS_SELECTOR, ".app-card form button"))
    assert "Статус заявки изменён" in page.text(page.MESSAGE)


def test_guest_cannot_open_admin_panel(driver, base_url):
    driver.get(base_url + "/manage/")
    LoginPage(driver, base_url).wait_url_contains("/login/")
    assert "next=/manage/" in driver.current_url
