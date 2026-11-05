import os
import pathlib
import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from portal_server import BASE, Portal

FAILED_DIR = pathlib.Path(__file__).resolve().parent / "failed"


@pytest.fixture(scope="session")
def portal():
    p = Portal()
    p.start()
    yield p
    p.stop()


@pytest.fixture(scope="session")
def base_url(portal):
    return BASE


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def driver(request, base_url):
    options = Options()
    if os.environ.get("QA_HEADED") != "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--lang=ru")
    d = webdriver.Chrome(options=options)
    yield d
    # при падении теста сохраняем снимок страницы
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        FAILED_DIR.mkdir(exist_ok=True)
        d.save_screenshot(str(FAILED_DIR / (request.node.name.replace("/", "_").replace("[", "_").replace("]", "") + ".png")))
    d.quit()


@pytest.fixture
def new_login():
    """Уникальный логин для теста, чтобы тесты не мешали друг другу."""
    return "qa_" + uuid.uuid4().hex[:8]
