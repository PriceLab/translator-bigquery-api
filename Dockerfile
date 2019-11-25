FROM tiangolo/uwsgi-nginx-flask:flask-python2.7

COPY ./app /app

# uwsgi-nginx-flask specified WORKDIR /app
RUN pip install -r requirements.txt
