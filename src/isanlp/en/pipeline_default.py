from .processor_lemmatizer_nltk_en import ProcessorLemmatizerNltkEn
from .processor_postagger_nltk_en import ProcessorPostaggerNltkEn
from .processor_tokenizer_nltk_en import ProcessorTokenizerNltkEn
from ..pipeline_common import PipelineCommon
from ..processor_sentence_splitter import ProcessorSentenceSplitter


def create_pipeline(delay_init=False):
    return PipelineCommon({'tokenizer': (ProcessorTokenizerNltkEn(),
                                         ['text'],
                                         {0: 'tokens'}),
                           'sentence_splitter': (ProcessorSentenceSplitter(),
                                                 ['tokens'],
                                                 {0: 'sentences'}),
                           'postagger': (ProcessorPostaggerNltkEn(),
                                         ['tokens', 'sentences'],
                                         {0: 'postag'}),
                           'lemmatizer': (ProcessorLemmatizerNltkEn(delay_init),
                                          ['tokens', 'sentences', 'postag'],
                                          {0: 'lemma'})},
                          name='default')
