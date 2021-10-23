from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer

from ..annotation_repr import CSentence


def get_wordnet_pos(treebank_tag):
    """Converts Penn treebank postag into WordNet postag."""

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


class ProcessorLemmatizerNltkEn:
    """Perform lemmatication of English texts.
    
    Simple wrapper around NLTK WordNetLemmatizer.
    """

    def __init__(self, delay_init=False):
        self._nltk_lmtzr = None
        if not delay_init:
            self.init()

    def init(self):
        if self._nltk_lmtzr is None:
            self._nltk_lmtzr = WordNetLemmatizer()

    def __call__(self, tokens, sentences, postags):
        """Performs lemmatization of texts.
        
        Args:
            tokens(list): List of Token objects.
            sentences(list): List of Sentence objects.
            postags(list): List of strings that represent tags in Penn Treebank format.
            
        Returns:
            List of lists (sentences) of lemmas.
        """

        assert self._nltk_lmtzr
        result = []
        for text_sent, postag_sent in zip(sentences, postags):
            result.append([self._nltk_lmtzr.lemmatize(word.text.lower(), get_wordnet_pos(postag))
                           for (word, postag) in zip(CSentence(tokens, text_sent), postag_sent)])

        return result
