# Docker
## Основные команды

### Образы
Создание образа     
`docker build -t <имя-образа> .`

Показать список всех образов        
`docker images`

Удалить образ       
`docker rmi <имя-образа>`

### Контейнеры
Создание контейнера     
`docker run <имя-образа>`

Параметры:

- `-d` - запуск в фоновом режиме
- `-p 1234:5432` - прокидывание портов
- `--name my-container` - задание имени контейнера
- `-v /my/dir:/container/dir` - прокидывание вольюмов
- `--network my-network>` - запуск контейнера внутри Docker сети

Показать список всех запущенных контейнеров        
`docker ps`

Показать список всех контейнеров        
`docker ps -a`

Удалить контейнер       
`docker rm <имя-контейнера>`

Удалить запущенный контейнер        
`docker rm -f <имя-контейнера>`

### Docker сети
Создать Docker сеть     
`docker network create <имя-сети>`

## Docker Compose
Создание образов
```
docker compose build
```

Поднятие всех контейнеров       
`docker compose up`

Поднятие всех контейнеров + сборка образов      
`docker compose up --build`

Поднятие всех контейнеров с кастомным названием файла       
`docker compose -f docker-compose-custom.yml up`

## Команды для проекта
### Создание Docker сети
`docker network create myNetwork`

### База данных
```
docker run --name training_db \
    -p 6432:5432 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=Qaz_wsx_123 \
    -e POSTGRES_DB=training \
    --network=myNetwork \
    -d postgres
```

### Redis
```
docker run --name training_cache \
    -p 7379:6379 \
    --network=myNetwork \
    -d redis
```