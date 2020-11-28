import sys
from ufal.udpipe import Model, Pipeline, ProcessingError
from .converter_conll_ud_v1 import ConverterConllUDV1
from .annotation_repr import CSentence


class ProcessorUDPipe:
    """Wrapper around UDPipe - Trainable pipeline library.
    Performs:
    1. Tokenization.
    2. Tagging.
    3. Lemmatizing.
    4. Parsing.
    """

    def __init__(self, model_path, tagger=True, parser=True, delay_init=False):
        self._model_path = model_path
        self._enable_tagger = tagger
        self._enable_parser = parser

        self.model = None
        if not delay_init:
            self.init()

    def init(self):
        if self.model is None:
            self.model = Model.load(self._model_path)
            if not self.model:
                sys.stderr.write('Cannot load model from file "%s"\n' % self._model_path)

            if self._enable_parser and not self._enable_tagger:
                self._enable_tagger = True
                
            self.tagger = Pipeline.DEFAULT if self._enable_tagger else Pipeline.NONE
            self.parser = Pipeline.DEFAULT if self._enable_parser else Pipeline.NONE
            self.error = ProcessingError()
            self.converter_conll = ConverterConllUDV1()

    def __call__(self, *argv):
        """Performs tokenization, tagging, lemmatizing and parsing.
        Args:
            text(str): text. OR
            tokens(list): List of Token objects.
            sentences(list): List of Sentence objects.
        Returns:
            Dictionary that contains:
            1. tokens - list of objects Token.
            2. sentences - list of objects Sentence.
            3. lemma - list of lists of strings that represent lemmas of words.
            4. postag - list of lists of strings that represent postags of words.
            5. morph - list of lists of strings that represent morphological features.
            6. syntax_dep_tree - list of lists of objects WordSynt that represent a dependency tree.
        """
        assert self.model
        if type(argv[0]) == str:
            self.TOKENIZER = 'generic_tokenizer'
            self.pipeline = Pipeline(self.model, self.TOKENIZER, self.tagger, self.parser, 'conllu')

            return self.process_text(argv[0])

        self.TOKENIZER = 'horizontal'
        self.pipeline = Pipeline(self.model, self.TOKENIZER, self.tagger, self.parser, 'conllu')
        return self.process_tokenized(argv[0], argv[1])

    def process_text(self, text):
        udpipe_result = self.pipeline.process(text, self.error)
        if self.error.occurred():
            sys.stderr.write('An error occurred when calling ProcessorUDPipe: ')
            sys.stderr.write(self.error.message)
            return sys.stderr.write('\n')

        annotation = self.convert_conll(text, udpipe_result)
        
        return annotation

    def process_tokenized(self, tokens, sentences):
        raw_input = self.prepare_tokenized_input(tokens, sentences)
        annotation = self.process_text(raw_input)
        lemma_result = annotation['lemma']
        postag_result = annotation['postag']
        morph_result = annotation['morph']
        synt_dep_tree_result = annotation['syntax_dep_tree']

        return {'lemma': lemma_result,
                'postag': postag_result,
                'morph': morph_result,
                'syntax_dep_tree': synt_dep_tree_result}

    def prepare_tokenized_input(self, tokens, sentences):
        raw_input_s = ''
        for sent in sentences:
            line = ' '.join((e.text for e in CSentence(tokens, sent)))
            raw_input_s += line
            raw_input_s += '\n'
        return raw_input_s

    def convert_conll(self, text, udpipe_result):
        annotation = self.converter_conll(udpipe_result)

        if self._enable_tagger:
            for sent_lemma in annotation['lemma']:
                for i in range(len(sent_lemma)):
                    sent_lemma[i] = sent_lemma[i].lower()
                    
        else:
            for key in ('lemma', 'postag', 'morph'):
                annotation.pop(key, None)

        if not self._enable_parser:
            for key in ('syntax_dep_tree',):
                annotation.pop(key, None)

        annotation['sentences'] = self.converter_conll.sentence_split(annotation['form'])
        annotation['tokens'] = self.converter_conll.get_tokens(text, annotation['form'])

        return annotation