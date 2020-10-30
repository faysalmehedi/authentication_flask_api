### AUTHENTICATION - FLASK API

## Endpoints:
```
- /api/v1/users (Get all users from DB. Only admin can do that.)
- /api/v1/user/<email> (Get indivisual user from DB by email(unique). Only admin can do that.)
- /api/v1/create_user (Anyone can create user.)
- /api/v1/update/<email> (Update existing indivisual user in DB by email(unique). Only admin can do that.)
- /api/v1/delete/<email> (Delete indivisual user from DB by email(unique). Only admin can do that.)
- /api/v1/login (Registered user can login.)
```

## JSON DATA FORMAT
```
{
    "name": "Faysal",
    "email": "fmehedi1992@gmail.com",
    "password": "testpass123",
    "admin": "True"
}

```
## JSON WEB TOKEN SAMPLE
```
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSIsImV4cCI6MTYwNDA2MTU3OX0.fn5ZaswE4VmbbtuIP76caIXKDcpGlD467YA1BiV4ilA"
}
```

## For Database Running

```
$ sudo docker-compose up -d
$ sudo docker-compose ps
```

## For application Running

```
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirments.txt
$ python app.py db init
$ python app.py db migrate
$ python app.py db upgrade
$ python app.py runserver -h 0.0.0.0
```