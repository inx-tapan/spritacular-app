# Spritacular
Core code repo for Spritacular - TLE Citizen Science web application 

## Technical Specifications
  
* Programming language: Python
  * Version: 3.8
  * <https://www.python.org/downloads/release/python-380/>

* Frameworks &
  * Django 3.2
    * <https://www.djangoproject.com/>
  * Django Rest Framework
    * <https://www.django-rest-framework.org/>
* Database: PostgresSQL(can configure in settings.py)

## Installation

Install python 3.8.0\
Install git\
clone this repo to local folder and change directory to Project path

```properties
git clone https://github.com/EnsembleGovServices/spritacular-app.git

cd app
```

Install,Create, activate Virtual Environment

```properties
#install
pip install virtualenv
#create virtual environment
virtualenv <nameof virtualenv eg:venv>
#activation[take name as venv]
cd venv
cd Scripts
activate
#back to app folder project path where requirements.txt file is there
```

Install requirements.txt

```properties
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

Create one .env file to root folder of the project and update following values
```properties
SECRET_KEY=xx
DEBUG=True

EMAIL_PORT=xx
EMAIL_USE_TLS=xx
EMAIL_HOST_USER=xx
EMAIL_HOST_PASSWORD=xx

ACCESS_TOKEN_LIFETIME=xx
REFRESH_TOKEN_LIFETIME=xx

AUTH_HEADER_TYPES=xx


ALGORITHM=xx

DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME=xx


DB_ENGINE=xx
DB_NAME=xx
DB_USER=xx
DB_PASSWORD=xx
DB_HOST=xx
DB_PORT=xx



AWS_ACCESS_KEY_ID=xx
AWS_SECRET_ACCESS_KEY=xx
DEFAULT_FILE_STORAGE=xx
AWS_STORAGE_BUCKET_NAME=xx
AWS_S3_REGION_NAME=xx
AWS_DEFAULT_ACL=xx
AWS_S3_CUSTOM_DOMAIN=xx


FRONTEND_URL=xx

CACHE_BACKEND=xx
CACHE_LOCATION=xx
CLIENT_CLASS=xx
KEY_PREFIX=xx


CELERY_BROKER_URL=xx
CELERY_RESULT_BACKEND=xx

FCM_SERVER_KEY=xx

PATH_TO_FCM_CREDS=xx
```

Run

```properties
# for running django server
python manage.py runserver

# make sure your redis server is running before starting celery
# for running celery worker open new terminal activate virtual environment & run
celery -A spritacular worker -l INFO
```

Access the application using follwing URL

* <http://localhost:8000/>

Access the Admin dashboard using follwing URL

* <http://localhost:8000/admin/>

Access the APIs using following URL

* <http://localhost:8000/api/>