FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y apt-utils git curl wget zlib1g-dev libssl-dev \
                                         build-essential libsqlite3-dev \
                                         libicu-dev locales libbz2-dev


RUN pip install --upgrade pip && pip install grpcio protobuf
COPY isanlp /src/isanlp
RUN pip install /src/isanlp/

COPY start.py /

ENV PYTHONPATH=/src/custom_modules

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
