from nltk.tokenize import RegexpTokenizer

from ..annotation import Token
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
    r'Mr\.',
    r'Mrs\.'
]


class ProcessorTokenizerNltkEn:
    """Performs tokenization of English texts.
    
    Wrapper around NLTK RegexpTokenizer.
    """

    def __init__(self, delay_init=False, *args, **kwargs):
        self._proc = None
        if not delay_init:
            self.init(*args, **kwargs)

    def init(self, abbrevs=_en_abbrevs):
        if self._proc is None:
            _en_regex = '|'.join(abbrevs + _ru_rules)
            self._proc = RegexpTokenizer(_en_regex)

    def __call__(self, text):
        """Performs tokenization of text.
        
        Args:
            text(str): raw text.
            
        Returns:
            List of Token objects.
        """

        return [Token(text[start: end], start, end)
                for (start, end) in self._proc.span_tokenize(text)]
