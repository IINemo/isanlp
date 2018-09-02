"""Representations of annotations with extended functionality.

Representations are not intended for RPC.
"""

from .annotation import Sentence


class CSentence(Sentence):
    """Representation of a sentence that utilizes a token list for addtional functionality."""
    
    def __init__(self, tokens, sent):
        super().__init__(sent.begin, sent.end)
        self.tokens = tokens
        
    def __len__(self):
        return self.end - self.begin
    
    def __iter__(self):
        return (e for e in self.tokens[self.begin : self.end])
    
    def __str__(self):
        return ' '.join([e.text for e in self])
        
    def __getitem__(self, idx):
        if idx >= 0:
            if idx + self.begin >= self.end:
                raise IndexError()

            return self.tokens[self.begin + idx]
        else:
            if idx + self.end < self.begin:
                raise IndexError()
            
            return self.tokens[self.end + idx]
