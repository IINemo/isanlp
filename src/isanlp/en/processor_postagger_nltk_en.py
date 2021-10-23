import nltk

from ..annotation_repr import CSentence


class ProcessorPostaggerNltkEn:
    """Performs postagging of Enlish sentences.
    
    Simple wrapper of NLTK postagger.
    """

    def __call__(self, tokens, sentences):
        """Performs postagging.
        
        Args:
            tokens(list): List of Token objects.
            sentences(list): List of Sentence objects.
            
        Returns:
            List of lists (sentences) of strings that represent postag in 
            Penn Treebank format.
        """

        result = []
        for sent in sentences:
            result.append([e[1] for e in nltk.pos_tag([word.text for word in CSentence(tokens, sent)])])

        return result
