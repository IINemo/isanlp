import pymystem3

from ..annotation_repr import CSentence


class ProcessorMystem:
    """Performs postagging, morphology analysis, and disambiguation of Russian texts.
    
    Simple wrapper around MyStem.
    """

    def __init__(self, delay_init=False):
        self._mystem = None
        if not delay_init:
            self.init()

    def init(self):
        if self._mystem is None:
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
        assert self._mystem

        lemma_result = []
        postag_result = []
        for sent in sentences:
            sent_repr = CSentence(tokens, sent)

            sent_text = ''
            for e in sent_repr:
                while len(sent_text) < e.begin:
                    sent_text += ' '

                sent_text += e.text

            offset_index = {e.begin: num for num, e in enumerate(sent_repr)}
            lemma_sent_result = [e.text for e in sent_repr]
            postag_sent_result = [''] * (sent.end - sent.begin)

            mystem_result = self._mystem.analyze(sent_text)

            offset = 0  # TODO: add all lemmas of unmached words to the first left matched word
            for mystem_token in mystem_result:
                mystem_token_text = mystem_token['text'].strip()
                new_pos = mystem_token['text'].find(mystem_token_text)
                new_pos = offset + new_pos

                if mystem_token_text and (new_pos in offset_index):
                    num = offset_index[new_pos]
                    if 'analysis' in mystem_token and mystem_token['analysis']:
                        an = mystem_token['analysis']
                        lemma_sent_result[num] = an[0]['lex']
                        postag_sent_result[num] = an[0]['gr']

                offset += len(mystem_token['text'])

            lemma_result.append(lemma_sent_result)
            postag_result.append(postag_sent_result)

        return {'lemma': lemma_result,
                'postag': postag_result}
