from .ru import pipeline_default as dflt_ru
from .en import pipeline_default as dflt_en
from .pipeline_conditional import PipelineConditional
from .processor_polyglot import ProcessorPolyglot
from .pipeline_common import PipelineCommon


def create_pipeline(delay_init = False):
    ru_ppl = dflt_ru.create_pipeline(delay_init)
    _ppl_cond = PipelineConditional((lambda _, lang: lang),
                                    {'ru' : ru_ppl,
                                     'en' : dflt_en.create_pipeline(delay_init)},
                                    default_ppl = ru_ppl)

    ppl = PipelineCommon([(ProcessorPolyglot().detect_language,
                           ['text'],
                           {0 : 'lang'}),
                          (_ppl_cond,
                           ['text', 'lang'],
                           {'tokens' : 'tokens',
                            'sentences' : 'sentences',
                            'postag' : 'postag',
                            'lemma' : 'lemma'})],
                         name = 'default')


    return ppl
