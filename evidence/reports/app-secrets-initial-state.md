# app-secrets: исходное состояние

[Каталог проверок](README.md)

Я сохранил замер от **28 мая 2026 года, 20:57:26 UTC**, выполненный до усиления Ubuntu. В нём зафиксированы Ubuntu 24.04, ядро `6.8.0-117-generic`, установленный Docker и наличие Wazuh Agent. Auditd в этой проверке не работал либо отсутствовал — исходный вывод не различает эти два состояния.

## Выдержка из замера

```text
Host:                 app-secrets
Role/Group Context:   docker_hosts, ubuntu_servers
Date/Time:            2026-05-28T20:57:26Z
OS Distribution:      Ubuntu 24.04
Kernel Version:       6.8.0-117-generic
IP Address:           192.168.31.210

[BASE SECURITY COMPONENT CHECK]
SSH Config Exists:    True
Auditd Service:       NOT RUNNING/MISSING
Firewall (UFW):       Installed

[DOCKER ECOSYSTEM]
Docker Engine:        Installed

[SECURITY AGENTS STATUS]
Wazuh-Manager:        Not installed
Wazuh-Agent:          Installed
```

Я перенёс выбранные строки из текстового замера `precheck/app-secrets_precheck.txt`. Это историческое состояние ОС; статус пакета или службы не описывает автоматически сервис внутри контейнера. По этому выводу я не вычисляю оценку SCA.

[Проверка после настройки](app-secrets-hardened-state.md) · [Замеры SCA](sca-results.md)
