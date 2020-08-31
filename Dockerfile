FROM python:3.8

RUN pip install pipenv

COPY Pipfile /opt/emporium/
COPY Pipfile.lock /opt/emporium/
WORKDIR /opt/emporium/

RUN pipenv install

COPY . /opt/emporium/

RUN pipenv run make collectstatic

EXPOSE 8000

CMD pipenv run gunicorn --chdir emporium --bind [::]:8000 emporium.wsgi
