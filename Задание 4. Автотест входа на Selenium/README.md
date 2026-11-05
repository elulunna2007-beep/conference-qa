# Задание 4. Автотест формы входа на Selenium

Выполнила Терзи Эллия. Python 3.12, pytest, Selenium 4.52, Chrome 156 (в тестах без окна, для снимков окна `QA_HEADED=1`).

## Как устроено

| Файл | Что в нём |
|---|---|
| `../pages/base_page.py` | `BasePage`: открыть адрес, найти элемент, ввести текст, клик, ждать адрес. Только явные ожидания (`WebDriverWait`), пауз `sleep` нет |
| `../pages/login_page.py` | `LoginPage`: адреса полей входа и методы `login`, `login_ok`, `error`, `validation_message` |
| `test_login.py` | сами тесты, в них нет ни одного адреса элемента: всё берётся из `LoginPage` |
| `../conftest.py` | запуск портала на временной базе, драйвер Chrome, хук: при падении теста снимок страницы сохраняется в папку `failed` |
| `../portal_server.py` | миграции, учебные данные и сервер Django на порту 8101 |

## Тесты

| Тест | Что проверяет |
|---|---|
| `test_login_ok` | верная пара: в шапке «Выйти (anna_k)», открылась главная |
| `test_wrong_password_shows_error` | неверный пароль: сообщение об ошибке, не вошла |
| `test_bad_credentials_do_not_log_in` (3 набора) | неизвестный логин, инъекция `' OR '1'='1`, логин с пробелом и неверным паролем |
| `test_empty_field_is_stopped_by_browser` (2 набора) | пустой логин и пустой пароль: у поля подсказка браузера, адрес не изменился |
| `test_logout` | выход: кнопки «Выйти» больше нет |
| `test_lockout_after_five_wrong_passwords` | после пяти неверных паролей вход закрыт, даже с верным |
| `test_logged_in_user_is_redirected_from_login_page` | вошедшего со страницы входа уводит на главную (BR-07) |
| `test_demo_failure` | нарочно падает, только для снимка; в обычный запуск не входит (`pytest -m manual`) |

## Результат

На портале до исправлений тест на BR-07 упал, остальные 9 прошли (`screens/01_zapusk_do_ispravleniy.png`: 1 failed, 9 passed). Снимок страницы в момент падения сохранил хук: `screens/02_snimok_upavshego_testa.png`. После исправления портала прошли все 10 (`screens/03_zapusk_posle_ispravleniy.png`).

Тест доказывает, что ловит ошибку: на старой версии портала он красный, на новой зелёный.

## Запуск

```
pip install -r requirements.txt
python -m pytest "Задание 4. Автотест входа на Selenium"
```
Нужен репозиторий `conference-django` рядом (см. README в корне). Прогон идёт около полутора минут: вход хеширует пароль.
