https://github.com/TvojaMamaLama/Auth_sprint_1

участники aleshnikov9, p.schislyaev, dimavakulenko2 Что делали?Решали проблемы бизнеса)

Запуск проекта:
- docker-compose up -d

Есть один метод grpc с помощью client.py можно в него сходить
Он ждет два параметра, token - access token пользователя и url - эндпоинт на который пользователь пришел. В ответ получаем статус 401(токен протух или невалидный) 403(Недостаточно прав) или 200(ОК пускайте)
- python client.py

Документация:
- localhost:8000/swagger-ui/

Тесты:
- в файле .env надо заменить хост redis и postgres на localhost
- docker-compose -f dev.yml -d
- python main.py
- python -m pytest tests/ (предыдущая команда не должна прерываться)

Настройка google Oauth2:
-Для настройки oauth2 на стороне google необходимо выполнить действия в соответсвие с официальной
документацией https://developers.google.com/identity/protocols/oauth2
-Необходимо указать redirect_uri=http://127.0.0.1:8000/api/oauth/google_callback/ , хост может быть изменен

Changelog в issues
