# Alt-Poet

This is an application to edit alt-text (for Project Gutenberg)

## Installation

### PostgreSQL

https://www.postgresql.org/download/

Alt-Poet development is using version 14.

create a database called `altpoet`
```sql
CREATE USER altpoet
    WITH
    PASSWORD 'somepassword';

CREATE DATABASE altpoet
    WITH
    OWNER = altpoet
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
```

### Python

Alt-Poet development is using python version 3.9.
PyEnv can be used to manage multiple python versions on one machine.
You'll want to install Pip and Pipenv (or a flavor of environment management that accepts pipfiles)
https://pipenv.pypa.io/en/latest/installation.html

### altpoet

1. Clone the repo

   `git clone https://github.com/gutenbergtools/altpoet.git`

2. create the logs directory inside the checkout

   ```bash
   cd altpoet
   mkdir logs
   ```

3. Create the virtualenv and install packages from pipfile

   `pipenv sync`

4. by default, altpoet will use a sqlite database. To use your local postgres
   instance, create `src/altpoet/settings/local_settings.py` with contents like:

   ```python
   DATABASES = {
       'default': {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": "altpoet",
           "USER": "altpoet",
           "PASSWORD": "somepassword",
           "HOST": "127.0.0.1",
           "PORT": "5432",
       }
   }
   ```

5. Apply the database schema / upgrades (see also https://docs.djangoproject.com/en/5.1/topics/install/)

   `./src/manage.py migrate`

6. Create a superuser

   `./src/manage.py createsuperuser --username=joe --email=joe@example.com`

7. load the sample data

   `./src/manage.py load_pgimgdata data/sample_alt_data.csv`

   or get a load of PG images data from https://www.gutenberg.org/cache/epub/feeds/img_data.csv.gz then load it with

    `./src/manage.py load_images [path to unzipped data file] `

8. start the server

   `./src/manage.py runserver`

The app is now accessible on port 8000, eg:
* http://127.0.0.1:8000/admin/
* http://127.0.0.1:8000/api/documents/

