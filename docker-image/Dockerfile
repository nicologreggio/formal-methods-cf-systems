FROM python:3.10

RUN apt update && apt upgrade -y && apt install nano

COPY *.whl /

RUN pip3 install *.whl

COPY NuSMV* /opt

WORKDIR /opt

RUN tar -xvf NuSMV*

RUN echo "PATH=$PATH:/opt/NuSMV-2.6.0-Linux/bin/ \n\
bind 'set completion-ignore-case on' \n\
alias ..='cd ..' \n\
" >> ~/.bashrc

WORKDIR /code

CMD python3