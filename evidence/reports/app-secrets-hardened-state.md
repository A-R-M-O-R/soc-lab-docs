# app-secrets: состояние после усиления

[Каталог проверок](README.md)

Я сохранил проверку Auditd, Wazuh Agent, Docker, SSH и UFW после доработок. В исходном файле дата отсутствует; точную дату этого замера не указываю.

## Службы и маршрутизация

```text
Host: app-secrets
Distribution: Ubuntu 24.04

[COMPLIANCE SUMMARY]
SSH Config Exists:       PASS
Auditd Installed & Run:  PASS
Wazuh Agent Active:      PASS
Docker Active:           PASS

[NETWORK / DOCKER NOTE]
IP Forwarding:
net.ipv4.ip_forward = 1
```

Я оставил `net.ipv4.ip_forward = 1` для контейнерной сети. В проверке Auditd, Wazuh Agent и Docker отмечены работающими. Проверка служб не заменяет оценку SCA.

## SSH и UFW

```text
[SSH EFFECTIVE SETTINGS]
maxauthtries 4
clientaliveinterval 300
clientalivecountmax 0
pubkeyauthentication yes
passwordauthentication yes
kbdinteractiveauthentication yes
x11forwarding no
allowtcpforwarding no
allowusers ansible
allowusers eldan
allowusers socadmin
allowgroups ssh-allowed
allowgroups sudo
allowgroups ssh-allowed

[UFW STATUS]
Status: active
Logging: on (low)
Default: deny (incoming), deny (outgoing), deny (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp (OpenSSH)           ALLOW IN    Anywhere                  
Anywhere on lo             ALLOW IN    Anywhere                  
Anywhere                   DENY IN     127.0.0.0/8               
22/tcp                     ALLOW IN    192.168.31.0/24            # SSH from lab LAN
8080/tcp                   ALLOW IN    192.168.31.0/24            # App HTTP from LAN
8443/tcp                   ALLOW IN    192.168.31.0/24            # App HTTPS from LAN
22/tcp (OpenSSH (v6))      ALLOW IN    Anywhere (v6)             
Anywhere (v6) on lo        ALLOW IN    Anywhere (v6)             
Anywhere (v6)              DENY IN     ::1                       

Anywhere                   ALLOW OUT   Anywhere on lo            
53/tcp                     ALLOW OUT   Anywhere                   # DNS TCP
53/udp                     ALLOW OUT   Anywhere                   # DNS UDP
80/tcp                     ALLOW OUT   Anywhere                   # HTTP outbound
123/udp                    ALLOW OUT   Anywhere                   # NTP outbound
443/tcp                    ALLOW OUT   Anywhere                   # HTTPS outbound
192.168.31.227 1514/tcp    ALLOW OUT   Anywhere                   # Wazuh agent events
192.168.31.227 1515/tcp    ALLOW OUT   Anywhere                   # Wazuh agent enrollment
22/tcp                     ALLOW OUT   Anywhere                   # Essential outbound git-ssh
Anywhere (v6)              ALLOW OUT   Anywhere (v6) on lo       
53/tcp (v6)                ALLOW OUT   Anywhere (v6)              # DNS TCP
53/udp (v6)                ALLOW OUT   Anywhere (v6)              # DNS UDP
80/tcp (v6)                ALLOW OUT   Anywhere (v6)              # HTTP outbound
123/udp (v6)               ALLOW OUT   Anywhere (v6)              # NTP outbound
443/tcp (v6)               ALLOW OUT   Anywhere (v6)              # HTTPS outbound
22/tcp (v6)                ALLOW OUT   Anywhere (v6)              # Essential outbound git-ssh

Anywhere                   ALLOW FWD   172.16.0.0/12              # Docker routed traffic
```

Я сохранил парольный доступ SSH, отключил X11 и TCP forwarding. В UFW зафиксированы запреты по умолчанию и явные разрешения для приложения, Wazuh и служебного исходящего трафика.

В этом же выводе есть широкое разрешение `OpenSSH` от любых адресов для IPv4 и IPv6. Поэтому по данному замеру я не заявляю ограничение SSH только лабораторной подсетью: рядом присутствует более узкое правило, но широкое разрешение остаётся. Пересмотр этих правил включил в доработки.

Я перенёс разделы из `postcheck/app-secrets_postcheck_after_followup_2.txt`; повторяющийся подробный вывод служб не включал. Значение SCA сохранил отдельно в [таблице измерений](sca-results.md).
