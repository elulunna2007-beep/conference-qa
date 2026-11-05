"""Проверка сценариев портала через HTTP: заявки, статусы, отзывы, права, служебные адреса.
Сам запускает портал на временной базе. Запуск: python check_flows.py"""
import pathlib
import re
import sys

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from portal_server import BASE, Portal  # noqa: E402

rows = []


def add(cid, what, expected, got_ok, got_text):
    rows.append((cid, what, expected, got_text, "Пройдена" if got_ok else "НЕ ПРОЙДЕНА"))


def session(user=None, password=None):
    s = requests.Session()
    if user:
        s.get(BASE + "/login/")
        r = s.post(BASE + "/login/", data={"username": user, "password": password, "csrfmiddlewaretoken": s.cookies["csrftoken"]}, allow_redirects=False)
        assert r.status_code == 302, "не удалось войти как " + user
    return s


def post(s, path, data=None):
    if "csrftoken" not in s.cookies:
        s.get(BASE + "/")
    return s.post(BASE + path, data=dict(data or {}, csrfmiddlewaretoken=s.cookies["csrftoken"]), allow_redirects=False)


def run(portal):
    guest = session()
    anna = session("anna_k", "Konf-2026-user")
    maria = session("maria_v", "Konf-2026-user")
    dmitry = session("dmitry_s", "Konf-2026-user")
    admin = session("admin", "Admin-2026-Konf")

    r = guest.get(BASE + "/")
    add("F-01", "гость открывает главную", "200 и 3 карточки", r.status_code == 200 and r.text.count('class="card"') == 3, "%d, карточек %d" % (r.status_code, r.text.count('class="card"')))
    r = guest.get(BASE + "/events/")
    add("F-02", "список мероприятий", "200 и 9 карточек", r.status_code == 200 and r.text.count('class="card"') == 9, "%d, карточек %d" % (r.status_code, r.text.count('class="card"')))
    r = guest.get(BASE + "/events/", params={"q": "Python"})
    add("F-03", "поиск «Python»", "одна карточка", r.text.count('class="card"') == 1, "карточек %d" % r.text.count('class="card"'))
    r = guest.get(BASE + "/events/?q=%25")
    add("F-04", "поиск по символу «%»", "ничего не найдено без ошибки", r.status_code == 200 and r.text.count('class="card"') == 0, "%d, карточек %d" % (r.status_code, r.text.count('class="card"')))

    # заявки
    r = post(maria, "/events/4/apply/", {"room": "Малый зал", "payment": "Банковская карта", "comment": "тест"})
    add("F-05", "участник подаёт заявку", "302 на «Мои заявки»", r.status_code == 302, str(r.status_code))
    r = post(maria, "/events/4/apply/", {"room": "Малый зал", "payment": "Банковская карта"})
    add("F-06", "вторая заявка на то же мероприятие", "отказ (200 с ошибкой)", r.status_code == 200, str(r.status_code))
    r = post(maria, "/events/1/apply/", {"room": "Малый зал", "payment": "Банковская карта"})
    add("F-07", "заявка на прошедшее мероприятие", "отказ (200 с ошибкой)", r.status_code == 200, str(r.status_code))
    r = post(maria, "/events/5/apply/", {"room": "Подвал", "payment": "Банковская карта"})
    add("F-08", "помещение не из списка", "отказ (200 с ошибкой)", r.status_code == 200, str(r.status_code))
    r = post(admin, "/events/5/apply/", {"room": "Малый зал", "payment": "Банковская карта"})
    add("F-09", "администратор подаёт заявку", "403", r.status_code == 403, str(r.status_code))

    # права
    r = anna.get(BASE + "/manage/")
    add("F-10", "участник открывает панель", "403", r.status_code == 403, str(r.status_code))
    r = guest.get(BASE + "/applications/", allow_redirects=False)
    add("F-11", "гость открывает «Мои заявки»", "302 на вход", r.status_code == 302 and "/login/" in r.headers["Location"], "%d %s" % (r.status_code, r.headers.get("Location", "")))
    r = post(anna, "/applications/4/cancel/")
    add("F-12", "участник отменяет чужую заявку", "404", r.status_code == 404, str(r.status_code))
    r = post(anna, "/manage/applications/5/next/")
    add("F-13", "участник меняет статус заявки", "403", r.status_code == 403, str(r.status_code))

    # статусы
    r = post(admin, "/manage/applications/6/next/")
    add("F-14", "администратор: новая -> назначено", "302", r.status_code == 302, str(r.status_code))
    post(admin, "/manage/applications/6/next/")
    post(admin, "/manage/applications/6/next/")
    page = admin.get(BASE + "/manage/?status=3&event=4").text
    add("F-15", "статус не уходит дальше «завершено»", "заявка остаётся «завершено»", "Участник dmitry_s" in page, "завершено" if "Участник dmitry_s" in page else "другой")

    # отзывы
    r = post(anna, "/applications/5/review/", {"rating": 5, "text": "Отзыв до завершения заявки"})
    add("F-16", "отзыв на заявку, которая не завершена", "отказ (302 на «Мои заявки» без сохранения)", r.status_code == 302, str(r.status_code))
    r = post(anna, "/applications/3/review/", {"rating": 5, "text": "Хорошие доклады, всё понравилось"})
    add("F-17", "отзыв после завершения", "302 и отзыв сохранён", r.status_code == 302 and "Хорошие доклады" in guest.get(BASE + "/events/2/").text, str(r.status_code))
    # заявка maria на прошедшее мероприятие доведена до «завершено» администратором
    post(admin, "/manage/applications/4/next/")
    r = post(maria, "/applications/4/review/", {"rating": 0, "text": "Оценка ноль, должна отклониться"})
    add("F-18", "отзыв с оценкой 0", "отказ (200 с ошибкой)", r.status_code == 200, str(r.status_code))
    out = portal.manage("shell", "-c", "from conference.models import *; from django.contrib.auth.models import User; "
                        "a = Application.objects.create(user=User.objects.get(username='dmitry_s'), event=Event.objects.get(pk=3), "
                        "status=Status.objects.get(name='завершено'), room='Малый зал', payment='Банковская карта'); print('PK', a.pk)")
    pk = int(re.search(r"PK (\d+)", out).group(1))
    r = post(dmitry, "/applications/%d/review/" % pk, {"rating": 100, "text": "Оценка сто, должна отклониться"})
    add("F-19", "отзыв с оценкой 100", "отказ (200 с ошибкой)", r.status_code == 200, str(r.status_code))
    r = guest.get(BASE + "/events/3/")
    add("F-20", "оценка вне 1-5 не попадает на страницу", "нет «Оценка сто»", "Оценка сто" not in r.text, "есть на странице" if "Оценка сто" in r.text else "нет")

    # служебное
    r = guest.get(BASE + "/favicon.ico")
    add("F-21", "значок сайта /favicon.ico", "200", r.status_code == 200, str(r.status_code))
    r = anna.get(BASE + "/register/", allow_redirects=False)
    add("F-22", "вошедший участник открывает регистрацию", "302 на главную", r.status_code == 302, str(r.status_code))
    r = anna.get(BASE + "/login/", allow_redirects=False)
    add("F-23", "вошедший участник открывает страницу входа", "302 на главную", r.status_code == 302, str(r.status_code))
    r = guest.get(BASE + "/events/999/")
    add("F-24", "несуществующее мероприятие", "404", r.status_code == 404, str(r.status_code))
    r = guest.get(BASE + "/")
    h = r.headers
    add("F-25", "заголовки безопасности", "X-Frame-Options и nosniff есть", h.get("X-Frame-Options") == "DENY" and h.get("X-Content-Type-Options") == "nosniff", "XFO=%s nosniff=%s" % (h.get("X-Frame-Options"), h.get("X-Content-Type-Options")))
    m = re.search(r"<title>(.*?)</title>", guest.get(BASE + "/events/4/").text)
    add("F-26", "заголовок вкладки страницы мероприятия", "название мероприятия", m and "Python" in m.group(1), m.group(1) if m else "нет")


if __name__ == "__main__":
    portal = Portal()
    portal.start()
    try:
        run(portal)
    finally:
        portal.stop()
    print("%-5s %-46s %-36s %-26s %s" % ("ID", "Что проверяем", "Ожидание", "Получили", "Статус"))
    for r in rows:
        print("%-5s %-46s %-36s %-26s %s" % r)
    bad = [r for r in rows if r[-1] != "Пройдена"]
    print("Всего проверок: %d, пройдено: %d, не пройдено: %d" % (len(rows), len(rows) - len(bad), len(bad)))
    for r in bad:
        print("Не пройдена:", r[0], r[1])
    sys.exit(1 if bad else 0)
