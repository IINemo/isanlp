from ..annotation import Token
from nltk.tokenize.regexp import WordPunctTokenizer


class ProcessorTokenizerNltkEn:
    """Performs tokenization of English texts.
    
    Simple wrapper around NLTK WordPunctTokenizer.
    """
    
    def __init__(self):
        self._nltk_proc = WordPunctTokenizer()
    
    def __call__(self, text):
        """Performs tokenization of text.
        
        Args:
            text(str): raw text.
            
        Returns:
            List of Token objects.
        """
        
        return [Token(text[start : end], start, end) for (start, end) in self._nltk_proc.span_tokenize(text)]
    