FROM python:3

RUN mkdir /FLASK_MYSQL_RESAPI

WORKDIR /FLASK_MYSQL_RESAPI

COPY requirements.txt /FLASK_MYSQL_RESAPI

RUN pip install -r requirements.txt

COPY . /FLASK_MYSQL_RESAPI

EXPOSE 5000

CMD [ "python", "src/app.py" ]