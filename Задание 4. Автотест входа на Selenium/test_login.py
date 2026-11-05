"""Автотест формы входа: Page Object, явные ожидания, снимок страницы при падении (хук в conftest.py)."""
import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage

PASSWORD = "Konf-2026-user"


def test_login_ok(driver, base_url):
    page = LoginPage(driver, base_url).open().login_ok("anna_k", PASSWORD)
    assert page.logged_in_as() == "Выйти (anna_k)"
    assert driver.current_url.rstrip("/") == base_url


def test_wrong_password_shows_error(driver, base_url):
    page = LoginPage(driver, base_url).open().login("anna_k", "nepravilnyj")
    assert "введите правильные" in page.error().lower()
    assert page.logged_in_as() is None


@pytest.mark.parametrize("username, password", [
    ("net_takogo", PASSWORD),
    ("' OR '1'='1", "x"),
    ("anna_k ", "nepravilnyj"),
])
def test_bad_credentials_do_not_log_in(driver, base_url, username, password):
    page = LoginPage(driver, base_url).open().login(username, password)
    assert page.error()
    assert page.logged_in_as() is None


@pytest.mark.parametrize("username, password, empty_field", [
    ("", PASSWORD, LoginPage.USERNAME),
    ("anna_k", "", LoginPage.PASSWORD),
])
def test_empty_field_is_stopped_by_browser(driver, base_url, username, password, empty_field):
    page = LoginPage(driver, base_url).open().login(username, password)
    assert page.validation_message(empty_field) != ""
    assert "/login/" in driver.current_url


def test_logout(driver, base_url):
    page = LoginPage(driver, base_url).open().login_ok("maria_v", PASSWORD)
    page.logout()
    assert page.logged_in_as() is None


def test_lockout_after_five_wrong_passwords(driver, base_url):
    page = LoginPage(driver, base_url).open()
    for i in range(5):
        page.open().login("dmitry_s", "nepravilnyj%d" % i)
        page.find(page.FORM_ERROR)
    page.open().login("dmitry_s", PASSWORD)
    assert "слишком много" in page.error().lower()
    assert page.logged_in_as() is None


def test_logged_in_user_is_redirected_from_login_page(driver, base_url):
    page = LoginPage(driver, base_url).open().login_ok("anna_k", PASSWORD)
    page.open()
    page.wait.until(lambda d: "/login/" not in d.current_url)
    assert page.logged_in_as() == "Выйти (anna_k)"


@pytest.mark.manual
def test_demo_failure(driver, base_url):
    """Нарочно падающий тест, нужен только чтобы показать снимок страницы при падении. Запуск: pytest -m manual"""
    page = LoginPage(driver, base_url).open().login("anna_k", "nepravilnyj")
    assert page.logged_in_as() == "Выйти (anna_k)"
