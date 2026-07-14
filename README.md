# Alt-Poet

This is an application to edit alt-text (for Project Gutenberg). This backend
pairs with the [alt-text-editor](https://github.com/gutenbergtools/alt-text-editor)
front-end.

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

8. start the development server

   `./src/manage.py runserver`

The django app is now accessible on port 8000, eg:
* http://127.0.0.1:8000/admin/
* http://127.0.0.1:8000/api/documents/

### Production with Apache

For a production environment, use [uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/)
behind Apache. The following instructions and associated service files
(`altpoet.service` & `uwsgi.ini`) assume that the repo is checked out under
`/var/lib/altpoet/altpoet` and that the database and pipenv virtualenv have
been set up per the instructions above.

This also assumes that you've checked out [alt-text-editor](https://github.com/gutenbergtools/alt-text-editor)
in `/var/lib/altpoet/alt-text-editor` and built it per its instructions. The Apache
config below is going to serve `/var/lib/altpoet/alt-text-editor/alt-text-react-app/dist`
at `/alttexteditor`.

Start by updating your `local_settings.py` file (or creating one, per the above)
and setting `ALLOWED_HOSTS` for the domain and a location to serve the static
files (currently only used for the django admin interface):

```python
DEBUG = False
ALLOWED_HOSTS = ["altpoet.pglaf.org"]
CORS_ALLOWED_ORIGINS = ["https://altpoet.pglaf.org"]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
STATIC_ROOT = "/var/lib/altpoet/static"
```

Now collect the static files to be served by Apache:

```bash
pipenv shell
./src/manage.py collectstatic
```

Finally wire up and start all the services as root:

1. Install the systemd service and start it:

   ```bash
   ln -s /var/lib/altpoet/altpoet/altpoet.service /etc/systemd/system/altpoet.service
   systemctl daemon-reload
   systemctl start altpoet
   ```

   You should now be able to curl the website:

   `curl http://localhost:8001/`

2. Enable the `proxy` and `proxy_uwsgi` Apache modules:

   ```bash
   a2enmod proxy
   a2enmod proxy_uwsgi
   ```

3. Create a site in Apache that will proxy your VirtualHost, like
   `/etc/apache2/sites-available/altpoet.conf`:

   ```
   <VirtualHost altpoet.pglaf.org:80>
       ServerName altpoet.pglaf.org
       ErrorLog /var/log/apache2/altpoet-error.log
       CustomLog /var/log/apache2/altpoet-access.log common

       DocumentRoot /var/lib/altpoet
       <Directory "/var/lib/altpoet">
           AllowOverride None
           Require all granted
       </Directory>

       Alias /alttexteditor /var/lib/altpoet/alt-text-editor/alt-text-react-app/dist

       ProxyPass /alttexteditor !
       ProxyPass /static/ !
       ProxyPass "/" "uwsgi://localhost:8001/"
   </VirtualHost>
   ```

   Then enable it and reload Apache:

   ```bash
   a2ensite altpoet
   systemctl reload apache2
   ```

You may need to adjust the uwsgi configuration in `/var/lib/altpoet/altpoet/uwsgi.ini`
based on your server workload.
