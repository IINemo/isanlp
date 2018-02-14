from .ru import pipeline_default as dflt_ru
from .en import pipeline_default as dflt_en
from .pipeline_conditional import PipelineConditional
from .processor_polyglot import ProcessorPolyglot
from .pipeline_common import PipelineCommon


_ppl_cond = PipelineConditional((lambda _, lang: lang),
                                {'ru' : dflt_ru.PIPELINE_DEFAULT,
                                 'en' : dflt_en.PIPELINE_DEFAULT},
                                default_ppl = dflt_ru.PIPELINE_DEFAULT)


PIPELINE_DEFAULT = PipelineCommon([(ProcessorPolyglot().detect_language, 
                                    ['text'], 
                                    {0 : 'lang'}),
                                   (_ppl_cond, 
                                    ['text', 'lang'], 
                                    {'tokens' : 'tokens', 
                                     'sentences' : 'sentences',
                                     'postag' : 'postag',
                                     'lemma' : 'lemma'})],
                                  name = 'default')
