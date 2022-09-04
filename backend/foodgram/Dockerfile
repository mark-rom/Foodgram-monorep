FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./ /app/

RUN python3 manage.py collectstatic

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]