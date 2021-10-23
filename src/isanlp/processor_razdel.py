from typing import List
from . import annotation as ann

try:
    import razdel
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'razdel'])
    import razdel


class ProcessorRazdel:
    """Wrapper around Razdel — rule-based system for Russian sentence and word tokenization.

    Performs:
    1. Tokenization.
    2. Sentence splitting.
    """

    def __init__(self, delay_init=False):
        pass

    def __call__(self, text: str):
        """Performs tokenization and sentence splitting.

        Args:
            text(str): text.

        Returns:
            Dictionary that contains:
            1. tokens - list of objects Token.
            2. sentences - list of objects Sentences.
        """

        ann_tokens = [ann.Token(text=token.text, begin=token.start, end=token.stop) for token in razdel.tokenize(text)]

        sentences = [ProcessorRazdel.offset_to_tokens(offset.start, offset.stop, ann_tokens) for offset in
                     razdel.sentenize(text)]
        ann_sentences = [ann.Sentence(begin, end) for begin, end in sentences]

        return {'tokens': ann_tokens,
                'sentences': ann_sentences}

    @staticmethod
    def offset_to_tokens(start: int, stop: int, tokens: List[ann.Token]):
        begin = -1
        for idx, token in enumerate(tokens):
            if begin == -1 and token.begin >= start:
                begin = idx
            if token.end >= stop:
                return begin, idx+1
