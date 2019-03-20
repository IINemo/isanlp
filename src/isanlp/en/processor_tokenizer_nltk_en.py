from ..annotation import Token
from nltk.tokenize import RegexpTokenizer
from ..ru.processor_tokenizer_ru import _ru_rules

_en_abbrevs = [
    r'dr',
    r'vs',
    r'mr\.',
    r'mrs\.',
    r'prof',
    r'inc',
    r'sc',
    r'ph',
    r'B\.Sc\.',
    r'Ph\.D\.',
    r'\w\. ?\w\.',
]

_en_regex = u'|'.join(_en_abbrevs + _ru_rules)

class ProcessorTokenizerNltkEn:
    """Performs tokenization of English texts.
    
    Wrapper around NLTK RegexpTokenizer.
    """
    
    def __init__(self):
        self._proc = RegexpTokenizer(_en_regex)
    
    def __call__(self, text):
        """Performs tokenization of text.
        
        Args:
            text(str): raw text.
            
        Returns:
            List of Token objects.
        """
        
        return [Token(text[start : end], start, end) for (start, end) in self._nltk_proc.span_tokenize(text)]
    