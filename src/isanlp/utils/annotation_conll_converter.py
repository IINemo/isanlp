class AnnotationCONLLConverter:
    """Converts isanlp-style annotation to raw CONLL-U format."""
    
    def __init__(self):
        self._unifeatures = (
             'Abbr',
             'Animacy',
             'Aspect',
             'Case',
             'Clusivity',
             'Definite',
             'Degree',
             'Evident',
             'Foreign',
             'Gender',
             'Mood',
             'NounClass',
             'NumType',
             'Number',
             'Person',
             'Polarity',
             'Polite',
             'Poss',
             'PronType',
             'Reflex',
             'Tense',
             'Typo',
             'VerbForm',
             'Voice')
    
    def __call__(self, doc_id: str, annotation: dict):
        assert 'sentences' in annotation.keys()
        assert 'tokens' in annotation.keys()
        assert 'lemma' in annotation.keys()
        assert 'postag' in annotation.keys()
        assert 'morph' in annotation.keys()
        assert 'syntax_dep_tree' in annotation.keys()
        
        _postag_key = 'ud_postag' if 'ud_postag' in annotation.keys() else 'postag'
        
        yield '# newdoc id = ' + doc_id
        for j, sentence in enumerate(annotation['sentences']):
            for i, token_number in enumerate(range(sentence.begin, sentence.end)):
                yield_string = '\t'.join(list(map(self._prepare_value, [
                    i+1,  # ID
                    annotation['tokens'][token_number].text,  # FORM
                    annotation['lemma'][j][i],  # LEMMA
                    annotation['ud_postag'][j][i] if annotation['ud_postag'][j][i] else 'X',  # UPOS
                    '_',  # XPOS
                    self._to_universal_features(annotation['morph'][j][i]),  # FEATS
                    annotation['syntax_dep_tree'][j][i].parent+1,  # HEAD
                    annotation['syntax_dep_tree'][j][i].link_name,  # DEPREL
                    '_',  # DEPS
                ])))
                yield yield_string
            yield '\n'
             
    def _prepare_value(self, value):
        if type(value) == str:
            return value
        elif value:
            return str(value)
        elif value == 0:
            return '0'
        return '_'
        
    def _to_universal_features(self, morph_annot):
        if not morph_annot:
            return None
        
        return '|'.join([feature + '=' + morph_annot.get(feature) 
                         for feature in self._unifeatures if morph_annot.get(feature)])
