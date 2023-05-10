# VK Джуниор/Friends

Проект является тестовым заданиeм для стажировки VK Джуниор. 

Проект Friends представляет собой сервис, который сможет позволить пользователям дружить в сети. 

### Что можно делать вместе с Friends:
- Создать нового пользователя.
- Отправлять заявки в друзья другим пользователям. Если 2 пользователя отправили друг другу заявки в друзья - заявки автоматом принимаются.
- Принимать/Отклонять заявки в друзья от других пользователей.
- Посмотреть список отклоненных заявок.
- Посмотреть список друзей.
- Удалять других пользователей из списка друзей.
- Посмотреть статус дружбы с другими пользователями: входящая заявка, исходящая заявка, друзья, none.

### Технологии:
- Python 3.8
- Django 3.2.9
- Django REST Framework 3.13.1
- django-friendship
- Djoser + JWT

### Начало работы:

Клонирование репозитория:

`git clone git@github.com:hatecodinglovemoney/vk_junior_backend.git`

Создание и активация виртуального окружения:

    Linux:~$ python3 -m venv venv
    Win, Mac:~$ python -m venv venv

	source venv/bin/activate

Установка requirements:

     Linux:~$ pip3 install -r requirements.txt
     Win, Mac:~$ pip install -r requirements.txt

Создание миграций:

    Linux:~$ python3 manage.py migrate
    Win, Mac:~$ python manage.py migrate

Запуск проекта:

	Linux:~$ python3 manage.py runserver
	Win, Mac:~$ python manage.py runserver
  
### Регистрация пользователя и получение токена:

Регистрация:

	POST http://127.0.0.1:8000/auth/users/
    
    {
      "username":"user_1",
      "password":"password_user_1"
	}
 Получение токена:
 
 	POST http://127.0.0.1:8000/auth/jwt/create/
    
    {
      "username":"user_1",
      "password":"password_user_1"
	}
 

### Примеры запросов:

Отправить заявку в друзья. В теле запроса передать username пользователя, для которого предназначается заявка:

 	POST http://127.0.0.1:8000/friends/add_friend/
    
    {
      "to_user":"user_2"
	}

Отклонить заявку в друзья. В теле запроса передать id заявки, которую нужно отклонить:

 	POST http://127.0.0.1:8000/friends/reject_request/
    
    {
      "id":"1"
	}

Принять заявку в друзья. В теле запроса передать id заявки, которую нужно принять:

	POST http://127.0.0.1:8000/friends/accept_request/
    
    {
      "id":"1"
	}

Удалить из друзей. В теле запроса передать username пользователя, которого нужно удалить из друзй:

	POST http://127.0.0.1:8000/friends/remove_friend/
    
    {
      "to_user":"user_2"
	}
    
Список исходящих заявок:

	GET http://127.0.0.1:8000/friends/sent_requests/
    
Список входящих заявок:

	GET http://127.0.0.1:8000/friends/requests/
    
Список отклоненных заявок:

	GET http://127.0.0.1:8000/friends/rejected_requests/
    
Список друзей:

	GET http://127.0.0.1:8000/friends/
    
Получить статус дружбы. В теле запроса передать username пользователя, статус дружбы с которым нужно получить:

	GET http://127.0.0.1:8000/friends/get_status/
    
    {
      "username":"user_2"
	}	

### Автор:

Ната Бутрина
