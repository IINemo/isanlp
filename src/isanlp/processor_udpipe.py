import sys
from ufal.udpipe import Model, Pipeline, ProcessingError
from . import annotation as ann
from .converter_conll_ud_v1 import ConverterConllUDV1


class ProcessorUDPipe:
    """Wrapper around UDPipe - Trainable pipeline library.

    Performs:
    1. Tokenization.
    2. Tagging.
    3. Lemmatizing.
    4. Parsing.
    """

    def __init__(self, model_path):
        self.model = Model.load(model_path)
        if not self.model:
            sys.stderr.write('Cannot load model from file "%s"\n' % model_path)

        self.pipeline = Pipeline(self.model, 'generic_tokenizer', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
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
            6. syntax_dep_tree - list of lists of objects WordSynt that represent a dependency tree
        """
        processed = self.pipeline.process(text, self.error)
        if self.error.occurred():
            sys.stderr.write('An error occurred when calling ProcessorUDPipe: ')
            sys.stderr.write(self.error.message)
            return sys.stderr.write('\n')

        annotation = self.converter_conll(processed)

        annotation['sentences'] = self.sentence_split(annotation['form'])
        annotation['tokens'] = self.get_tokens(text, annotation['form'])

        return annotation


    def get_tokens(self, text, form_annotation):
        """Performs sentence splitting.

        Args:
            form_annotation(list): list of lists of forms of words.

        Returns:
            List of objects Token.
        """

        ann_tokens = list()
        for sent in form_annotation:
            for form in sent:
                begin = text.find(form)
                end = begin + len(form)
                ann_tokens.append(ann.Token(text=form, begin=begin, end=end))
        return ann_tokens

    def sentence_split(self, form_annotation):
        """Performs sentence splitting.

        Args:
            form_annotation(list): list of lists of forms of words.

        Returns:
            List of objects Sentence.
        """
        sentences = list()
        start = 0
        for sent in form_annotation:
            sentences.append(ann.Sentence(begin=start, end=start + len(sent)))
            start += len(sent)
        return sentences
