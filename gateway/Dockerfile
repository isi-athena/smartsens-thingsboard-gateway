FROM python:3.9

ENV TB_BROKER="smartsens.tb"
ENV TB_PORT="1883"
ENV SOCK_ADDRESS="0.0.0.0"
ENV SOCK_PORT="9999"
ENV SOCK_THREADING="true"

WORKDIR /app
COPY . /app

RUN  chmod 755 run.sh &&\
     python -m pip install -r requirements.txt

CMD /app/run.sh