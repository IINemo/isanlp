from conll_format_parser import ConllFormatStreamParser


# TODO: @elena copy all functions for annotation extraction.
# TODO: @elena I moved parse_conll here as a useful function for dealing with conll. This function is good
# but it creates some overhead and slower than direct indexes.
# consider using int literals like: 
# ID = 0 
# FORM = 1
# LEMMA = 2

def parse_conll(self, string):
    keys = ['id', 'form', 'lemma', 'UPOS', 'XPOS', 'feats', 'head', 'deprel', 'deps']
    return [[dict(zip(keys, word.split('\t')[:10])) for word in sentence.split("\n")[2:-2]] for sentence in
            string.split("sent_id = ")[1:]]

class ConverterConllUDV1:
    def __call__(conll_raw_text):
        # TODO: @elena  
        # input: conll_raw_text 
        # output: all available annotations 
        # Please, use the ConllFormatStreamParser for your purposes.
        pass