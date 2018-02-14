import pymystem3
from ..annotation_repr import CSentence


class ProcessorMystem:
    """Performs postagging, morphology analysis, and disambiguation of Russian texts.
    
    Simple wrapper around MyStem.
    """
    
    def __init__(self):
        self._mystem = pymystem3.Mystem()
        self._mystem.start()
    
    def __call__(self, tokens, sentences):
        """Runs MyStem on the text.
        
        Args:
            tokens(list): List of Token objects.
            sentences(list): List of Sentence objects.
            
        Returns:
            Dictionary that contains:
            'lemma' : List of lists (sentences) of lemmas.
            'postag' : List of lists (sentences) of postags.
        """
        
        lemma_result = []
        postag_result = []
        for sent in sentences:
            sent_text = ' '.join([e.text for e in CSentence(tokens, sent)])
            mystem_result = self._mystem.analyze(sent_text)
            
            lemma_sent_result = []
            postag_sent_result = []
            for mystem_token in mystem_result:
                mystem_token_text = mystem_token['text'].strip()
                if mystem_token_text:
                    if 'analysis' in mystem_token:
                        lemma = mystem_token['analysis'][0]['lex']
                        postag = mystem_token['analysis'][0]['gr']
                    else:
                        lemma = mystem_token_text
                        postag = ''
                        
                    lemma_sent_result.append(lemma)
                    postag_sent_result.append(postag)
                    
            lemma_result.append(lemma_sent_result)
            postag_result.append(postag_sent_result)
        
        return {'lemma' : lemma_result, 
                'postag' : postag_result}
