FROM python:3.10

RUN apt update && apt upgrade -y && apt install nano

COPY *.whl /

RUN pip3 install *.whl

WORKDIR /code

CMD python3