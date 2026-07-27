FROM python:3.14-slim

WORKDIR /opt/healthchecks

COPY requirements.txt /opt/healthchecks/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /opt/healthchecks/

ENV PYTHONUNBUFFERED=1
ENV DEBUG=True

RUN mkdir -p /data

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_test_data && python manage.py runserver 0.0.0.0:8000"]
