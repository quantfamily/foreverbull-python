FROM python:3.9

RUN apt update && apt install cmake -y

COPY dist/foreverbull-0.0.7.tar.gz foreverbull.tar.gz
COPY examples/with_parameters/example.py example.py
RUN pip install pip --upgrade
RUN pip install setuptools
RUN pip install foreverbull.tar.gz 

CMD python -m foreverbull example.py