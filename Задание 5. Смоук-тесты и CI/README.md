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

Готов файл GitHub Actions `smoke.yml`: ubuntu-latest, Python 3.12, скачивает оба репозитория, ставит зависимости, запускает `pytest -m smoke` (Chrome на ubuntu-latest уже стоит, драйвер скачивает Selenium Manager), сохраняет отчёт как артефакт.

**Запуск в GitHub Actions не проверялся.** Токену, которым я выкладывала репозитории, не хватает права `workflow`, поэтому GitHub не принимает файл из `.github/workflows`. Файл лежит здесь же как `smoke.yml`, а также в локальной ветке `ci` (путь `.github/workflows/smoke.yml`). Чтобы включить CI: добавить файл в `.github/workflows` через веб-интерфейс GitHub («Add file») или отправить ветку токеном с правом `workflow`. Зелёного прогона у меня нет, и я его не выдумываю.
