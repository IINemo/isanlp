from .annotation import Sentence
from nltk.tokenize.punkt import PunktSentenceTokenizer


class ProcessorSentenceSplitter:
    """Performs sentence splitting using simple rules.
    
    Simple wrapper around NLTK component. Suitable for european languages.
    """
    
    def __init__(self):
        self.sent_tokeniser_ = PunktSentenceTokenizer()
    
    def __call__(self, tokens):
        sents = self.sent_tokeniser_.sentences_from_tokens((e.text for e in tokens))
        curr = 0
        res_sents = list()
        for sent in sents:
            res_sents.append(Sentence(curr, curr + len(sent)))
            curr += len(sent)
        
        return res_sents
