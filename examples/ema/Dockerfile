FROM python:3.9

RUN apt-get update 
RUN apt-get install cmake build-essential python-dev -y

WORKDIR /app

COPY ema.py /app/ema.py

RUN pip install pip --upgrade
RUN pip install foreverbull

ENTRYPOINT [ "foreverbull", "/app/ema.py" ]