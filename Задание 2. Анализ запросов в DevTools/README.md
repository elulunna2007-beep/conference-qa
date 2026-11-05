# Задание 2. Анализ HTTP-запроса и ответа в DevTools

Выполнила Терзи Эллия. Chrome 156, вкладка «Сеть» (Network) в DevTools. Разобрала два запроса: страницу документации Django (настоящий сайт) и вход на моём портале.

## Запрос 1. GET страницы документации Django

Адрес https://docs.djangoproject.com/en/6.1/, открыла в Chrome с открытыми DevTools, фильтр «Все», первая строка списка (`01_docs_spisok_zaprosov.png`).

| Что | Значение |
|---|---|
| Метод | GET |
| Код ответа | 200 OK |
| Адрес сервера | 151.101.1.55:443 (HTTPS) |
| Тело запроса | нет (у GET его не бывает) |
| Тело ответа | HTML-страница, 10,7 кБ по сети, внутри разметка с `<head>` и ссылками на стили (`03_docs_otvet_html.png`) |
| Всего на странице | 20 запросов, 567 кБ ресурсов, загрузка завершена за 112 мс, DOMContentLoaded 92 мс |

Заголовки запроса (`02b_docs_zagolovki_zaprosa.png`): `Accept: text/html,...`, `Accept-Encoding: gzip, deflate, br, zstd` (браузер умеет сжатие), `Accept-Language: ru,en-US`, `Cookie: theme=auto`, `Sec-Fetch-Dest: document`, `Sec-Fetch-Mode: navigate`, `Upgrade-Insecure-Requests: 1`, `User-Agent: ... Chrome/156.0.0.0`.

Заголовки ответа (`02_docs_zagolovki_zaprosa_i_otveta.png`):

| Заголовок | Значение | Что значит |
|---|---|---|
| Content-Type | text/html; charset=utf-8 | тип и кодировка тела |
| Content-Encoding | gzip | тело сжато, поэтому 10,5 кБ вместо большего |
| Cache-Control | max-age=300 | страницу можно держать в кеше 5 минут |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload | год только по HTTPS |
| X-Content-Type-Options | nosniff | браузер не угадывает тип файла |
| X-Frame-Options | SAMEORIGIN | сайт нельзя вставить во фрейм чужого сайта |
| Referrer-Policy | same-origin | адрес страницы уходит только на свой сайт |
| X-Cache, Via | HIT, 1.1 varnish | ответ отдал кеш-сервер |

## Запрос 2. POST входа на портале

Форма входа http://localhost:8101/login/. Обычная отправка формы уводит на другую страницу и запрос пропадает из списка, поэтому отправила тот же запрос из консоли браузера через `fetch` с параметром `redirect: 'manual'`, токен CSRF взяла со страницы (`04_portal_spisok_zaprosov.png`).

| Что | Значение |
|---|---|
| Метод и адрес | POST http://localhost:8101/login/ |
| Код ответа | 302 Found, `Location: /` (перенаправление на главную) |
| Время | 2,91 с |
| Тело запроса | поля формы: `csrfmiddlewaretoken`, `username` (anna_k), `password` (учебный пароль) (`07_portal_post_login_nagruzka.png`) |
| Тело ответа | пустое, `Content-Length: 0` |

Заголовки запроса (`06_portal_post_login_zagolovki_zaprosa.png`): `Content-Type: application/x-www-form-urlencoded`, `Content-Length: 124`, `Cookie: csrftoken=...`, `Origin` и `Referer` на тот же адрес.

Заголовки ответа (`05_portal_post_login_zagolovki_otveta.png`): `Set-Cookie: sessionid=...; HttpOnly; Max-Age=7200; Path=/; SameSite=Lax` и `Set-Cookie: csrftoken=...; SameSite=Lax`, `Cache-Control: max-age=0, no-cache, no-store, must-revalidate, private`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `Server: WSGIServer/0.2 CPython/3.12.10`.

Для сравнения GET поиска `/events/?q=Python` (`08_portal_get_poisk_zagolovki.png`): 200 OK, `Content-Type: text/html; charset=utf-8`, тело запроса нет, параметр поиска в адресе.

## Что полезно для тестирования

- Вход идёт медленно, 2,91 с: пароль проверяется хешем PBKDF2 с 1,5 млн итераций (число видно в базе, `$1500000$`). Это защита от подбора, но автотестам с входом нужно ждать дольше обычного, поэтому в них только явные ожидания и таймаут 10 с.
- Сессионная cookie с `HttpOnly` и `SameSite=Lax`, значит скрипт страницы её не прочитает: защита работает.
- Пароль идёт в теле запроса открытым текстом. На локальном адресе это нормально, на настоящем сайте нужен HTTPS, как у документации Django (там заголовок Strict-Transport-Security).
- Заголовок `Server: WSGIServer/0.2 CPython/3.12.10` раскрывает версию Python. Это встроенный сервер разработки, на настоящем сервере его заменит другой, поэтому ошибкой не считаю.
- В консоли при открытии страниц портала видна ошибка 404 для `favicon.ico`: нашла так ошибку BR-06 (Задание 1).
