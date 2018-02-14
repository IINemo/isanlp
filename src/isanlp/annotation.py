"""Classes for basic linguistic annotations.

Intended for RPC.
"""

class Span:
    """Basic class for span-type annotations in text.
    
    Class members:
        begin - span offset begin.
        end - span offset end.
        
    """
    
    def __init__(self, begin = -1, end = -1):
        self.begin = begin
        self.end = end
    
    def left_overlap(self, other):
        """Checks whether the current span overlaps with other span on the left side."""
        
        return (self.begin <= other.begin and self.end <= other.end and self.end > other.begin
                or
                self.begin >= other.begin and self.end <= other.end)
    
    def overlap(self, other):
        """Checks whether the current span oeverlaps with other span."""
        
        return self.left_overlap(other) or other.left_overlap(self)
    
    def __str__(self):
        return '<{}, {}>'.format(self.begin, self.end)
    
    def __eq__(self, other):
        return self.begin == other.begin and self.end == other.end
    
    
class TaggedSpan(Span):
    """The span with additional tag field."""
    
    def __init__(self, tag, begin = -1, end = -1):
        super().__init__(begin, end)
        self.tag = tag
    
    
class Token(Span):
    """Token class that expands span with its text representation in text."""
    
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        
        
class TaggedRelation:
    """Relation between two annotations that are identified by ordinal number."""
    
    def __init__(self, tag, head = -1, dep = -1):
        self.tag = tag
        self.head = head
        self.dep = dep
    
    
class WordSynt:
    """Node in syntax dependency tree."""
    
    def __init__(self, parent, link_name):
        self.parent = parent
        self.link_name = link_name


class Sentence:
    """Sentence specified by starting token number and ending token number."""
    
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end


class Event:
    """Multi argument relation. Suitable for predicate-argument structures.
       
       Args:
            pred(tuple): Predicate address tuple of begin end positions.
            args(list): List of arguments - tuples of string tag and argument address (pair of ints).
    """
    
    def __init__(self, pred, args):    
        self.pred = pred
        self.args = args
