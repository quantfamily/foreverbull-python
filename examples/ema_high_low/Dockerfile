FROM python:3.9

WORKDIR /app

COPY ema.py /app/ema.py

RUN pip install pip --upgrade
RUN pip install foreverbull

ENTRYPOINT [ "foreverbull", "/app/ema.py" ]