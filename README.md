# Alt-Poet

This is an application to edit alt-text (for Project Gutenberg)

## Installation

### PostgreSQL

https://www.postgresql.org/download/

Alt-Poet development is using version 14.

create a database called `altpoet`
```CREATE DATABASE altpoet
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
    ```

### Python

Alt-Poet development is using version 3.9
PyEnv can be used to manage multiple python versions on one machine.
You'll want to install Pip and Pipenv (or a flavor of environment management that accepts pipfiles)
https://pipenv.pypa.io/en/latest/installation.html

### altpoet

`git clone https://github.com/gutenbergtools/altpoet.git`

create a python env in the new altpoet directory:
`pipenv shell`

install packages from pipfile
`pipenv install`

to use your local postgres instance, change the settings in 
`src/altpoet/settings/sample_local_settings.py`
or leave them alone to use sqlite.

https://docs.djangoproject.com/en/5.1/topics/install/
`django-admin migrate`

now, make yourself a superuser
`django-admin createsuperuser --username=joe --email=joe@example.com`

load the sample data
`django-admin load_pgimgdata data/sample_alt_data.csv `
or get a load of PG images data from https://www.gutenberg.org/cache/epub/feeds/img_data.csv.gz
then load it with 
`django-admin load_images [path to unzipped data file] `
start the server
`django-admin rundata`

look at
`http://127.0.0.1:8000/admin/`
`http://127.0.0.1:8000/api/documents/

`

