"""Проверка форм регистрации и входа по классам эквивалентности и граничным значениям.
Скрипт сам запускает портал на временной базе, отправляет формы так же, как браузер (с токеном CSRF),
и сравнивает ответ с ожидаемым. Запуск: python check_forms.py"""
import pathlib
import sys
import uuid

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from portal_server import BASE, Portal  # noqa: E402

rows = []


def rnd(n):
    return uuid.uuid4().hex[:n]


def post_form(path, data, session=None):
    s = session or requests.Session()
    r = s.get(BASE + path)
    token = s.cookies["csrftoken"]
    return s.post(BASE + path, data=dict(data, csrfmiddlewaretoken=token), allow_redirects=False)


def good_reg(**kw):
    login = "r_" + rnd(8)
    d = {"username": login, "email": login + "@example.com", "phone": "+7 916 123-45-67",
         "password1": "Pr0verka-2026", "password2": "Pr0verka-2026"}
    d.update(kw)
    return d


def check(cid, field, data_text, expect_ok, path, data):
    """expect_ok: ожидаем успех (перенаправление) или отказ (страница с ошибкой)."""
    r = post_form(path, data)
    ok = r.status_code == 302
    passed = ok == expect_ok
    rows.append((cid, field, data_text, "принять" if expect_ok else "отклонить", "принято" if ok else "отклонено", "Пройдена" if passed else "НЕ ПРОЙДЕНА"))
    return r


def reg(cid, field, data_text, expect_ok, **kw):
    return check(cid, field, data_text, expect_ok, "/register/", good_reg(**kw))


def run():
    # регистрация: логин
    reg("R-01", "все поля", "корректные данные", True)
    reg("R-02", "логин", "2 символа", False, username="ab")
    reg("R-03", "логин", "3 символа", True, username="q" + rnd(2), email="r03@example.com")
    reg("R-04", "логин", "20 символов", True, username="r20_" + rnd(16), email="r04@example.com")
    reg("R-05", "логин", "21 символ", False, username="r21_" + rnd(17))
    reg("R-06", "логин", "с пробелом", False, username="ab cd")
    reg("R-07", "логин", "кириллица", False, username="логин_ру")
    reg("R-08", "логин", "admin (уже есть)", False, username="admin")
    reg("R-09", "логин", "ADMIN (другой регистр)", False, username="ADMIN")
    reg("R-10", "логин", "<script>", False, username="<script>")
    reg("R-11", "логин", "пусто", False, username="")
    # почта
    reg("R-12", "почта", "name@site.ru", True, email="r12" + rnd(4) + "@site.ru")
    reg("R-13", "почта", "без @", False, email="nameatsite.ru")
    reg("R-14", "почта", "name@site (без точки)", False, email="name@site")
    reg("R-15", "почта", "255 символов", False, email="a" * 243 + "@example.com")
    reg("R-16", "почта", "пусто", False, email="")
    # телефон
    reg("R-17", "телефон", "+79161234567", True, phone="+79161234567")
    reg("R-18", "телефон", "8 (916) 123-45-67", True, phone="8 (916) 123-45-67")
    reg("R-19", "телефон", "12345", False, phone="12345")
    reg("R-20", "телефон", "буквы в номере", False, phone="+7 916 abc-45-67")
    reg("R-21", "телефон", "9 цифр после +7", False, phone="+7916123456")
    reg("R-22", "телефон", "11 цифр после +7", False, phone="+791612345678")
    reg("R-23", "телефон", "не российский", False, phone="+1 202 555 0100")
    reg("R-24", "телефон", "пусто", False, phone="")
    # пароль
    reg("R-25", "пароль", "7 символов", False, password1="Ab1-xyz", password2="Ab1-xyz")
    reg("R-26", "пароль", "8 символов", True, password1="Ab1-xyzq", password2="Ab1-xyzq")
    reg("R-27", "пароль", "8 цифр", False, password1="40719283", password2="40719283")
    reg("R-28", "пароль", "password (частый)", False, password1="password", password2="password")
    reg("R-29", "пароль", "8 пробелов", False, password1=" " * 8, password2=" " * 8)
    reg("R-30", "пароль", "подтверждение не совпадает", False, password2="Drugoj-2026-x")
    login = "r_" + rnd(8)
    reg("R-31", "пароль", "совпадает с логином", False, username=login, email=login + "@example.com", password1=login, password2=login)
    reg("R-32", "пароль", "200 символов", True, password1="Aa1-" * 50, password2="Aa1-" * 50)
    # вход
    check("L-01", "вход", "верный логин и пароль", True, "/login/", {"username": "anna_k", "password": "Konf-2026-user"})
    check("L-02", "вход", "неверный пароль", False, "/login/", {"username": "anna_k", "password": "nepravilnyj"})
    check("L-03", "вход", "неизвестный логин", False, "/login/", {"username": "net_takogo", "password": "Konf-2026-user"})
    check("L-04", "вход", "пустой пароль", False, "/login/", {"username": "anna_k", "password": ""})
    check("L-05", "вход", "пустой логин", False, "/login/", {"username": "", "password": "Konf-2026-user"})
    check("L-06", "вход", "SQL-инъекция в логине", False, "/login/", {"username": "' OR '1'='1", "password": "x"})
    for _ in range(5):
        post_form("/login/", {"username": "dmitry_s", "password": "nepravilnyj"})
    check("L-07", "вход", "верный пароль после 5 ошибок подряд", False, "/login/", {"username": "dmitry_s", "password": "Konf-2026-user"})
    r = post_form("/login/?next=https://evil.example/", {"username": "maria_v", "password": "Konf-2026-user"})
    safe = r.status_code == 302 and "evil.example" not in r.headers.get("Location", "")
    rows.append(("L-08", "вход", "next=внешний адрес", "остаться на портале", "остались" if safe else "ушли на чужой адрес", "Пройдена" if safe else "НЕ ПРОЙДЕНА"))


if __name__ == "__main__":
    portal = Portal()
    portal.start()
    try:
        run()
    finally:
        portal.stop()
    w = [5, 8, 36, 20, 12, 12]
    print("%-5s %-8s %-36s %-20s %-12s %s" % ("ID", "Поле", "Данные", "Ожидание", "Результат", "Статус"))
    for r in rows:
        print("%-5s %-8s %-36s %-20s %-12s %s" % r)
    bad = [r for r in rows if r[-1] != "Пройдена"]
    print("Всего проверок: %d, пройдено: %d, не пройдено: %d" % (len(rows), len(rows) - len(bad), len(bad)))
    for r in bad:
        print("Не пройдена:", r[0], r[2])
    sys.exit(1 if bad else 0)
