from .conll_format_parser import ConllFormatStreamParser
from .annotation import WordSynt
import logging

logger = logging.getLogger('isanlp')


class ConverterConllUDV1:
    FORM = 1
    LEMMA = 2
    POSTAG = 3
    MORPH = 5
    HEAD = 6
    DEPREL = 7


    def __call__(self, conll_raw_text):
        """Performs conll text parsing.

            Args:
                text(str): text.

            Returns:
                Dictionary that contains:
                1. form - list of lists with forms of words.
                2. lemma - list of lists of strings that represent lemmas of words.
                3. postag - list of lists of strings that represent postags of words.
                4. morph - list of lists of strings that represent morphological features.
                5. syntax_dep_tree - list of lists of objects WordSynt that represent a dependency tree
            """

        try:
            result_form = list()
            result_lemma = list()
            result_postag = list()
            result_morph = list()
            result_synt = list()
            for sent in ConllFormatStreamParser(conll_raw_text):
                new_sent_form = list()
                new_sent_lemma = list()
                new_sent_postag = list()
                new_sent_morph = list()
                new_sent_synt = list()
                for word in sent:
                    if word[0][0] != '#':
                        new_sent_form.append(word[self.FORM])
                        new_sent_lemma.append(word[self.LEMMA])
                        new_sent_postag.append(word[self.POSTAG])
                        new_sent_morph.append(self._parse_morphology(word[self.MORPH]))
                        new_sent_synt.append(self._parse_synt_tree(word[self.HEAD], word[self.DEPREL]))
                result_form.append(new_sent_form)
                result_lemma.append(new_sent_lemma)
                result_postag.append(new_sent_postag)
                result_morph.append(new_sent_form)
                result_synt.append(new_sent_synt)

        except IndexError as err:
            logger.error('Err: Index error: {}'.format(err))
            logger.error('--------------------------------')
            logger.error(conll_raw_text)
            logger.error('--------------------------------')
            raise

        return {'form': result_form,
                'lemma': result_lemma,
                'postag': result_postag,
                'morph': result_morph,
                'synt_dep_tree': result_synt}

    def _parse_morphology(self, string):
        result = [(s.split('=')) for s in string.split('|') if len(string) > 2]
        return {feature[0]: feature[1] for feature in result}

    def _parse_synt_tree(self, head, deprel):
        return WordSynt(parent=int(head) - 1,
                        link_name=deprel)
