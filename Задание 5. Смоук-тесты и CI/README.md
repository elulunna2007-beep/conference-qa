# Задание 5. Смоук-тесты своего приложения и запуск в CI

Выполнила Терзи Эллия. Приложение: портал «Конференции.РФ». Тесты в `test_smoke.py`, помечены `@pytest.mark.smoke`, используют те же Page Object, что и задание 4.

## Смоук-тесты

| Тест | Сценарий |
|---|---|
| `test_home_page_shows_events` | главная открывается, в названии вкладки «Конференции.РФ», в списке 9 мероприятий |
| `test_participant_login_opens_my_applications` | участница входит, открывается «Мои заявки» с карточками |
| `test_new_user_can_apply_for_event` | новый пользователь регистрируется, подаёт заявку, видит «Заявка отправлена» и статус «новая» |
| `test_admin_moves_application_to_next_status` | администратор входит в панель и переводит заявку на следующий статус |
| `test_guest_cannot_open_admin_panel` | гость на `/manage/` попадает на страницу входа |

Запуск: `python -m pytest -m smoke --html=report.html --self-contained-html`. Результат: 5 passed за 39,9 с (`screens/01_zapusk_smoke.png`), отчёт pytest-html (`screens/02_otchet_pytest_html.png`). Отчёт открывала по http: файл по пути с кириллицей в Chrome не показывает таблицу результатов.

## CI

Файл `.github/workflows/smoke.yml` в корне репозитория запускает смоук-тесты на каждый push и pull request. Задача на ubuntu-latest: скачивает этот репозиторий и `conference-django`, ставит Python 3.12 и зависимости, выводит версии Chrome и Django, запускает `pytest -m smoke` (портал тесты поднимают сами, Chrome на ubuntu-latest уже стоит, драйвер скачивает Selenium Manager) и сохраняет `report.html` как артефакт.

Первый прогон: https://github.com/elulunna2007-beep/conference-qa/actions/runs/42128585948. Статус success, Chrome 156, Django 6.1.3, `5 passed, 11 deselected in 19.73s`. Остальные 11 тестов репозитория (задание 4 и тест, который падает по заданию) в смоук-набор не входят.

Снимок страницы прогона: screens/03_github_actions_zelenyj_progon.png.
