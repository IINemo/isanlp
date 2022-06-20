import spacy
from . import annotation as ann


class ProcessorSpaCy:
    """ Wrapper around spaCy - The NLP library for multiple languages.

    Performs:
    1. Tokenization, sentence splitting.
    2. POS-Tagging, morphological analysis, lemmatizing.
    3. Dependency parsing.
    4. Named entity recognition.

    USAGE EXAMPLE
    (!) For ru_core_news_lg model, the spacy's tokenization does not always match with its components (parser, ner),
        so enforce an external tokenizer if possible.
    (!) Download the model beforehand with $ python -m spacy download model_name

    from isanlp import PipelineCommon
    from isanlp.processor_razdel import ProcessorRazdel
    from isanlp.processor_spacy import ProcessorSpaCy
    ppl = PipelineCommon([
        (ProcessorRazdel(), ['text'],
         {'tokens': 'tokens',
          'sentences': 'sentences'}),
        (ProcessorSpaCy('ru_core_news_lg'), ['tokens', 'sentences'],
         {'lemma': 'lemma',
          'postag': 'postag',
          'morph': 'morph',
          'syntax_dep_tree': 'syntax_dep_tree',
          'entities': 'entities'}),
    ])

    Tested with spacy==3.3.1
    """

    def __init__(self, model_name='en_core_web_trf', morphology=True, parser=True, ner=True, delay_init=False):
        """
        Args:
            model_name (str): spaCy model name, RoBERTa-based model for English by default.
            morphology (boolean): load the model with postagger, lemmatizer, and morphology predictor.  Will not affect other modules.
            parser (boolean): load the model with dependency parser. Disabling the parser leads to a switch to rule-based tokenizer.
            ner (boolean): load the model with named entity recognition. Will not affect other modules.
        """
        self._modelname = model_name
        self._enable_morphology = morphology
        self._enable_parser = parser
        self._enable_ner = ner

        self.model = None
        if not delay_init:
            self.init()

    def init(self):
        if self.model is None:
            exclude = []
            for key, include in zip(['tagger', 'parser', 'ner'],
                                    [self._enable_morphology, self._enable_parser, self._enable_ner]):
                if not include: exclude.append(key)

            self.model = spacy.load(self._modelname, exclude=exclude)
            if self._enable_parser == False: self.model.add_pipe(
                "sentencizer")  # By default sentence boundaries are predicted in the dependency parser.

    def __call__(self, *argv):
        """Performs tokenization, tagging, lemmatizing and parsing.
        Args:
            text(str): text. OR
            tokens(list): List of Token objects.
            sentences(list): List of Sentence objects.
        Returns:
            Dictionary that contains:
            1. tokens - list of objects Token.
            2. sentences - list of objects Sentence.
            3. lemma - list of lists of strings that represent lemmas of words.
            4. postag - list of lists of strings that represent postags of words.
            5. morph - list of lists of strings that represent morphological features.
            6. syntax_dep_tree - list of lists of objects WordSynt that represent a dependency tree.
            7. entities - list of lists of objects Span that represent named entities.
        """
        assert self.model

        if type(argv[0]) == str:
            # Run with tokenization
            text = argv[0]
            spacy_doc = self.model(text)

        else:
            # Run on pre-tokenized text
            tokens, sentences = argv[0], argv[1]

            words = [tok.text for tok in tokens]
            sent_starts = []
            for sentence in sentences:
                sent_starts += [True] + [False] * (sentence.end - sentence.begin - 1)

            assert len(words) == len(sent_starts)

            spacy_doc = spacy.tokens.Doc(self.model.vocab, words=words, sent_starts=sent_starts)
            spacy_doc = self.model(spacy_doc)

        return self._dictionarize(spacy_doc)

    def _dictionarize(self, doc, tokenization=True):
        def features_as_dict(features):
            result = dict()
            for feature in features:
                if '=' in feature:
                    key, value = feature.split('=')
                    result[key] = value
            return result

        def recount_offsets_by_sentence(token_idxs):
            if len(token_idxs) == 1:
                return token_idxs

            last_sentence_end = token_idxs[0][-1] + 1
            result = [token_idxs[0]]
            for sentence in token_idxs[1:]:
                result.append([tok - last_sentence_end for tok in sentence])
                last_sentence_end = sentence[-1] + 1

            return result

        result = dict()
        if tokenization:
            tokens = [ann.Token(tok.text, begin=tok.idx, end=tok.idx + len(tok.text)) for tok in doc]
            sentences = [ann.Sentence(sent.start, sent.end) for sent in doc.sents]
            result.update({'tokens': tokens, 'sentences': sentences})

        if self._enable_morphology:
            lemma = [[t.lemma_ for t in s] for s in doc.sents]
            postag = [[t.pos_ for t in s] for s in doc.sents]
            morph = [[features_as_dict(t.morph) for t in s] for s in doc.sents]
            result.update({'lemma': lemma, 'postag': postag, 'morph': morph})

        if self._enable_parser:
            # Map absolute indexes to intrasentential indexes
            idxs = [[t.i for t in s] for s in doc.sents]
            idxs_by_sent = recount_offsets_by_sentence(idxs)
            idx_dict = [dict(zip(idxs[i], idxs_by_sent[i])) for i in range(len(idxs))]

            # Parsing results
            link_names = [[t.dep_ for t in s] for s in doc.sents]
            link_heads = [[t.head.i for t in s] for s in doc.sents]  # absolute
            link_heads = [[idx_dict[i][head] for head in link_heads[i]] for i in
                          range(len(link_heads))]  # intrasentential

            # Collect to WordSynt objects
            syntax_dep_tree = []
            for sentence in zip(link_heads, link_names):
                current_syntax = []
                for parent, link_name in zip(*sentence):
                    current_syntax.append(ann.WordSynt(parent, link_name))
                syntax_dep_tree.append(current_syntax)

            # SpaCy links the ROOT token to itself, in isanlp we use -1
            for sent in range(len(syntax_dep_tree)):
                for tok in range(len(syntax_dep_tree[sent])):
                    if syntax_dep_tree[sent][tok].parent == tok:
                        syntax_dep_tree[sent][tok].parent = -1

            result.update({'syntax_dep_tree': syntax_dep_tree})

        if self._enable_ner:
            entities = [ann.TaggedSpan(ent.label_, ent.start, ent.end) for ent in doc.ents]
            result.update({'entities': entities})

        return result
