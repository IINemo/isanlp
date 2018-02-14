from . import annotation as ann


class ConverterNltkDepGraph:
    """Converter for transforming NLTK dependency graph into the list of basic dependecy nodes.
    
    Converter can be used in a common pipeline.
    """
    
    def __call__(self, dep_graph):
        result = []
        for sent in dep_graph:
            syn_ann = [None] * (len(sent.nodes) - 1)
            for num, node in sent.nodes.items():
                if node['head'] is not None:
                    syn_ann[num - 1] = ann.WordSynt(parent = node['head'] - 1, link_name = node['rel'])
            result.append(syn_ann)
        
        return result
