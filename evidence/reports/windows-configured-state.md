# Windows: два замера после настройки

[Каталог проверок](README.md)

Я сохранил два замера от **23 июня 2026 года**. Они показывают параметры защиты и изменение состояния агента в течение вечера.

| Параметр | 22:54:33 UTC+03:00 | 23:47:40 UTC+03:00 |
| --- | --- | --- |
| Wazuh Agent | Работает | Остановлен |
| Sysmon | Работает | Работает |
| Defender и Firewall | Работают | Работают |
| WinRM и SSH | Работают | Работают |
| RDP | Отключён | Отключён |
| Аудит командной строки, модулей и блоков PowerShell | Включён | Включён |
| Журналы Firewall | Один путь для профилей | Отдельные файлы для трёх профилей |

## Замер в 22:54

```text
Date/Time:            2026-06-23T22:54:33+03:00

[REMOTE ACCESS]
WinRM Service:        Running
SSH Service:          Running
RDP Status:           Disabled

[BASE SECURITY SERVICES]
Windows Event Log:    Running
Windows Defender:     Running
Windows Firewall:     Running
Security Center:      Running

[SECURITY AGENTS]
Wazuh Agent Service:  Running
Wazuh Config Exists:  True
Wazuh Config Path:    C:\Program Files (x86)\ossec-agent\ossec.conf
Sysmon Service:       Running
Sysmon EXE Exists:    True

[DEFENDER STATE]
Defender Status:      AntivirusEnabled=True, RealTime=True, Behavior=True, IOAV=True, NIS=True
Defender Preferences: PUA=1, MAPS=2, Samples=1, NetworkProtection=1, ControlledFolderAccess=2, CloudBlockLevel=2
ASR Rules:            01443614-cd74-433a-b99e-2ecdc07bfc25=2; 26190899-1602-49e8-8b27-eb1d0a1ce869=2; 3b576869-a4ec-4529-8536-b80a7769e899=1; 56a863a9-875e-4185-98a7-b882c64b5ce5=1; 5beb7efe-fd9a-4556-801d-275e5ffc04cc=1; 75668c1f-73b5-4cf0-bb93-3ecf5cb7cc84=2; 7674ba52-37eb-4a4f-a9a1-f0f9a1619a2c=1; 92e97fa1-2edf-4476-bdd6-9dd0b4dddc7b=1; 9e6c4e1f-7d60-472f-ba1a-a39ef669e4b2=1; b2b3f03d-6a65-4f7b-a9c7-1c7ef74a9ba4=1; be9ba2d9-53ea-4cdc-84e5-9b1eeee46550=1; c1db55ab-c21a-4637-bb3f-a12568109d35=1; d1e49aac-8f56-4280-b9ba-993a6d77406c=2; d3e037e1-3eb8-44c8-a917-57927947596d=1; d4f940ab-401b-4efc-aadc-ad5f3c50688a=2

[WINDOWS FIREWALL]
Profiles:
Domain: Enabled=True, DefaultInbound=Block, DefaultOutbound=Allow, LogBlocked=True, LogFile=%systemroot%\system32\LogFiles\Firewall\pfirewall.log
Private: Enabled=True, DefaultInbound=Block, DefaultOutbound=Allow, LogBlocked=True, LogFile=%systemroot%\system32\LogFiles\Firewall\pfirewall.log
Public: Enabled=True, DefaultInbound=Block, DefaultOutbound=Allow, LogBlocked=True, LogFile=%systemroot%\system32\LogFiles\Firewall\pfirewall.log
SOC-LAB Rule Count:   12

[AUDIT AND TELEMETRY]
Command Line Audit:   Enabled
PS ScriptBlock Log:   Enabled
PS Module Logging:    Enabled
Sysmon Channel:       Present
Defender Channel:     Present
PowerShell Channel:   Present
WinRM Channel:        Present
OpenSSH Channel:      Present

[WAZUH COLLECTION CHECK]
Collects Sysmon:      Yes
Collects Defender:    Yes
Top Manager FIM:      Yes
SCA Block Present:    Yes
SCA Scan On Start:    Yes
```

## Повторный замер в 23:47

```text
Date/Time:            2026-06-23T23:47:40+03:00

[SECURITY AGENTS]
Wazuh Agent Service:  Stopped
Wazuh Config Exists:  True
Wazuh Config Path:    C:\Program Files (x86)\ossec-agent\ossec.conf
Sysmon Service:       Running
Sysmon EXE Exists:    True

[WINDOWS FIREWALL]
Profiles:
Domain: Enabled=True, DefaultInbound=Block, DefaultOutbound=Allow, LogBlocked=True, LogFile=%SystemRoot%\System32\LogFiles\Firewall\domainfw.log
Private: Enabled=True, DefaultInbound=Block, DefaultOutbound=Allow, LogBlocked=True, LogFile=%SystemRoot%\System32\LogFiles\Firewall\privatefw.log
Public: Enabled=True, DefaultInbound=Block, DefaultOutbound=Allow, LogBlocked=True, LogFile=%SystemRoot%\System32\LogFiles\Firewall\publicfw.log
SOC-LAB Rule Count:   12
```

## Как я использую эти результаты

Я зафиксировал настройку журналирования, наличие Sysmon и конфигурации сбора событий Wazuh. По двум замерам не делаю вывод о непрерывной доставке событий: в позднем замере Wazuh Agent остановлен. Контроль доступности агентов включил в дальнейшие улучшения.

Поля `Collects Sysmon`, `Collects Defender` и проверки FIM описывают найденную конфигурацию. Факт поступления событий в Wazuh показываю отдельно на [скриншотах](../README.md). Числовые значения настроек Defender и ASR сохранил без переинтерпретации; эти строки сами по себе не являются тестом блокировки атаки.

Я объединил выдержки двух замеров от 23 июня 2026 года: в 22:54:33 и 23:47:40 UTC+03:00. Список локальных администраторов и учебные каталоги пользователя в эту выдержку не включал. Оценку SCA сохранил отдельно: [35% → 45%](sca-results.md).
