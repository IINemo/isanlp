import subprocess
import sys

import pkg_resources

from isanlp.converter_conll_ud_v1 import ConverterConllUDV1

try:
    from deeppavlov import build_model, configs
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deeppavlov'])
    from deeppavlov import build_model, configs


class ProcessorDeeppavlovSyntax:
    def __init__(self, delay_init=False):
        if not delay_init:
            self.init()

        self.MODELNAME = 'ru_syntagrus_joint_parsing'
        self.model = build_model(self.MODELNAME, download=True)

        self._enable_tagger = True
        self._enable_parser = True
        self.converter_conll = ConverterConllUDV1()

    def init(self):
        required = set('uvicorn fastapi telebot pyOpenSSL russian-tagsets'.split())
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed

        if missing:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])

        subprocess.check_call([sys.executable, '-m', 'deeppavlov', 'install', 'syntax_ru_syntagrus_bert'])

    def __call__(self, *argv):
        """Performs tagging, lemmatizing and parsing.
        Args:
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
            raise Exception('ProcessorDeeppavlovSyntax does not perform sentence splitting!')

        return self.process_tokenized(argv[0], argv[1])

    def process_tokenized(self, tokens, sentences):
        predictions = self.model(self.prepare_tokenized_input(tokens, sentences))
        annotation = self.converter_conll('\n\n'.join(predictions))
        lemma_result = annotation['lemma']
        postag_result = annotation['postag']
        morph_result = annotation['morph']
        synt_dep_tree_result = annotation['syntax_dep_tree']

        return {'lemma': lemma_result,
                'postag': postag_result,
                'morph': morph_result,
                'syntax_dep_tree': synt_dep_tree_result}

    def prepare_tokenized_input(self, tokens, sentences):
        lines = []
        for sent in sentences:
            lines.append([tok.text for tok in tokens[sent.begin: sent.end]])
        return lines
