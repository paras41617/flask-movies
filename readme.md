
# Movies CRUD API with Flask and SQLAlchemy

As a user, I want to be able to manage a collection of movies through a RESTful API. This
includes being able to create, read, update, and delete movies. I also want to ensure that
proper validation is in place for movie fields, and that only authenticated users can perform
certain actions. Furthermore, I want to be able to search for movies by title or description,
sort movies by release date and price, and filter movies by genre, director, and release year.

## Features

- Validation
- Authentication
- Permissions
- Pagination and Filtering
- Searching
- Sorting

## Tech Stack

**Server:** Flask, SQLAlchemy, MySQL

## Run Locally

Clone the project

```bash
  git clone https://github.com/paras41617/flask-movies.git
```

Go to the project directory

```bash
  cd flask-movies
```

Install dependencies

```bash
  pip install requirements.txt
```

Create a database in mysql ( open mysq in your terminal by going to the username and then entering password)

```bash
  create database flaskdb
```

Create a .env file with reference from env_example and put values in .evn

```bash
  put secret key
  database uri (add username and password)
```

Start the server

```bash
  python run.py
```

### API Documentation

Explore the API using Swagger UI:

[![Swagger UI](https://img.shields.io/badge/Swagger-UI-orange?style=flat&logo=swagger)](https://paras41617.github.io/flask-movies/)
