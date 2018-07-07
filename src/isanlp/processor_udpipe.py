import sys
from ufal.udpipe import Model, Pipeline, ProcessingError
from . import annotation as ann

# TODO: @elena
# 1) Move all annotation extraction functions to separate class converter_conll_ud_v1.py . Thats because we 
# have the same functionality in processor_syntaxnet_remote.py. I will update it to use this class.
# 2) Remove custom substring search function, use the standard one. 
# 3) Document __call__ method and prettify code according pep. I see at least discrepancy in string quotes. 

class ProcessorUDPipe:
    def __init__(self, model_path):
        self.model = Model.load(model_path)
        if not self.model:
            sys.stderr.write("Cannot load model from file '%s'\n" % model_path)

        self.pipeline = Pipeline(self.model, 'generic_tokenizer', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
        self.error = ProcessingError()

    def __call__(self, text):
        processed = self.pipeline.process(text, self.error)
        if self.error.occurred():
            sys.stderr.write("An error occurred when calling ProcessorUDPipe: ")
            sys.stderr.write(self.error.message)
            return sys.stderr.write("\n")

        annotation = self.parse_conll(processed)

        return {'text': text,
                'tokens': self.get_tokens(text, annotation),
                'sentences': self.sentence_split(annotation),
                'lemma': self.get_lemma(annotation),
                'postag': self.get_postag(annotation),
                'syntax_dep_tree': self.get_syntax_dep_tree(annotation),
                'morph': self.get_morph(annotation)
                }

    # TODO: @elena move all this functions to separate class converter_conll_ud_v1.py
    def parse_conll(self, string):
        keys = ['id', 'form', 'lemma', 'UPOS', 'XPOS', 'feats', 'head', 'deprel', 'deps']
        return [[dict(zip(keys, word.split('\t')[:10])) for word in sentence.split("\n")[2:-2]] for sentence in
                string.split("sent_id = ")[1:]]

    def get_tokens(self, text, annotation):
        """Performs sentence splitting.

        Returns:
            List of objects Token.
        """

        # TODO: @elena at least use standard `find` function in string. Why custom? 
        # (optional) you can also checkout fast substring search functions.
        def get_position(text, start, form): 
            # no way to get Token from udpipe.pipeline
            while (form != text[start: start + len(form)] and start + len(form) <= len(text)):
                start += 1
            return (start, start + len(form))

        ann_tokens = []
        position = 0

        for sent in annotation:
            for word in sent:
                form = word['form']
                begin, end = get_position(text, position, form)
                ann_tokens.append(ann.Token(text=word['form'], begin=begin, end=end))
                position = end
        return ann_tokens

    def sentence_split(self, annotation):
        """Performs sentence splitting.

        Returns:
            List of objects Sentence.
        """
        sentences = []
        start = 0
        for sent in annotation:
            sentences.append(ann.Sentence(begin=start, end=start + len(sent)))
            start += len(sent)
        return sentences

    def get_syntax_dep_tree(self, annotation):
        """Performs syntax dep tree parsing.

        Returns:
            List of objects WordSynt for each sentence.
        """
        syntax_dep_tree = []
        for sent in annotation:
            syntax_dep_tree.append([])
            for word in sent:
                syntax_dep_tree[-1].append(ann.WordSynt(link_name=word['deprel'], parent=word['head']))
        return syntax_dep_tree

    def get_lemma(self, annotation):
        """
        Returns:
             List of lists (sentences) of lemmas.
        """
        return [[word['lemma'] for word in sent] for sent in annotation]

    def get_postag(self, annotation):
        """
        Returns:
             List of lists (sentences) of postags.
        """
        return [[word['UPOS'] for word in sent] for sent in annotation]

    def get_morph(self, annotation):
        """
        Returns:
             List of lists (sentences) of morphological annotations.
        """

        def parse_string(morph_string):
            tmp = [(s.split('=')) for s in morph_string.split('|') if len(morph_string) > 2]
            return {feature[0]: feature[1] for feature in tmp}

        return [[parse_string(word['feats']) for word in sent] for sent in annotation]
