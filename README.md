# Description

ISANLP is a Python 3 library that encompasses several open-source natural language processing tools for English and Russian and provides a framework for running them locally as a single pipeline or in a distributed environment via RPC. It also provides an easy to deploy docker container inemo/isanlp for starting various types of workers.

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
from isanlp import ProcessorRemote
ppl = ProcessorRemote(host = 'localhost', port = 33333, pipeline_name = '')

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

To be included:
1. Russian semantic role labeler (SRL) based on FrameBank.
2. English/Russian advanced neural network named entity recognition.
3. English/Russian sentiment analysis.
4. English/Russian anaphora resolution.

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
                       ['text],
                       {'entities' : 'entities'})])

text_ru = 'Мама мыла раму.'
annotations = ppl(text_ru)
```

The pipeline contains a list of processors -- objects that perform separate language processing tasks. The result of the pipeline execution is a dictionary of "facets" -- different types of annotations extracted from the text by processors. The dictionary of annotations is stored inside the pipeline and filled up by processors. Processors get their input parameters from the annotation dictionary and save results into the dictionary. 

The prarameters of processors are specified in a tuple during pipeline construction:
```PipelineCommon((<ProcObject>(), <list of input parameters>, <dictionary of output results>), ...) ```

You also should specify the label, which would be used to save your results in a pipeline annotation dictionary. If you do not provide a name for a result annotation it would be dropped from further processing. Processors can overwrite annotations aquired from other processors. To avoid overwriting just drop the result annotations.

Pipelines also can include other pipelines and remote processors:

```python
ppl = PipelineCommon([(ProcessorRemote(host = 'some host', port = 8207),
                      ['text'],
                      {'tokens' : 'tokens',
                       'sentences' : 'sentences',
                       'lemma' : 'lemma',
                       'postag' : 'postag',
                       'morph' : 'morph'}),
                     (ProcessorSyntaxNetRemote(host = 'other host', port = 7678),
                      ['sentences'],
                      {'syntax_dep_tree' : 'syntax_dep_tree'})])
```

Conditional execution: TBD:


## Data structures
TBD:

## Docker worker

The library provides a docker container inemo/isanlp that contains all required packages and models to run a natural language pipeline. You can invoke RPC server (gRPC) with a default pipeline using the following command:

``` docker run --rm -p 3333:3333 inemo/isanlp ```

You can also run a custom processor insed the container using the simple command:

``` docker run --rm -p 3333:3333 -v <custom module dir>:/src/custom_modules \ 
           <some repo>/isanlp /start.py \
           -m <custom module> \
           -a <pipeline object>
```