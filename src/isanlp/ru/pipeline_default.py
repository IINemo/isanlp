from .processor_mystem import ProcessorMystem
from .processor_tokenizer_ru import ProcessorTokenizerRu
from ..pipeline_common import PipelineCommon
from ..processor_sentence_splitter import ProcessorSentenceSplitter


def create_pipeline(delay_init=False):
    return PipelineCommon({'tokenizer': (ProcessorTokenizerRu(),
                                         ['text'],
                                         {0: 'tokens'}),
                           'sentence_splitter': (ProcessorSentenceSplitter(),
                                                 ['tokens'],
                                                 {0: 'sentences'}),
                           'mystem': (ProcessorMystem(delay_init=delay_init),
                                      ['tokens', 'sentences'],
                                      {'postag': 'postag',
                                       'lemma': 'lemma'})},
                          name='default')
