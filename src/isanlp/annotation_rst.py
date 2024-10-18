class DiscourseUnit:
    def __init__(self, id, left=None, right=None, text='', start=None, end=None,
                 orig_text=None, relation='', nuclearity='', proba=1.):
        """
        :param int id:
        :param DiscourseUnit left:
        :param DiscourseUnit right:
        :param str text: (optional)
        :param int start: start position in original text
        :param int end: end position in original text
        :param string relation: {the relation between left and right components | 'elementary' | 'root'}
        :param string nuclearity: {'NS' | 'SN' | 'NN'}
        :param float proba: predicted probability of the relation occurrence
        """
        self.id = id
        self.left = left
        self.right = right
        self.relation = relation
        self.nuclearity = nuclearity
        self.proba = proba
        self.start = start
        self.end = end

        if self.left:
            self.start = left.start
            self.end = right.end

        if orig_text:
            self.text = orig_text[self.start:self.end + 1].strip()
        else:
            self.text = text.strip()

        self._exporter = None

    def __str__(self):
        result = f"id: {self.id}\n"
        result += f"text: {self.text}\n"
        result += f"proba: {self.proba}\n"
        result += f"relation: {self.relation}\n"
        result += f"nuclearity: {self.nuclearity}\n"
        result += f"left: {self.left.text if self.left else None}\n"
        result += f"right: {self.right.text if self.right else None}\n"
        result += f"start: {self.start}\n"
        result += f"end: {self.end}"
        return result

    def to_rs3(self, filename, encoding='utf8'):
        self._exporter = Exporter(encoding=encoding)
        self._exporter(self, filename)


class Segment:
    def __init__(self, _id, parent, relname, text):
        self.id = _id + 1
        self.parent = parent + 1
        self.relname = relname
        self.text = self._xmlize_edu(text)

    @staticmethod
    def _xmlize_edu(text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def __str__(self):
        if self.parent != -1:
            return f'<segment id="{self.id}" parent="{self.parent}" relname="{self.relname}">{self.text}</segment>'

        return f'<segment id="{self.id}">{self.text}</segment>'


class Group:
    def __init__(self, _id, type, parent, relname):
        self.id = _id + 1
        self.type = type
        self.parent = parent + 1
        self.relname = relname

    def __str__(self):
        return f'<group id="{self.id}" type="{self.type}" parent="{self.parent}" relname="{self.relname}"/>'


class Root(Group):
    def __init__(self, _id, type="span"):
        Group.__init__(self, _id, type=type, parent=-1, relname="span")

    def __str__(self):
        return f'<group id="{self.id}" type="{self.type}"/>'


class Exporter:
    def __init__(self, encoding='utf8', verbose=False):
        self._encoding = encoding
        self.verbose = verbose
        self.max_id = 0

    def __call__(self, tree, filename):

        with open(filename, 'w', encoding=self._encoding) as fo:
            fo.write('<rst>\n')
            fo.write(self.make_header(tree))
            fo.write(self.make_body(tree))
            fo.write('</rst>')

    def compile_relation_set(self, tree):
        result = ['_'.join([tree.relation, tree.nuclearity])] + ['antithesis_NN']
        if not tree.left:
            return result
        if tree.left.left:
            result += self.compile_relation_set(tree.left)
        if tree.right.left:
            result += self.compile_relation_set(tree.right)

        return result

    def make_header(self, tree, whole_set=False):
        if whole_set:
            relations = ['preparation', 'cause-effect', 'solutionhood', 'condition', 'sequence', 'same-unit', 'background', 'interpretation-evaluation', 'contrast',
                         'evidence', 'joint', 'elaboration', 'purpose', 'attribution', 'concession', 'restatement', 'comparison'].sorted()
        else:
            relations = list(set(self.compile_relation_set(tree)))
            relations = [value if value != "elementary__" else "antithesis_NN" for value in relations]

        result = '\t<header>\n'
        result += '\t\t<relations>\n'
        for rel in relations:
            _relname, _type = rel.split('_')
            _type = 'multinuc' if _type == 'NN' else 'rst'
            result += f'\t\t\t<rel name="{_relname}" type="{_type}" />\n'
        result += '\t\t</relations>\n'
        result += '\t</header>\n'

        return result

    def print_log(self, log):
        if self.verbose:
            print(log)

    def get_max_id(self):
        self.max_id += 1
        return self.max_id

    def get_groups_and_edus(self, tree, terminal=False):
        groups = []
        edus = []

        if not tree.left:
            edus.append(Segment(tree.id, parent=-2, relname='', text=tree.text))
            return groups, edus

        if not tree.left.left:
            if tree.nuclearity == "SN":
                edus.append(Segment(tree.left.id, parent=tree.right.id, relname=tree.relation, text=tree.left.text))
            elif tree.nuclearity == "NS":
                edus.append(Segment(tree.left.id, parent=tree.id, relname='span', text=tree.left.text))
            else:
                edus.append(Segment(tree.left.id, parent=tree.id, relname=tree.relation, text=tree.left.text))

        else:
            _type = 'multinuc' if tree.left.nuclearity == "NN" else 'span'
            if tree.nuclearity == "SN":
                groups.append(Group(tree.left.id, type=_type, parent=tree.right.id, relname=tree.relation))
            elif tree.nuclearity == "NS":
                groups.append(Group(tree.left.id, type=_type, parent=tree.id, relname='span'))
            else:
                groups.append(Group(tree.left.id, type=_type, parent=tree.id, relname=tree.relation))

            _groups, _edus = self.get_groups_and_edus(tree.left)
            groups += _groups
            edus += _edus

        if not tree.right.left:
            if tree.nuclearity == "SN":
                edus.append(Segment(tree.right.id, parent=tree.id, relname='span', text=tree.right.text))
            elif tree.nuclearity == "NS":
                edus.append(Segment(tree.right.id, parent=tree.left.id, relname=tree.relation, text=tree.right.text))
            else:
                edus.append(Segment(tree.right.id, parent=tree.id, relname=tree.relation, text=tree.right.text))

        else:
            _type = 'multinuc' if tree.right.nuclearity == "NN" else 'span'
            if tree.nuclearity == "SN":
                groups.append(Group(tree.right.id, type=_type, parent=tree.id, relname='span'))
            elif tree.nuclearity == "NS":
                groups.append(Group(tree.right.id, type=_type, parent=tree.left.id, relname=tree.relation))
            else:
                groups.append(Group(tree.right.id, type=_type, parent=tree.id, relname=tree.relation))

            _groups, _edus = self.get_groups_and_edus(tree.right)
            groups += _groups
            edus += _edus

        if terminal:
            if len(edus) > 1:
                if tree.nuclearity == "NN":
                    groups.append(Root(tree.id, type='multinuc'))
                else:
                    groups.append(Root(tree.id))

        return groups, edus

    def make_body(self, tree):
        groups, edus = self.get_groups_and_edus(tree, terminal=True)
        result = '\t<body>\n'
        for edu in edus + groups:
            result += '\t\t' + str(edu) + '\n'
        result += '\t</body>\n'

        return result


class ForestExporter:
    def __init__(self, encoding='cp1251', verbose=False):
        self._encoding = encoding
        self._tree_exporter = Exporter(self._encoding, verbose=verbose)

    def __call__(self, trees, filename):

        with open(filename, 'w', encoding=self._encoding) as fo:
            fo.write('<rst>\n')
            fo.write(self.make_header(trees))
            fo.write(self.make_body(trees))
            fo.write('</rst>')

    def compile_relation_set(self, trees):
        result = []

        for tree in trees:
            result += list(set(self._tree_exporter.compile_relation_set(tree)))

        result = [value if value != "elementary__" else "antithesis_NN" for value in result]
        return result

    def make_header(self, trees):
        relations = list(set(self.compile_relation_set(trees)))

        result = '\t<header>\n'
        result += '\t\t<relations>\n'
        for rel in relations:
            _relname, _type = rel.split('_')
            _type = 'multinuc' if _type == 'NN' else 'rst'
            result += f'\t\t\t<rel name="{_relname}" type="{_type}" />\n'
        result += '\t\t</relations>\n'
        result += '\t</header>\n'

        return result

    def make_body(self, trees):
        groups, edus = [], []
        roots = []

        for tree in trees:
            _groups, _edus = self._tree_exporter.get_groups_and_edus(tree, terminal=True)

            if len(edus) > 1:
                if tree.nuclearity == "NN":
                    roots.append(Root(tree.id, type='multinuc'))
                else:
                    roots.append(Root(tree.id))

            groups += _groups
            edus += _edus

        result = '\t<body>\n'
        for edu in edus + groups:
            result += '\t\t' + str(edu) + '\n'
        result += '\t</body>\n'

        return result.replace('\u2015', '-')
