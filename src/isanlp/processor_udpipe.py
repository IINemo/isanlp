import sys
from ufal.udpipe import Model, Pipeline, ProcessingError
from .converter_conll_ud_v1 import ConverterConllUDV1


class ProcessorUDPipe:
    """Wrapper around UDPipe - Trainable pipeline library.

    Performs:
    1. Tokenization.
    2. Tagging.
    3. Lemmatizing.
    4. Parsing.
    """

    def __init__(self, model_path, tagger=True, parser=True):
        self.model = Model.load(model_path)
        if not self.model:
            sys.stderr.write('Cannot load model from file "%s"\n' % model_path)

        self.tagger = Pipeline.DEFAULT if tagger else Pipeline.NONE
        self.parser = Pipeline.DEFAULT if parser else Pipeline.NONE
        self.pipeline = Pipeline(self.model, 'generic_tokenizer', self.tagger, self.parser, 'conllu')
        self.error = ProcessingError()
        self.converter_conll = ConverterConllUDV1()

    def __call__(self, text):
        """Performs tokenization, tagging, lemmatizing and parsing.

        Args:
            text(str): text.

        Returns:
            Dictionary that contains:
            1. tokens - list of objects Token.
            2. sentences - list of objects Sentence.
            3. lemma - list of lists of strings that represent lemmas of words.
            4. postag - list of lists of strings that represent postags of words.
            5. morph - list of lists of strings that represent morphological features.
            6. syntax_dep_tree - list of lists of objects WordSynt that represent a dependency tree.
        """
        processed = self.pipeline.process(text, self.error)
        if self.error.occurred():
            sys.stderr.write('An error occurred when calling ProcessorUDPipe: ')
            sys.stderr.write(self.error.message)
            return sys.stderr.write('\n')

        annotation = self.converter_conll(processed)

        if self.tagger == Pipeline.NONE:
            for key in ('lemma', 'postag'):
                annotation.pop(key, None)

        if self.parser == Pipeline.NONE:
            for key in ('synt_dep_tree', 'postag'):
                annotation.pop(key, None)
        
        for sent_lemma in annotation['lemma']:
            for i in range(len(sent_lemma)):
                sent_lemma[i] = sent_lemma[i].lower()

        annotation['sentences'] = self.converter_conll.sentence_split(annotation['form'])
        annotation['tokens'] = self.converter_conll.get_tokens(text, annotation['form'])

        return annotation
