# Скриншоты и результаты проверок

[Главная страница](../README.md) · [Результаты лаборатории](../docs/06-results-and-evidence.md)

Я собрал здесь 23 скриншота с этапами настройки, проверками и результатами. Каждый файл находится внутри этого репозитория. По подписи можно понять, что я проверял; по ссылке — открыть изображение в полном размере.

## Каталог

| Изображение                                                                       | Что я проверял                                                                                                            |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [SCA приложения — 73%](screenshots/app-secrets-sca-73.png)                        | получил 133 пройденные проверки, 48 непройденных и одну неприменимую.                                                   |
| [SCA SOAR — 73%](screenshots/soar-ir-sca-73.png)                                  | проверил SCA SOAR после подготовки узла.                                                                                |
| [SCA Windows — 35%](screenshots/windows-sca-35.png)                               | использовал этот замер как состояние до последующих доработок.                                                          |
| [SCA Windows — 45%](screenshots/windows-sca-45.png)                               | После доработок я получил 179 пройденных проверок.                                                                        |
| [Обнаружение локального подбора пароля](screenshots/windows-rule-100301.png)      | нашёл событие правила 100301 для win10-endpoint.                                                                        |
| [SSH Alert и комментарий](screenshots/ssh-thehive-comment.png)                    | получил оповещение правила 5758 и комментарий о DShield.                                                                |
| [Семь анализаторов Cortex](screenshots/cortex-seven-analyzers.png)                | сохранил раннюю историю успешных заданий, включая Shodan до истечения ключа.                                            |
| [Политики PowerShell](screenshots/windows-powershell-policies.png)                | включил журналирование модулей, блоков сценариев и транскрипцию PowerShell.                                             |
| [Процессы Windows в Discover](screenshots/windows-process-events.png)             | проверяю поступление событий whoami, netstat и net user. На раннем снимке агент использует прежнее имя.                 |
| [Изменения файлов UFW](screenshots/linux-fim-events.png)                          | наблюдаю события FIM для конфигурации UFW. Значение SCA ниже относится к промежуточному этапу.                          |
| [Доступность управления Windows](screenshots/windows-management-connectivity.png) | проверяю порты 5985 и 22; другие показанные соединения завершаются по тайм-ауту.                                        |
| [Проверка API с Windows](screenshots/secret-service-health.png)                   | получаю успешный ответ /api/v1/health от приложения.                                                                    |
| [Клонирование SOAR](screenshots/virtualbox-soar-clone.png)                        | создаю SOAR из защищённой VM app-secrets. В списке VirtualBox видны и другие ранние учебные VM.                         |
| [Отчёт DShield](screenshots/thehive-dshield-report.png)                           | открываю аналитический отчёт по тестовому IP 8.8.8.8. Это проверка интеграции, а не утверждение о вредоносности адреса. |
| [Тестовый Case](screenshots/thehive-core-case.png)                                | проверяю работу ядра TheHive с тестовым Case.                                                                           |
| [Результаты обогащения](screenshots/thehive-analyzer-observables.png)             | проверяю метки и результаты анализаторов для тестовых IP, URL, домена и хеша.                                           |
| [Тест API TheHive](screenshots/thehive-api-test.png)                              | проверяю создание оповещения через API перед основной интеграцией.                                                      |
| [Динамические observables](screenshots/thehive-dynamic-observables.png)           | проверяю передачу тестовых значений пользователя, имени узла и IP через Shuffle.                                        |
| [Оповещения Wazuh в TheHive](screenshots/thehive-wazuh-alerts.png)                | получаю оповещения аутентификации в TheHive.                                                                            |
| [Контекст SSH-оповещения](screenshots/ssh-observables.png)                        | передаю сервис, пользователя, имя узла и IP как отдельные observables.                                                  |
| [Исходное событие Windows](screenshots/windows-logon-event.png)                   | проверяю событие Security 4625 с типом входа 2.                                                                         |
| [Ручная блокировка Nginx](screenshots/nginx-manual-block-test.png)                | проверяю блокировку: для запроса к / получаю 403, после снятия запрета — 404.                                           |
| [Сценарий Shuffle](screenshots/shuffle-workflow.png) | Показываю структуру обработки событий в интерфейсе Shuffle. |

## Текстовые результаты

В [каталоге текстовых проверок](reports/README.md) я сохранил состояние приложения до и после усиления, исходную проверку Windows и два последующих замера. В отчётах сохранил даты и выдержки из вывода.

[Таблица замеров SCA](reports/sca-results.md) дополняет скриншоты оценок защищённости.
