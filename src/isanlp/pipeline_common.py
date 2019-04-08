class PipelineCommon:
    """The common pipeline of several processors.
    
    The pipeline provides an ablity to specify its structure in a declarative way. It requires that all 
    its processors are callable (implement __call__ method). The pipeline can contain processors, 
    remote gRPC processors, or other pipelines. During processing the pipeline stores the results in a dictionary. If
    processor returns None, results are ommited.
    Args:
        processors(list or dict): A list or a dictionary ({<name> : <processor>}) that contains tripples: 
            (<processor object>, <list of names of input annotations>, <dictionary of output annotations>).
            Dictionary of output annotations should specify name/ordianl number of annotation in dictioanry/tuple 
            returned from processor. This is needed for storing the result annotation in an internal dictionary.
            If name or number is ommited then result will not be stored in a piplene and will be dropped from further
            processing.
        name(str): The name of the pipeline. It is used for automatic pipeline naming in a gRPC server container.
        
    Examples:
        1.
        PipelineCommon([(ProcessorTokenizerNltkEn(), ['text'], {0 : 'tokens'}),
                        (ProcessorSentenceSplitter(), ['tokens'], {0 : 'sentences'}),
                        (ProcessorPostaggerNltkEn(), ['tokens', 'sentences'], {0 : 'postag'}),
                        (ProcessorLemmatizerNltkEn(), ['tokens', 'sentences', 'postag'], {0 : 'lemma'})])
        
        2.
        PipelineCommon([(ProcessorRemote(host = 'some_host', port = 3333, pipeline_name = 'main'), 
                         ['text'], 
                         {'tokens' : 'tokens', 
                          'sentences' : 'sentences',
                          'postags' : 'postags',
                          'morph' : 'morph'}),
                        (ProcessorSyntaxNetRemote('some_host', 7777),
                         ['tokens', 'sentences'],
                         {'syntax_dep_tree' : 'syntax_dep_tree',
                          'morph' : 'morph'})])
         
        3.         
        PipelineCommon({'tokenizer' : (ProcessorTokenizerNltkEn(), 
                                       ['text'], 
                                       {0 : 'tokens'}),
                        'sentence_splitter' : (ProcessorSentenceSplitter(), 
                                               ['tokens'], 
                                               {0 : 'sentences'}),
                        'postagger' : (ProcessorPostaggerNltkEn(), 
                                       ['tokens', 'sentences'], 
                                       {0 : 'postag'}),
                        'lemmatizer' : (ProcessorLemmatizerNltkEn(), 
                                        ['tokens', 'sentences', 'postag'], 
                                        {0 : 'lemma'})}, 
                       name = 'main')
                       
        4. 
        PipelineCommon([(ProcessorTokenizerNltkEn(), ['text'], {'tokens' : 'tokens'}),
                        (ProcessorSentenceSplitter(), ['tokens'], {'sentences' : 'sentences'}),
                        (ProcessorPostaggerNltkEn(), ['sentences'], {'postag' : 'postag'}),
                        (WrapperMultiProcessSentence([ProcessorPostaggerNltkEn() for i in range(4)]), 
                                                     ['sentences'], {'postag' : 'postag'}),
                        (WrapperMultiProcessSentence([ProcessorLemmatizerNltkEn() for i in range(4)]), 
                                                     ['sentences', 'postag'], {'lemma' : 'lemma'}),
                        (ProcessorSyntaxNetRemote('some_host', 8555), ['sentences'], 
                         {'morph' : 'morph', 'syn_dep_tree' : 'syn_dep_tree'})])
    """
    
    def __init__(self, processors, name = 'main'):
        self._name = name
        if type(processors) is dict:
            self._processors = processors
        else:
            self._processors = {str(i) : processors[i] for i in range(len(processors))}
        
    def __call__(self, *input_data):            
        result = {e : inp for (e, inp) in zip(list(self._processors.values())[0][1], input_data)}
        
        for proc, proc_input, proc_output in list(self._processors.values()):
            results = proc(*[result[e] for e in proc_input])
            if type(results) is tuple:
                results = {i : results[i] for i in range(len(results))}
            elif type(results) is not dict:
                results = {0 : results}
            
            result.update({ppl_label : results[proc_label] 
                           for (proc_label, ppl_label) in proc_output.items() 
                           if ppl_label})
            
            keys_to_delete = [k for (k,v) in result.items() if v is None]
            for k in keys_to_delete:
                del result[k]
        
        return result

    def get_processors(self):
        return self._processors

    def processors_iter(self):
        for proc_stuff in self._processors.values():
            proc = proc_stuff[0]
            if hasattr(proc, 'processors_iter'):
                yield from proc.processors_iter()
            else:
                yield proc
