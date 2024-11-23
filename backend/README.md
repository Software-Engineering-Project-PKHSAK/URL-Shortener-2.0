Steps to run the backend project

### Initial Project setup
1. sudo apt install -y     build-essential     libssl-dev     zlib1g-dev     libbz2-dev     libreadline-dev     libsqlite3-dev     wget     curl     llvm     libncurses5-dev     libncursesw5-dev     xz-utils     tk-dev     libffi-dev     liblzma-dev     python3-dev     libgdbm-dev     libnss3-dev     libssl-dev     libgdbm-compat-dev
2. pyenv install 3.10.14
3. cd backend
4.  pip install -r requirements.txt 

### Local DB setup
4. psql
```Install PostgreSQL
create database url_shortener;
\q
```
5. flask db init 
6. flask db migrate -m "initial migration"
7. flask db upgrade

### Local Flask

8. flask run

### Heroku setup

9. git remote add heroku https://git.heroku.com/url-shortener-server-api.git

### Heroku deployment
10. cd ../ && git subtree push --prefix backend heroku main
heroku run flask db upgrade

