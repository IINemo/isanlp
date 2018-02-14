"""Classes for CONLL-X format parsing."""

from io import StringIO


class ConllFormatSentenceParser:
    """Parses annotations of a single sentence in CONLL-X format aquired from stream."""
    
    def __init__(self, string_io):
        self.string_ = string_io
        self.stop_ = False
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.stop_:
            line = self.string_.readline().rstrip('\n')
            if not line:
                self.stop_ = True
            else:
                return line.strip().split('\t')
        
        raise StopIteration()


class ConllFormatStreamParser:
    """Parses annotations of a text document in CONLL-X format aquired from stream."""
    
    def __init__(self, string):
        self.string_io_ = StringIO(string)
        self.stop_ = False
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.stop_:
            sent_parser = ConllFormatSentenceParser(self.string_io_)
            result = list(sent_parser)
            if not result:
                self.stop_ = True
            else:
                return result
            
        raise StopIteration()
    