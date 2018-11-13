from . import annotation as ann
from .annotation_repr import CSentence
import subprocess as sbp
from nltk.parse.util import taggedsent_to_conll
from nltk.parse.dependencygraph import DependencyGraph


_warmup_text = """1	Mama	_	NNP	NNP	_	0	a	_	_
2	washed	_	VBD	VBD	_	0	a	_	_
3	the	_	DT	DT	_	0	a	_	_
4	frame	_	NN	NN	_	0	a	_	_

"""


class ProcessorParserMalt:
    """Performs parsing with MaltParser.
    
    Invokes MaltParser as a seprate process and communicates with it using pipes. MaltParser
    is active during the lifetime of the object. If MaltParser process is destroyed then
    current object cannot be used any further and should be recreated.
    Args:
        malt_commnd(str): Full MaltParser command.
        root_label(str): Root label that is used in the annotation.
        warmup_text(str): CONLL-X formmated string with small example for parser initialization.
        
    Example:
        ProcessorParserMalt(mal_command = '''java -cp /src/parser_conll2008/ensemble/ensemble-2010-04-19.jar:/src/parser_conll2008/ensemble/lib/log4j-1.2.15.jar:/src/parser_conll2008/ensemble/lib/liblinear-1.33-with-deps.jar \
edu.stanford.nlp.parser.ensemble.maltparser.Malt \
-gds T.TRANS+A.DEPR+A.PPLIFTED -m parse -w /src/parser_conll2008/ensemble/models/default/ -c conll08-covnonproj-ltr'''
    """
    
    def __init__(self, malt_command, root_label = 'root', warmup_text = _warmup_text):
        self._malt_process = sbp.Popen(malt_command.split(' '),
                                       stdin = sbp.PIPE, 
                                       stdout = sbp.PIPE,
                                       stderr = sbp.PIPE)
        self._root_label = root_label
        self._warmup(warmup_text)
        
    def __del__(self):
        self._malt_process.terminate()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, value, traceback):
        self._malt_process.terminate()
        
    def _warmup(self, warmup_text):
        self._process_sentence_str(warmup_text)
    
    def _process_sentence_str(self, str_sent):
        if not str_sent[:-1]:
            return ''
        
        self._malt_process.stdin.write(str_sent.encode('utf8'))
        self._malt_process.stdin.flush()

        tree_str = b''
        while not tree_str.endswith(b'\n\n'):
            if self._malt_process.poll() is not None:
                raise RuntimeError('MaltParser terminated, can no longer continue. The object should be recreated.')
                
            tree_str += self._malt_process.stdout.readline()

        return tree_str[:-2].decode('utf8')
        
    def __call__(self, tokens, sentences, postags):
        """Perform syntax dep parsing.
        
        Args:
            tokens: list of tokens
            sentence: list of sentences
            postags: list of postags
        
        Returns:
            Syntax dependency tree in NLTK format (use ConverterNltkDepGraph to convert to standard annotation.
        """
        
        result = list()
        for i in range(len(sentences)):
            nltk_sent = zip([word.text for word in CSentence(tokens, sentences[i])], postags[i])
            str_sent = ''.join([e for e in taggedsent_to_conll(nltk_sent)]) + '\n'
            tree_str = self._process_sentence_str(str_sent)
            dep_gr = DependencyGraph(tree_str, top_relation_label = self._root_label)
            result.append(dep_gr)
        
        return result
    
