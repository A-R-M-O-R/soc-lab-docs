# Windows: исходная проверка состояния

[Каталог проверок](README.md)

Я сохранил исходный замер от **21 июня 2026 года, 20:05:31 UTC+03:00**. В нём работали WinRM, Defender, Firewall, Wazuh Agent и Sysmon; RDP был отключён.

## Выдержка из замера

```text
Host:                 WIN10-ENDPOINT
Inventory Host:       win10-endpoint
Role/Group Context:   windows, windows_workstations
Date/Time:            2026-06-21T20:05:31+03:00

[SYSTEM]
OS Name:              Microsoft Windows 10 Enterprise LTSC
OS Version:           10.0.17763
OS Build:             17763
Architecture:         Not collected in original precheck
Domain/Workgroup:     Not collected in original precheck
Primary IPv4:         192.168.31.236
All IPv4:             192.168.31.236

[REMOTE ACCESS]
WinRM Service:        Running
SSH Service:          Not collected in original precheck
RDP Status:           Disabled

[BASE SECURITY SERVICES]
Windows Event Log:    Running
Windows Defender:     Running
Windows Firewall:     Running
Security Center:      Not collected in original precheck

[SECURITY AGENTS]
Wazuh Agent Service:  Running
Wazuh Config Exists:  True
Wazuh Config Path:    C:\Program Files (x86)\ossec-agent\ossec.conf
Sysmon Service:       Running
Sysmon EXE Exists:    True
```

Я использовал нормализованный текстовый отчёт `precheck/win10-endpoint_windows_state_precheck.txt`. В исходном замере не собирались подробные параметры Defender, правила ASR, настройки журналирования и состав каналов Wazuh. Поэтому их отсутствие в этом файле не трактую как отключённую защиту.

Названия групп в историческом выводе относятся к тому запуску; состав опубликованного inventory описал в [каталоге Ansible](../../ansible/README.md).

[Проверки после настройки](windows-configured-state.md) · [Замеры SCA](sca-results.md)
