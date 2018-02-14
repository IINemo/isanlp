class PipelineConditional:
    def __init__(self, condition, ppl_dict, default_ppl = None):
        self._condition = condition
        self._ppl_dict = ppl_dict
        self._default = default_ppl
    
    def __call__(self, *args):
        cond_res = self._condition(*args)
        
        for key, ppl in self._ppl_dict.items():
            if cond_res == key:
                return ppl(*args)
        
        if self._default is not None:
            return self._default(*args)
        
        raise RuntimeError('No such option: {}.'.format(cond_res))
        