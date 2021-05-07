import string
import pandas as pd


class GeEdge(object):
    """ Class for gephi-style edge objects """

    def __init__(self, source, target, kind, label, type='Undirected', timeset=None, weight=1.):
        self.Source, self.Target, self.Type, self.Kind, self.Label, self.timeset, self.Weight = (
            source, target, type, kind, label, timeset, weight)

    def __iter__(self):
        iters = dict((x, y) for x, y in GeEdge.__dict__.items() if x[:2] != '__')
        iters.update(self.__dict__)

        for x, y in iters.items():
            yield x, y

    def __hash__(self):
        return hash(str(self.Source) + str(self.Target) + self.Kind + self.Type)


class AnnotationGephiConverter:
    """Converts isanlp-style lemma+syntax annotation to the gephi-style tables nodes.csv and edges.csv
        Optional fields for node.csv (may require corresponding fields in the annotation):
            - postag
            - frequency of lemma in the annotation
        Optional types of edges for edges.csv (requires corresponding fields in the annotation):
            - srl
    """

    def __init__(self, srl=True, postag=True, freq=True):
        self._srl, self._postag, self._freq = srl, postag, freq

    def __call__(self, annot: dict, outfile_nodes='nodes.csv', outfile_edges='edges.csv'):
        assert 'lemma' in annot
        assert 'syntax_dep_tree' in annot

        if self._srl: assert 'srl' in annot
        if self._postag: assert 'postag' in annot

        nodes, edges = [], []
        postags, freqs = [], []

        for i, sentence in enumerate(annot['syntax_dep_tree']):

            # Nodes
            for j, lemma in enumerate(annot['lemma'][i]):
                lemma = lemma.lower()
                if not lemma in nodes and not lemma in string.punctuation:
                    nodes.append(lemma)
                    if self._freq: freqs.append(1)
                    if self._postag: postags.append(annot['postag'][i][j])

                if self._freq and lemma in nodes: freqs[nodes.index(lemma)] += 1

            # Edges
            for j, syntannot in enumerate(sentence):

                try:
                    source = nodes.index(annot['lemma'][i][syntannot.parent].lower())
                    target = nodes.index(annot['lemma'][i][j].lower())
                except:
                    # punctuation is ommited
                    continue

                new_edge = GeEdge(source=source, target=target, kind='synt', label=syntannot.link_name)
                if new_edge not in edges:
                    edges.append(new_edge)

            if self._srl:
                for srlannot in annot['srl'][i]:
                    source_lemma = annot['lemma'][i][srlannot.pred[0]].lower()
                    if source_lemma in nodes:
                        source = nodes.index(source_lemma)
                        for arg in srlannot.args:
                            target_lemma = annot['lemma'][i][arg.begin].lower()
                            if target_lemma in nodes:
                                target = nodes.index(target_lemma)
                                new_edge = GeEdge(source=source, target=target, kind='sem', label=arg.tag)
                                if new_edge not in edges:
                                    edges.append(new_edge)

        dfnodes = pd.DataFrame({
            'Label': nodes,
            'timeset': '',
            'POS': postags,
            'Freq': freqs,
        }).reset_index().rename(columns={"index": "Id",})

        if not self._postag:
            del dfnodes.POS

        if not self._freq:
            del dfnodes.Freq
        else:
            dfnodes.Freq /= dfnodes.Freq.sum()

        dfnodes.to_csv(outfile_nodes, index=False)

        dfedges = pd.DataFrame([dict(edge) for edge in edges]).reset_index().rename(columns={"index": "Id",})
        dfedges.to_csv(outfile_edges, index=False)
