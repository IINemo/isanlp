FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04


RUN apt-get update && apt-get install -y git curl wget zlib1g-dev libssl-dev \
                                         build-essential libsqlite3-dev \
                                         libicu-dev locales libbz2-dev

ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}

# Python 3.6
RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
ENV PYENV_ROOT /root/.pyenv
ENV PATH /root/.pyenv/shims:/root/.pyenv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN pyenv install 3.6.8
RUN pyenv global 3.6.8

# Locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
        dpkg-reconfigure --frontend=noninteractive locales

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Python libraries

RUN pip install --upgrade pip && pip install grpcio protobuf
RUN pip install --upgrade torch tensorflow-gpu
COPY isanlp /src/isanlp
RUN pip install /src/isanlp/

COPY start.py /

ENV PYTHONPATH=/src/custom_modules

COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
