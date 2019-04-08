FROM inemo/isanlp_base

MAINTAINER Nemo

# Install common
RUN apt-get update && apt-get install -y default-jre default-jdk

# Installing Mystem
RUN pip install git+https://github.com/nlpub/pymystem3
RUN python -c "import pymystem3 ; pymystem3.Mystem()"

# NLTK
RUN pip install nltk
RUN python -c "import nltk;\
               nltk.download('averaged_perceptron_tagger');\
               nltk.download('wordnet')"

# Polyglot
RUN pip install numpy pyicu pycld2 morfessor polyglot
RUN polyglot download embeddings2.ru && \
    polyglot download embeddings2.en && \
    polyglot download ner2.ru && \
    polyglot download ner2.en

# MaltParser
RUN cd /src/ && wget http://maltparser.org/dist/maltparser-1.9.1.tar.gz 
RUN cd /src/ && tar -xf maltparser-1.9.1.tar.gz


CMD [ "python", "/start.py", "-m", "isanlp.pipeline_default", "-a", "create_pipeline" ]
