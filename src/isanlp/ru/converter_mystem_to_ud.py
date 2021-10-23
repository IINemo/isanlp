import re

conv_postag = {'A': 'ADJ',
               'ADV': 'ADV',
               'S': 'NOUN',
               'V': 'VERB',
               'PR': 'ADP',
               'INTJ': 'INTJ',
               'PART': 'PART',
               'NUM': 'NUM',
               'ADVPRO': 'ADV',
               'APRO': 'PRON',
               'SPRO': 'PRON',
               'ANUM': 'ADJ',
               'CONJ': 'CONJ',
               'COM': 'X'}

conv_number = {'ед': 'Sing',
               'мн': 'Plur'}

conv_case = {'им': 'Nom',
             'род': 'Gen',
             'вин': 'Acc',
             'дат': 'Dat',
             'твор': 'Ins',
             'пр': 'Loc',
             'парт': 'Par',
             'местн': 'Loc',
             'зват': 'Voc'}

conv_tense = {'наст': 'Pres',
              'прош': 'Past',
              'непрош': 'Imp'}

conv_gender = {'муж': 'Masc',
               'жен': 'Fem',
               'сред': 'Neut'}

conv_verb_form = {'изъяв': 'Fin',
                  'инф': 'Inf',
                  'деепр': 'Ger',
                  'прич': 'Part',
                  'пов': 'Fin'}

conv_person = {'1-л': '1',
               '2-л': '2',
               '3-л': '3'}

conv_comparis = {'прев': 'Sup',
                 'срав': 'Cmp'}

conv_degree = {'полн': 'Pos'}
conv_variant = {'кр': 'Brev'}

conv_aspect = {'несов': 'Imp',
               'сов': 'Perf'}

conv_voice = {'действ': 'Act',
              'страд': 'Pass'}

conv_anim = {'од': 'Anim',
             'неод': 'Inan'}

conv_valency = {'пе': 'TR',
                'нп': 'INTR'}

conv_dicts = {'Animacy': conv_anim,
              'Case': conv_case,
              'Gender': conv_gender,
              'Number': conv_number,
              'fPOS': conv_postag,
              'Aspect': conv_aspect,
              'Tense': conv_tense,
              'VerbForm': conv_verb_form,
              'Voice': conv_voice,
              'Person': conv_person,
              'Comparision': conv_comparis,
              'Valency': conv_valency,
              'Degree': conv_degree,
              'Variant': conv_variant}

conv_rev = {}
for (label, dct) in conv_dicts.items():
    for key in dct.keys():
        conv_rev[key] = label


def convert_item(feats, item):
    if item:
        label = conv_rev[item]
        feats[label] = conv_dicts[label][item]


def parse_mystem(mystem_str):
    if not mystem_str or not '=' in mystem_str:
        # token is not in russian
        return {}

    lexeme, wordform = mystem_str.split('=')
    lexeme = lexeme.split(',')
    pos_tag = lexeme[0]
    lexeme = lexeme[1:]

    feats = {'fPOS': pos_tag}
    for item in lexeme:
        if item and item in conv_rev:
            label = conv_rev[item]
            feats[label] = item

    wordforms = [e for e in re.split('\||\(|\)', wordform) if e]

    for form in wordforms[:1]:
        vals = form.split(',')
        for item in vals:
            if item and item in conv_rev:
                label = conv_rev[item]
                feats[label] = item

    return feats


def convert_mystem_to_ud(mystem_str):
    if not mystem_str:
        return {}

    feats = parse_mystem(mystem_str)

    ud_feats = {}
    for k, v in feats.items():
        ud_feats[k] = conv_dicts[k][v]

    return ud_feats


class ConverterMystemToUd:
    """Converts MyStem postag annotation format into Universal dependency annotation format.
    
    Can be used inside a common pipeline.
    """

    def __call__(self, mystem_postags):
        result_postags = list()
        result_morph = list()
        for sent in mystem_postags:
            result_sent_postag = []
            result_sent_morph = []
            for postag in sent:
                cv = convert_mystem_to_ud(postag)
                result_sent_postag.append(cv.get('fPOS', ''))
                result_sent_morph.append(cv)

            result_postags.append(result_sent_postag)
            result_morph.append(result_sent_morph)

        return {'postag': result_postags,
                'morph': result_morph}
