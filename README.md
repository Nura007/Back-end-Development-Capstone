# Back-end-Development-Capstone

Django integration application for the IBM Back-End Development capstone.
Based on [IBM's official starter](https://github.com/ibm-developer-skills-network/sfvih-Back-end-Development-Capstone).

The application displays the Djirection homepage, songs with Bootstrap lyrics
dialogs, one photo per page, concerts and RSVP choices. It includes signup,
login, POST logout, and Django administration. Sample content is fictional and
comes from the course starter, except the two clearly fictional demo concerts.

## Local setup

Use Python 3.14. Start Pictures on port 8080 and Songs on port 5000, with its
MongoDB database seeded. Activate a virtual environment and run:

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/ and visit /songs/, /photos/, /concerts/, /admin/.
The seed command adds fictional concerts and does not create an administrator.
Create your own admin account interactively.

SONGS_API_URL and PICTURES_API_URL override the two service base URLs.
Requests have a five-second timeout. Unavailable services produce a visible
503 response rather than fabricated fallback content.

Concert and RSVP data are stored in SQLite. Song and Photo are unmanaged
models describing microservice resources; Django does not duplicate those
resources into SQLite. Migration 0001 creates Concert and ConcertAttending;
0002 records Photo and Song in Django's migration state.

## Verification

```sh
python manage.py check
python manage.py test --verbosity 2
python manage.py makemigrations --check --dry-run
```

Six tests passed locally: public/admin pages, signup/login/logout, protected RSVP
updates, escaped song lyrics, service-outage handling, and photo pagination.
The local homepage also opened successfully in a browser. Screenshot collection
is pending; cloud deployments are not yet verified.

## Configuration

- DJANGO_DEBUG: 1 for local development, 0 for deployment.
- DJANGO_SECRET_KEY: required when debug is disabled. Use an independently
  generated value supplied through a Kubernetes Secret. Setting it locally
  also preserves sessions across restarts.
- DJANGO_ALLOWED_HOSTS: comma-separated hosts without schemes.
- DJANGO_CSRF_TRUSTED_ORIGINS: comma-separated HTTPS origins.
- DJANGO_DB_PATH: SQLite path; default db.sqlite3, container /data/db.sqlite3.
- SONGS_API_URL and PICTURES_API_URL: reachable service base URLs.

The development default permits only localhost addresses. Deployment uses
Waitress and WhiteNoise to serve the application and its static assets.

## Container and Kubernetes lab

```sh
docker build -t "$DJANGO_IMAGE" .
docker push "$DJANGO_IMAGE"
```

Set DJANGO_IMAGE to your actual pushed image, APP_HOST to the lab's assigned
browser hostname, and SONGS_API_URL/PICTURES_API_URL to your deployed services.
Create a Secret named django-secret with a DJANGO_SECRET_KEY entry, without
putting its value in source control. In the Linux course terminal:

```sh
envsubst < deployment.yml > deployment.rendered.yml
kubectl apply -f deployment.rendered.yml
kubectl rollout status deployment/djangoserver
kubectl exec deployment/djangoserver -- python manage.py seed_demo
kubectl exec -it deployment/djangoserver -- python manage.py createsuperuser
```

Configure the course's route/ingress to point at the djangoserver service.
The single-replica deployment uses a persistent volume for SQLite and Recreate
strategy. Your cluster must have a suitable default storage class. For scaling,
replace SQLite with a shared database before increasing replicas.

Collect the real build/apply output and browser screenshots after deployment.
For Task 29, the detailed question asks to demonstrate successful admin login.
No cloud success logs or cloud screenshots are included in this repository.

