# Сохранённая конфигурация SOAR

[Раздел SOAR](README.md)

Я сохранил настройки прокси, исполнителя Cortex и заготовку Compose. Ниже описал их фактическое содержимое.

## Контейнеры и сети

В Compose я зафиксировал имя проекта `soar-core` и восемь сервисов.

| Сервис             | Образ                                                  | Сети                                              |
| ------------------ | ------------------------------------------------------ | ------------------------------------------------- |
| `nginx`            | `nginx:1.27-alpine`                                    | `frontend`                                        |
| `thehive`          | `strangebee/thehive:5.7.3`                             | `frontend`, `backend`, `shuffle_swarm_executions` |
| `cortex`           | `thehiveproject/cortex:4.0.1`                          | `frontend`, `backend`, `shuffle_swarm_executions` |
| `cassandra`        | `cassandra:4.1`                                        | `backend`                                         |
| `elasticsearch`    | `docker.elastic.co/elasticsearch/elasticsearch:8.17.4` | `backend`                                         |
| `shuffle-backend`  | `ghcr.io/shuffle/shuffle-backend:latest`               | `frontend`, `shuffle`, `shuffle_swarm_executions` |
| `shuffle-frontend` | `ghcr.io/shuffle/shuffle-frontend:latest`              | `frontend`, `shuffle`                             |
| `shuffle-orborus`  | `ghcr.io/shuffle/shuffle-orborus:latest`               | `shuffle`, `shuffle_swarm_executions`             |

В `frontend` и `shuffle` использовал тип `bridge`. Сеть `backend` объявил внутренней (`internal: true`). Сеть исполнения Shuffle объявил как `overlay` с `attachable: true`; при повторной сборке нужно подготовить Docker Swarm и проверить фактическое имя сети, к которой подключаются исполнители.

На хост в этой заготовке опубликовал только порты Nginx — 80 и 443. Порты TheHive 9000 и Cortex 9001 указал через `expose`; публикации через `ports` для них нет. Для каждого сервиса указал `restart: unless-stopped`. 

## Границы сохранённого комплекта

В заготовку я не включил OpenSearch и параметры подключения TheHive к Cassandra и Elasticsearch. Том `shuffle_database` объявил, но ни к одному сервису не подключил.

Из переменных `.env.example` в Compose использую только `CORTEX_SECRET`. Остальные оставил как заглушки для настройки интеграций; заполнение этих значений само по себе не настраивает сервисы. В Nginx локальные имена записаны непосредственно в конфигурации.

## Nginx

В `nginx/nginx.conf` я сохранил отдельные виртуальные хосты:

| Маршрут                                 | Куда передаю запрос          |
| --------------------------------------- | ---------------------------- |
| HTTPS `thehive.soar.local`              | `http://thehive:9000`        |
| HTTPS `cortex.soar.local`               | `http://cortex:9001`         |
| HTTPS `shuffle.soar.local`              | `http://shuffle-frontend:80` |
| HTTP `shuffle.soar.local/api/v1/hooks/` | `http://shuffle-frontend:80` |

Для HTTPS использовал `/etc/nginx/certs/nginx.crt` и `/etc/nginx/certs/nginx.key`. В Compose подключил конфигурацию и каталог сертификатов только для чтения. Сертификат и закрытый ключ нужно подготовить отдельно; их нет в примере переменных окружения.

Для интерфейсов сохранил заголовки `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto` и поддержку обновления соединения. Тайм-ауты TheHive и Cortex задал по 600 секунд, Shuffle — по 300 секунд. 

HTTP-маршрут webhook выделил, чтобы обращения Wazuh не уходили в перенаправление на HTTPS. В сохранённом блоке нет отдельного списка разрешённых адресов источника. Ограничение доступа и шифрование этого участка оставил в доработках.

## Исполнение заданий Cortex

В `cortex/application.conf` я указал:

```hocon
job.runners = [docker]
job.directory = "/tmp/cortex-jobs"
job.dockerDirectory = "/tmp/cortex-jobs"
```

В Compose включил привилегированный режим Cortex, запуск Docker через `--start-docker`, каталог заданий `/tmp/cortex-jobs` и адрес Elasticsearch `http://elasticsearch:9200`. Для заданий и данных вложенного Docker выделил отдельные тома.

