import polyglot
from polyglot.text import Text, Word
from . import annotation as ann


_make_tokens = lambda spans, text: [ann.Token(text[span.begin : span.end], span.begin, span.end) for span in spans]


class ProcessorPolyglot:
    """Wrapper around Polyglot - multi-language library (40 languages).
    
    Performs:
    1. Language detection.
    2. Tokenization.
    3. Sentence splitting.
    4. Named entity recognition.
    """
    
    def __call__(self, text):
        """Performs language detection, tokenization, and named entity recognition.
        
        Args:
            text(str): text.
        
        Returns:
            Dictionary that contains:
            1. tokens - list of objects Token.
            2. entities - list of objects TaggedSpan.
            3. lang - str language of text.
        """
        
        pg_text = Text(text)
        token_spans = self._tokenize(pg_text)
        pg_entities = pg_text.entities
        ann_entities = []
        for pg_ent in pg_entities:
            tok_begin = token_spans[pg_ent.start]
            tok_end = token_spans[pg_ent.end - 1]
            ann_entities.append(ann.TaggedSpan(pg_ent.tag, tok_begin.begin, tok_end.end))
        
        return {'tokens' : _make_tokens(token_spans, text),
                'entities' : ann_entities,
                'lang' : pg_text.language.code}
    
    def detect_language(self, text):
        """Detects language of the text.
        
        Returns:
            String that represents language code ("ru", "en").
        """
        
        from langdetect import detect
        code = detect(text)
        
        if code not in ('ru', 'en'):
            return Text(text).language.code
        
        return code
    
    def tokenize(self, text):
        """Performs tokenization of text.
        
        Returns:
            List of objects Token.
        """
        
        return _make_tokens(self._tokenize(Text(text)), text)
    
    def sentence_split(self, text):
        """Performs sentence splitting.
        
        Args:
            text(str): raw text.
        
        Returns:
            List of objects Sentence.
        """
        pg_text = Text(text)
        return {'tokens' : _make_tokens(self._tokenize(pg_text), text),
                'sentences' : [ann.Sentence(begin = pg_sent.start, end = pg_sent.end) 
                for pg_sent in Text(text).sentences]}
    
    def _tokenize(self, pg_text):
        pg_tokens = pg_text.word_tokenizer.transform(polyglot.base.Sequence(pg_text.raw))
        
        ann_tokens = []
        for start, end in zip(pg_tokens.idx[:-1], pg_tokens.idx[1:]):
            orig_text = pg_tokens.text[start : end]
            
            tmp_text = orig_text.lstrip()
            start += len(orig_text) - len(tmp_text)
            
            tmp_text = orig_text.rstrip()
            end -= len(orig_text) - len(tmp_text)
            
            tok_text = pg_tokens.text[start : end]
            if tok_text:
                ann_tokens.append(ann.Span(start, end))
        
        return ann_tokens
    
