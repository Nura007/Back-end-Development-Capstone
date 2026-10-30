FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput && mkdir -p /data && chown -R 1001:0 /app /data && chmod -R g=u /app /data
USER 1001
ENV DJANGO_DEBUG=0 DJANGO_DB_PATH=/data/db.sqlite3
EXPOSE 8000
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["waitress-serve", "--listen=0.0.0.0:8000", "django_concert.wsgi:application"]

