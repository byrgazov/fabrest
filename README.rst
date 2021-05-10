
Задание
-------

Тестовое задание – дополнительный способ для нас убедиться в вашей квалификации и понять, какого рода задачи
вы выполняете эффективнее всего.

Расчётное время на выполнение тестового задания: 3-4 часа, время засекается нестрого. Приступить к выполнению
тестового задания можно в любое удобное для вас время.

У текущего тестового задания есть только общее описание требований, конкретные детали реализации остаются на
усмотрение разработчика.

Задача: спроектировать и разработать API для системы опросов пользователей.

Функционал для администратора системы:

- авторизация в системе (регистрация не нужна)
- добавление/изменение/удаление опросов.
  Атрибуты опроса: название, дата старта, дата окончания, описание.
  После создания поле "дата старта" у опроса менять нельзя.
- добавление/изменение/удаление вопросов в опросе.
  Атрибуты вопросов: текст вопроса, тип вопроса (ответ текстом, ответ с выбором одного варианта,
  ответ с выбором нескольких вариантов)

Функционал для пользователей системы:

- получение списка активных опросов
- прохождение опроса: опросы можно проходить анонимно, в качестве идентификатора пользователя в API передаётся числовой ID,
  по которому сохраняются ответы пользователя на вопросы; один пользователь может участвовать в любом количестве опросов
- получение пройденных пользователем опросов с детализацией по ответам (что выбрано) по ID уникальному пользователя

Использовать следующие технологии: Django 2.2.10, Django REST framework.

Результат выполнения задачи:
- исходный код приложения в github (только на github, публичный репозиторий)
- инструкция по разворачиванию приложения (в docker или локально)
- документация по API


Установка
---------

.. code:: bash

    $ virtualenv --python=python3 .venv
    $ .venv/bin/pip install -UI pip setuptools zc.buildout
    $ .venv/bin/buildout

.. code:: bash

    $ bin/fabrest migrate
    $ bin/fabrest createsuperuserwithpassword --username=admin --password=admin --email=admin@example.org
    $ bin/fabrest loaddata fixtures.yaml
    $ bin/fabrest runserver

Использование
-------------

.. code:: bash

    $ bin/http -a admin:admin POST http://localhost:8000/api/pollings/ title=title1 description=description1 start_time="2021-05-01T11:00Z" duration="1 days"
    $ bin/http -a admin:admin POST http://localhost:8000/api/pollings/1/questions/ polling=1 description=text1
    $ bin/http -a admin:admin POST http://localhost:8000/api/pollings/3/questions/ title=title1 description=description1
    $ bin/http -a admin:admin POST http://localhost:8000/api/pollings/3/questions/ title=title2 description=description2 has_choices=yes
    $ bin/http -a admin:admin POST http://localhost:8000/api/pollings/3/questions/ title=title3 description=description3 has_choices=yes multiple=no

.. code:: bash

    $ bin/http -a admin:admin POST http://localhost:8000/api/pollings/ title=title1 description=description1 start_time="1970-01-01T11:00Z" duration="1 days"
    {
        "created_by": "admin",
        "description": "description1",
        "duration": "1 00:00:00",
        "id": 3,
        "questions": "http://localhost:8000/api/pollings/3/questions/",
        "start_time": "1970-01-01T11:00:00Z",
        "title": "title1",
        "updated_by": "admin"
    }

.. code:: bash

    $ bin/http -a admin:admin POST http://localhost:8000/api/pollings/3/questions/ title=title1 description=description1
    {
        "description": "description1",
        "id": 5,
        "order": 10
    }

.. code:: bash

    $ bin/http POST http://localhost:8000/api/questions/5/answers/ guest_id=1 text=text
    {
        "non_field_errors": [
            "Polling has already ended."
        ]
    }


Комментарии
-----------

Валидация моделей была сделана в `clean`, но этот метод используется только в формах, так что пришлось портить
`create` и `update` в сериализациях.

`fabrest.polls.views.PollingViewSet` и `fabrest.polls.serializers.PollingSerializer` сделаны, как это задумывалось
разработчиками DRF (нет), но дальше я решил сделать по своему о чём успел 10 раз пожалеть.

Не хочет DRF без выкрутасов работать, см. `fabrest.polls.serializers.ChoicesField` и ко. DRF не только не реализует
запись ManyToMany-полей, но и всячески препятствует разработчику сделать это самостоятельно.

У DRF отвратительная обработка ошибок, например, см. `fabrest.polls.serializers.QuestionAnswerSerializer`.

Сейчас, если бы я вновь делал подобное приложение, то отказался бы от валидации в моделях, при этом, в
сопровождающей документации нужно указать на тот факт, что реляционная БД не выполняет одну из своих
основных функций, т.е. не обеспечивает целостность данных.
