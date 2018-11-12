[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/IINemo/isanlp_srl_framebank/blob/master/LICENSE)
![Python 3.6](https://img.shields.io/badge/python-3.6-green.svg)

# Description

ISANLP is a Python 3 library that encompasses several open-source natural language processing tools for English and Russian and provides a framework for running them locally as a single pipeline or in a distributed environment via RPC. It also provides an easy to deploy docker container inemo/isanlp for starting various types of workers.
Version 0.0.5

# Getting started

## Installation

### 1. Installing dependencies
In the basic use case, the library depends only on grpc library.
``` pip install grpcio ```

### 2. Installing the library
``` pip install git+https://github.com/IINemo/isanlp.git ```

### 3. (Optional) Starting docker container with installed dependencies and models
``` docker run -ti --rm -p 3333:3333 inemo/isanlp ```

# Basic usage
```python
from isanlp.processor_remote import ProcessorRemote
ppl = ProcessorRemote(host='localhost', port=3333, pipeline_name='default')

text_ru = 'Мама мыла раму'
annotations = ppl(text_ru)
print(annotations)
```

# Included components

Current:
1. NLTK (English tokenizing, sentence splitting, lemmatizing, postagging; Russian tokenizing, sentence splitting).
2. MyStem (Russian morphological analysis, postagging, lemmatizing).
3. Polyglot (Language detection, English/Russian tokening, sentence splitting, named entity recognition).
4. SyntaxNet (English/Russian dependency parsing in Universal dependencies format, postagging, morphological analysis).
5. Postag converters.
6. MaltParser: dependency parsing (for now without runtime and models).
7. MaltParser CoNLL-2008: dependency parsing with a runtime and a model for English as a standalone docker container.
8. Deep-SRL parser as a standalone docker container (semantic role labeling for English).
9. Russian semantic role labeler (SRL) based on FrameBank and neural network models.

To be included:
1. English/Russian advanced neural network named entity recognition.
2. English/Russian sentiment analysis.
3. English/Russian anaphora resolution.

# Usage

## Common usage

The most common usage consists in constructing a pipeline of processors with ```PipelineCommon``` class. For example, the following pipeline processes texts in Russian and solves sequentially the following tasks: tokenization, sentence splitting, postagging, syntax parsing, and named entity recognition.

```python
from isanlp.pipeline_common import PipelineCommon
from isanlp.ru.processor_tokenizer_ru import ProcessorTokenizerRu
from isanlp.processor_sentence_splitter import ProcessorSentenceSplitter
from isanlp.ru.processor_mystem import ProcessorMystem
from isanlp.processor_polyglot import ProcessorPolyglot
from isanlp.processor_syntaxnet_remote import ProcessorSyntaxNetRemote

ppl = PipelineCommon([(ProcessorPolyglot().detect_language,
                       ['text'],
                       {0: 'lang'}),
                      (ProcessorTokenizerRu(), 
                       ['text'], 
                       {0 : 'tokens'}),
                      (ProcessorSentenceSplitter(), 
                       ['tokens'], 
                       {0 : 'sentences'}),
                      (ProcessorMystem(), 
                       ['tokens', 'sentences'], 
                       {'lemma' : 'lemma', 
                        'postag' : 'postag'}),
                      (ProcessorSyntaxNetRemote('localhost', 8207), 
                       ['tokens', 'sentences'],
                       {'syntax_dep_tree' : 'syntax_dep_tree'}),
                      (ProcessorPolyglot(), 
                       ['text'],
                       {'entities' : 'entities'})])

text_ru = 'Мама мыла раму.'
annotations = ppl(text_ru)
```

The pipeline contains a list of processors -- objects that perform separate language processing tasks. The result of the pipeline execution is a dictionary of "facets" -- different types of annotations extracted from the text by processors. The dictionary of annotations is stored inside the pipeline and filled up by processors. Processors get their input parameters from the annotation dictionary and save results into the dictionary. 

The parameters of processors are specified in a tuple during pipeline construction:
```PipelineCommon((<ProcObject>(), <list of input parameters>, <dictionary of output results>), ...) ```

You also should specify the label, which would be used to save your results in a pipeline annotation dictionary. If you do not provide a name for a result annotation it would be dropped from further processing. Processors can overwrite annotations aquired from other processors. To avoid overwriting just drop the result annotations.

Pipelines also can include other pipelines and remote processors:

```python
ppl = PipelineCommon([(ProcessorRemote(host='some host', port=8207),
                      ['text'],
                      {'tokens' : 'tokens',
                       'sentences' : 'sentences',
                       'lemma' : 'lemma',
                       'postag' : 'postag',
                       'morph' : 'morph'}),
                     (ProcessorSyntaxNetRemote(host='other host', port=7678),
                      ['sentences'],
                      {'syntax_dep_tree' : 'syntax_dep_tree'})])
```

Conditional execution: TBD:


## Data structures

The pipeline returns the results in a dictionary with keys that were provided in the parameters of processors. If processor returns None, results are ommited.
Available keys & values structures:
  * `'lang'`(str) -- ISO code of detected language.
  * `'lemma'`(list) -- list of lists of string lemma annotations for each sentence. The first list corresponds to sentences, the second corresponds to annotations inside a sentence.
  * `'morph'`(list) -- list of lists of dictionary objects where the keys are the morphological features available for the current word. 
  * `'postag'`(list) -- list of lists of string POS tags for each sentence.
  * `'sentences'`(list) -- list of `isanlp.annotation.Sentence` objects. Each Sentence contains:
    * begin(int) -- number of the first token in a sentence.
    * end(int) -- number of the last token in a sentence + 1.
  * `'syntax_dep_tree'`(list) -- list of lists of `isanlp.annotation.WordSynt` objects. WordSynt objects mean nodes in syntax dependency tree and have two members:
    * parent(int) -- number of the parent token.
    * link_name(str) -- name of the link between this word and it's parent.
  * `'tokens'`(list) -- list of `isanlp.annotation.Token` objects. Each Token contains:
    * text(str) -- as represented in text.
  

## Docker worker

The library provides a docker container inemo/isanlp that contains all required packages and models to run a natural language pipeline. You can invoke RPC server (gRPC) with a default pipeline using the following command:

``` docker run --rm -p 3333:3333 inemo/isanlp ```

You can also run a custom processor instead the container using the simple command:

``` docker run --rm -p 3333:3333 -v <custom module dir>:/src/custom_modules \ 
           <some repo>/isanlp /start.py \
           -m <custom module> \
           -a <pipeline object>
```
# Additional modules for IsaNLP.

The IsaNLP library provides several core routines, processors, and models that do not need many dependencies. However, the IsaNLP framework is significantly broader. It encompasses many other easy-to-use packages for various types of NLP. Currently they include:
1. [isanlp_srl_framebank](https://github.com/IINemo/isanlp_srl_framebank) -- the neural-based SRL parser for Russian based on well-known [FrameBank](https://github.com/olesar/framebank) corpus. The package provides the python 3 library for final users, trained models (Shelmanov and Devyatkin), a docker container inemo/isanlp_srl_framebank with ready-to-use NLP service, and a playground for training new deep learning models (jupyter notebook).
2. [isanlp_deep_srl](https://github.com/IINemo/isanlp_deep_srl) -- the docker container [inemo/isanlp_deep_srl](https://hub.docker.com/r/inemo/isanlp_deep_srl/) with ready-to-use SRL service for English. The parser and models is created by [Deep SRL project](https://github.com/luheng/deep_srl) and adopted for IsaNLP framework.
3. [isanlp_parser_conll2008](https://github.com/IINemo/isanlp_parser_conll2008/) -- the docker container [inemo/isanlp_parser_conll2008](https://hub.docker.com/r/inemo/isanlp_parser_conll2008/) with ready-to-use dependency parsing service for English. The parser is based on MaltParser and CONLL-2008/2009 syntactic annotation (semantically rich). The model is developed by [Surdenau et al.](http://www.surdeanu.info/mihai/ensemble/)
4. [docker-syntaxnet](https://github.com/IINemo/docker-syntaxnet) -- the docker containers with Google's [SyntaxNet](https://github.com/tensorflow/models/tree/master/research/syntaxnet) for [English](https://hub.docker.com/r/inemo/syntaxnet_eng/), [Russian](https://hub.docker.com/r/inemo/syntaxnet_rus/), and [Italian](https://hub.docker.com/r/inemo/syntaxnet_ita/). The containers provides easy-to-use gRPC service for dependency parsing, pos-tagging, and morphology analysis.

# Roadmap:
1. <s>Publish SRL parser for Russian.</s> [published](https://github.com/IINemo/isanlp_srl_framebankmark).
2. <s>UDPipe support.</s> Implemented.
3. Expand documentation.
4. Automatic tests.
5. Sentiment analysis for English and Russian.
6. Anaphora resolution for English and Russian.
7. Spacy wrapper.
