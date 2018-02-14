from ..pipeline_common import PipelineCommon
from ..processor_sentence_splitter import ProcessorSentenceSplitter

from .processor_tokenizer_ru import ProcessorTokenizerRu
from .processor_mystem import ProcessorMystem


PIPELINE_DEFAULT = PipelineCommon({'tokenizer' : (ProcessorTokenizerRu(), 
                                                  ['text'], 
                                                  {0 : 'tokens'}),
                                   'sentence_splitter' : (ProcessorSentenceSplitter(), 
                                                          ['tokens'], 
                                                          {0 : 'sentences'}),
                                   'mystem' : (ProcessorMystem(),
                                               ['tokens', 'sentences'], 
                                               {'postag' : 'postag', 
                                                'lemma' : 'lemma'})
                                  },
                                  name = 'default')
