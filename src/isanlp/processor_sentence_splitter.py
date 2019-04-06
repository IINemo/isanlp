from .annotation import Sentence
from nltk.tokenize.punkt import PunktParameters
from nltk.tokenize.punkt import PunktSentenceTokenizer
from .ru.processor_tokenizer_ru import _ru_abbrevs
from .en.processor_tokenizer_nltk_en import _en_abbrevs
from itertools import combinations


class ProcessorSentenceSplitter:
    """Performs sentence splitting using simple rules.
    
    Simple wrapper around NLTK component. Suitable for european languages.
    """
    
    def __init__(self, delay_init = False):
        self.sent_tokeniser_ = None
        if not delay_init:
            self.init()

    def init(self):
        if self.sent_tokeniser_ is None:
            punkt_param = PunktParameters()
            punkt_param.abbrev_types = self.compile_abbreviations()
            self.sent_tokeniser_ = PunktSentenceTokenizer(punkt_param)

    def __call__(self, tokens):
        assert self.sent_tokeniser_
        sents = self.sent_tokeniser_.sentences_from_tokens((e.text for e in tokens))
        curr = 0
        res_sents = list()
        for sent in sents:
            res_sents.append(Sentence(curr, curr + len(sent)))
            curr += len(sent)
              
        return res_sents
    
    def compile_abbreviations(self):
        def get_dot_pairs(alphabet):
            return ['.'.join(abbrev) for abbrev in list(combinations(alphabet, 2))]
            
        def clean_regexps(regexps):
            return [''.join(abbrev.lower().split('.')[:-1]).replace('\\', '').replace(u'\xad', '').replace(' ', '.').replace('?', ' ').lower() for abbrev in regexps]
        
        ru_abbrevs = get_dot_pairs('цукенгшзхфвапролджэячсмитбю')
        ru_abbrevs += clean_regexps(_ru_abbrevs)

        en_abbrevs = get_dot_pairs('qwertyuiopasdfghjklzxcvbnm')
        en_abbrevs += clean_regexps(_en_abbrevs)
        
        return list(set(ru_abbrevs + en_abbrevs))
