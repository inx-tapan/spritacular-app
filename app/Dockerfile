FROM python:3.8

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN pip install virtualenv
RUN virtualenv sprite
CMD source sprite/bin/activate
RUN pip install -r requirements.txt