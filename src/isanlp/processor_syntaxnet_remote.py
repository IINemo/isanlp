from .annotation import WordSynt
from .annotation_repr import CSentence
from .conll_format_parser import ConllFormatStreamParser

import sys
import socket
import logging


logger = logging.getLogger('isanlp')


class ProcessorSyntaxNetRemote:
    """Processor for calling SyntaxNet remotely.
    
    It is intended to work with docker container inemo/syntaxnet_ru inemo/syntaxnet_eng etc.
    Calls SyntaxNet remotely, but does not use gRPC.
    
    Args:
        host(str): hostname via which the SyntaxNet container can be accessed.
        port(int): port of the accessibly docker container.
    """
    
    def __init__(self, host, port):
        self.host_ = host
        self.port_ = port
    
    def __call__(self, tokens, sentences):
        """Invokes SyntaxNet on the remote server.
        
        Args:
            tokens(list): list of objects Token.
            sentences(list): list of objects Sentence.
            
        Returns: 
            Dictionary that contains:
            1. 'syntax_dep_tree': List of objects SynWord that represent a dependency tree.
            2. 'postag': List of lists of strings that represent postags of words.
            3. 'morph': List of strings that represent morphological features.
        """
        
        raw_input_s = self._prepare_raw_input_for_syntaxnet(tokens, sentences)        
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host_, self.port_))
        sock.sendall(raw_input_s)
        raw_output_s = self._read_all_from_socket(sock)
        sock.close()

        if not raw_output_s:
            return None

        result_postag, result_morph, result_synt = self._parse_conll_format(raw_output_s)
        
        return {'postag' : result_postag, 
                'morph' : result_morph, 
                'syntax_dep_tree' : result_synt}
    
    def _fill_spans_in_trees(self, tokens, sentences, trees):
        for in_sent, p_sent in zip(sentences, trees):
            for in_word, p_word in zip(CSentence(tokens, in_sent), p_sent):
                p_word.begin = in_word.begin
                p_word.end = in_word.end
    
    def _prepare_raw_input_for_syntaxnet(self, tokens, input_data):
        raw_input_s = ''
        if input_data is str:
            raw_input_s = text + '\n\n'
        else:
            for sent in input_data:
                line = ' '.join((e.text for e in CSentence(tokens, sent)))
                raw_input_s += line
                raw_input_s += '\n'
            raw_input_s += '\n'
        
        return raw_input_s.encode('utf8')
        
    def _read_all_from_socket(self, sock):
        buf = bytes()
        
        try:
            while True:
                data = sock.recv(51200)
                if data:
                    buf += data
                else:
                    break
        except socket.error as err:
            logger.error('Err: Socket error: {}'.format(err))
            raise

        return buf.decode('utf8')
  
    def _parse_conll_format(self, string):
        try:
            result_postag = list()
            result_morph = list()
            result_synt = list()
            for sent in ConllFormatStreamParser(string):
                new_sent_postag = list()
                new_sent_morph = list()
                new_sent_synt = list()
                for word in sent:
                    new_word = WordSynt(parent = int(word[6]) - 1,
                                        link_name = word[7])
                    new_sent_synt.append(new_word)
                    new_sent_morph.append(word[5])
                    new_sent_postag.append(word[3])
                    
                result_postag.append(new_sent_postag)
                result_morph.append(new_sent_morph)
                result_synt.append(new_sent_synt)
            
            return result_postag, result_morph, result_synt
        except IndexError as err:
            logger.error('Err: Index error: {}'.format(err))
            logger.error('--------------------------------')
            logger.error(string)
            logger.error('--------------------------------')
            raise
            