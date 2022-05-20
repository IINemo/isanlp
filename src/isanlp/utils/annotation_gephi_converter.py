import string
import numpy as np
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
    """ Converts isanlp-style lemma+syntax annotation to the gephi-style tables nodes.csv and edges.csv
        Optional additional fields for node.csv (may require corresponding fields in the annotation):
            - postag
            - frequency of lemma in the annotation
        Optional additional types of edges for edges.csv (requires corresponding fields in the annotation):
            - srl
    """

    def __init__(self, freq=True, postag=True, srl=True, rst=True,
                 key_lemma='lemma', key_postag='postag', key_syntax='syntax_dep_tree', key_srl='srl', key_rst='rst',
                 mask_edu_names=False):
        self._freq = freq
        self._keys = {
            'lemma': (key_lemma, True),
            'postag': (key_postag, postag),
            'syntax': (key_syntax, True),
            'srl': (key_srl, srl),
            'rst': (key_rst, rst)
        }
        self._mask_edu_names = mask_edu_names
        self._PUNCTUATION = string.punctuation + "«»—"
        self._edu_marker = '___'

    def __call__(self, annot: dict, outfile_nodes='nodes.csv', outfile_edges='edges.csv', rst_tree_type='dependency'):
        for key, params in self._keys.items():
            name, required = params
            if required:
                assert name in annot, f"Required key {name} is missing in input dict!"

        labels, edges = [], []
        postags, freqs = [], []

        key_syntax = self._keys['syntax'][0]
        key_lemma = self._keys['lemma'][0]
        key_postag, required_postag = self._keys['postag']

        for i, sentence in enumerate(annot[key_syntax]):

            # Nodes
            for j, lemma in enumerate(annot[key_lemma][i]):
                lemma = lemma.lower()
                if not lemma in labels and not lemma in self._PUNCTUATION:
                    labels.append(lemma)
                    if self._freq: freqs.append(1)
                    if required_postag: postags.append(annot[key_postag][i][j])

                if self._freq and lemma in labels: freqs[labels.index(lemma)] += 1

            # Edges
            for j, syntannot in enumerate(sentence):
                try:
                    source = labels.index(annot[key_lemma][i][syntannot.parent].lower())
                    target = labels.index(annot[key_lemma][i][j].lower())
                except:
                    # punctuation is ommited
                    continue

                new_edge = GeEdge(source=source, target=target, kind='synt', type='Directed', label=syntannot.link_name)
                if new_edge not in edges:
                    edges.append(new_edge)

            # SRL (optional)
            key_srl, required_srl = self._keys['srl']
            if required_srl:
                for srlannot in annot[key_srl][i]:
                    source_lemma = annot[key_lemma][i][srlannot.pred[0]].lower()
                    if source_lemma in labels:
                        source = labels.index(source_lemma)
                        for arg in srlannot.args:
                            target_lemma = annot[key_lemma][i][arg.begin].lower()
                            if target_lemma in labels:
                                target = labels.index(target_lemma)
                                new_edge = GeEdge(source=source, target=target, kind='sem', type='Directed',
                                                  label=arg.tag)
                                if new_edge not in edges:
                                    edges.append(new_edge)

        if self._freq:
            # Count actual lemma frequencies
            freqs = (np.array(freqs) / sum(freqs)).tolist()
            self._current_lemma = labels
            self._current_freqs = freqs

        # RST (optional)
        key_rst, required_rst = self._keys['rst']
        if required_rst:
            # For matching discourse units with collected nodes
            lemmas_plain = [word for sentence in annot[key_lemma] for word in sentence]
            self._all_tokens = annot['tokens']
            for word, lemma in zip(self._all_tokens, lemmas_plain):
                word.lemma = lemma

            # Nodes
            for tree in annot[key_rst]:
                rst_nodes, rst_postags, rst_freqs = self._rst2nodes(tree)
                labels += rst_nodes
                postags += rst_postags
                freqs += rst_freqs
                edges += self._rst2edges(tree, labels, rst_tree_type)

        dfnodes = pd.DataFrame({
            'Label': labels,
            'timeset': '',
            'POS': postags,
            'Freq': freqs if freqs else '',
        }).reset_index().rename(columns={"index": "Id", })

        # (optional) replace EDU labels with their numbers
        if required_rst and self._mask_edu_names:
            counter = iter(range(1, dfnodes.shape[0] + 1))
            masked_label = pd.Series(
                [next(counter) if tag == 'EDU' else dfnodes.Label.iloc[i] for i, tag in enumerate(dfnodes.POS.values)])
            dfnodes.Label = masked_label

        if not required_postag:
            del dfnodes.POS

        if not self._freq:
            del dfnodes['Freq']

        dfnodes.to_csv(outfile_nodes, index=False, sep='\t')

        dfedges = pd.DataFrame([dict(edge) for edge in edges]).reset_index().rename(columns={"index": "Id", })
        dfedges.to_csv(outfile_edges, index=False, sep='\t')

    def _text_to_lemmas(self, start, end):
        return [word.lemma for word in self._all_tokens if word.begin >= start and word.end <= end]

    def _rst2nodes(self, tree):
        """ Returns labels, tags (EDU/DU) and -optionally- freqs (weighted number of tokens) for a single RST discourse unit and it's children """

        label = [self._edu_marker + tree.text] if tree.relation == 'elementary' else []
        tag = ['EDU'] if tree.relation == 'elementary' else []

        # DU frequency is a sum of it's lemma frequencies
        freq = [] if (not self._freq or tree.relation != 'elementary') else [
            sum([self._current_freqs[self._current_lemma.index(word)
                 ] for word in self._text_to_lemmas(tree.start, tree.end)
                 if word in self._current_lemma])]

        if tree.relation != 'elementary':
            l_label, l_tag, l_freq = self._rst2nodes(tree.left)
            r_label, r_tag, r_freq = self._rst2nodes(tree.right)

            label += l_label + r_label
            tag += l_tag + r_tag
            freq += l_freq + r_freq

        return label, tag, freq

    @staticmethod
    def _get_root_edu(tree):
        """ Returns the leftmost elementary root child """
        if tree.relation == 'elementary':
            return tree

        # Nucleus at the left
        if tree.nuclearity[0] == 'N':
            return AnnotationGephiConverter._get_root_edu(tree.left)

        # Nucleus at the right
        return AnnotationGephiConverter._get_root_edu(tree.right)

    @staticmethod
    def rename_relation(relation, nuclearity):
        target_map = {
            'antithesis': 'attribution',
            'cause': 'cause-effect',
            'effect': 'cause-effect',
            'conclusion': 'restatement',
            'interpretation': 'interpretation-evaluation',
            'evaluation': 'interpretation-evaluation',
            'motivation': 'condition',
        }

        relation = target_map.get(relation, relation)

        relation_map = {
            'evidence_SN': 'preparation_SN',
            'restatement_SN': 'condition_SN',
            'restatement_NS': 'elaboration_NS',
            'solutionhood_NS': 'elaboration_NS',
            'preparation_NS': 'elaboration_NS',
            'concession_SN': 'preparation_SN',
            'evaluation_SN': 'preparation_SN',
            'elaboration_SN': 'preparation_SN',
            'background_SN': 'preparation_SN',
        }

        full_relation = relation + '_' + nuclearity
        full_relation = relation_map.get(full_relation, full_relation)

        return relation, nuclearity

    def _rst2edges(self, tree, labels, tree_type='constituency'):
        """ Returns list of edges for a single RST discourse unit and it's children """

        assert tree_type in ('constituency', 'dependency')

        if not tree.relation:
            tree.relation = 'joint'
            tree.nuclearity = 'NN'

        if not tree.nuclearity:
            tree.nuclearity = '_'

        relation, nuclearity = self.rename_relation(tree.relation, tree.nuclearity)
        label = 'contains' if tree.relation == 'elementary' else relation
        kind = 'edu' if tree.relation == 'elementary' else 'rst'
        etype = 'Directed'

        if tree.relation == 'elementary':
            lemmatized = self._text_to_lemmas(tree.start, tree.end)
            targets = [labels.index(word) for word in lemmatized if word in labels]
            source = labels.index(self._edu_marker + tree.text)
            return [GeEdge(source=source, target=target, kind=kind, type=etype, label=label) for target in targets]

        if tree_type == 'constituency':
            left_target, left_source = labels.index(self._edu_marker + tree.left.text), labels.index(
                self._edu_marker + tree.text)
            right_target, right_source = labels.index(self._edu_marker + tree.right.text), labels.index(
                self._edu_marker + tree.text)
            left_label = 'contains' if nuclearity == 'NS' else label
            right_label = 'contains' if nuclearity == 'SN' else label

            return [GeEdge(source=left_source, target=left_target, kind=kind, type=etype, label=left_label),
                    GeEdge(source=right_source, target=right_target, kind=kind, type=etype, label=right_label)
                    ] + self._rst2edges(tree.left, labels, tree_type) + self._rst2edges(tree.right, labels, tree_type)

        elif tree_type == 'dependency':

            if nuclearity == 'SN':
                source, target = (labels.index(self._edu_marker + self._get_root_edu(tree.left).text),
                                  labels.index(self._edu_marker + self._get_root_edu(tree.right).text))
            else:
                source, target = (labels.index(self._edu_marker + self._get_root_edu(tree.right).text),
                                  labels.index(self._edu_marker + self._get_root_edu(tree.left).text))

            return [GeEdge(source=source, target=target, kind=kind, type=etype, label=label)
                    ] + self._rst2edges(tree.left, labels, tree_type) + self._rst2edges(tree.right, labels, tree_type)
