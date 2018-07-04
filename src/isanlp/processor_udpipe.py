import sys
from ufal.udpipe import Model, Pipeline, ProcessingError


class ProcessorUDPipe:
    def __init__(self,
                 model_path,
                 input_format,
                 output_format):
        self.model = Model.load(model_path)
        if not self.model:
            sys.stderr.write("Cannot load model from file '%s'\n" % model_path)

        self.pipeline = Pipeline(self.model, input_format, Pipeline.DEFAULT, Pipeline.DEFAULT, output_format)
        self.error = ProcessingError()

    def __call__(self, text):
        processed = self.pipeline.process(text, self.error)
        if self.error.occurred():
            sys.stderr.write("An error occurred when calling ProcessorUDPipe: ")
            sys.stderr.write(self.error.message)
            return sys.stderr.write("\n")

        morph_annot = self.parse_morph(processed)
        synt_annot = self.parse_synt(processed)

        return {'morph': morph_annot,
                'synt': synt_annot}

    def parse_morph(self, string):
        keys = ['id', 'form', 'lemma', 'UPOS', 'XPOS', 'feats']
        return [[dict(zip(keys, word.split('\t')[:6])) for word in sentence.split("\n")[2:-2]] for sentence in
                string.split("sent_id = ")[1:]]

    def parse_synt(self, string):
        keys = ['head', 'deprel', 'deps']
        return [[dict(zip(keys, word.split('\t')[6:10])) for word in sentence.split("\n")[2:-2]] for sentence in
                string.split("sent_id = ")[1:]]
