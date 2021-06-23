import tqdm
from ..annotation import Sentence


def parse_by_paragraphs(text, ppl):
    """ Pipeline wrapper for the long texts. """

    def correct_sentences(annotation):
        sentences = []
        start = 0

        key = [key for key in annotation.keys() if key not in ['text', 'tokens', 'sentences']][0]
        for sentence in annotation[key]:
            sentences.append(Sentence(start, start+len(sentence)))
            start += len(sentence)
        return sentences

    while '  ' in text:
        text = text.replace('  ', ' ')

    text = text.replace('\n ', '\n')
    while '\n\n' in text:
        text = text.replace('\n\n', '\n')

    paragraphs = text.strip().split('\n')
    full_result = {
        'text': text,
        'paragraphs': []
    }
    start = 0
    new_start = 0

    for paragraph in tqdm.tqdm(paragraphs):

        if new_start:
            full_result['paragraphs'].append((start, new_start))
        start = new_start

        result = ppl(paragraph)

        for token in result['tokens']:
            token.begin += start
            token.end += start

        for key in result:
            if not key in full_result:
                full_result[key] = result[key]
            else:
                full_result[key] += result[key]

        new_start = start + len(paragraph) + 1

    full_result['sentences'] = correct_sentences(full_result)

    return full_result
