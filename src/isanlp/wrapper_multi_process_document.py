from multiprocessing import current_process, Pool
import math
import tqdm


def _process_chunk(chunk, proc):
    result = []
    for doc_num, doc in enumerate(chunk):
        result.append(proc(doc))
        if (doc_num % 100) == 0:
            print('{}: {:.2f}%'.format(current_process(), 
                                       (doc_num / len(chunk)) * 100))
    
    return result

    
def split_equally(lst, nparts):
    """Splits equally list into nparts. 
    
    If length of the list cannot be devided without residue the functions splits list in the way
    when some parts have n items and some n-1, so lengths of them are almost equal.
    """
    
    data_size = len(lst)
    ratio = data_size / nparts
    if ratio < 1.:
        return [[e] for e in lst]
    
    chunk_size = int(math.ceil(ratio))
    new_size = chunk_size * nparts - data_size
    chunks = []
    if new_size > 0:
        chunks += [lst[x : x + chunk_size - 1] for x in range(0, new_size * (chunk_size - 1), chunk_size - 1)]
    chunks += [lst[x : x + chunk_size] for x in range((chunk_size - 1) * new_size, len(lst), chunk_size)]
    return chunks
    

global_proc = None
def _initialize(processors):
    global global_proc
    global_proc = processors[current_process()._identity[0] % len(processors)]

    
def _perform_analysis(arg):
    return arg[0], global_proc(arg[1])


class WrapperMultiProcessDocument:
    def __init__(self, 
                 processors, 
                 ptype='balanced', 
                 chunksize=10,
                 progress_bar=tqdm.tqdm):
        """
        Args:
            processors(list): 
            ptype(str): balanced, even
        """
        
        self._processors = processors
        self._ptype = ptype
        self._chunksize = chunksize
        self._progress_bar = progress_bar
        
        if self._ptype == 'balanced':
            self._pool = Pool(len(self._processors), 
                              initializer = _initialize, 
                              initargs = (self._processors,))
        elif self._ptype == 'even':
            self._pool = Pool(len(self._processors))
        else:
            raise ValueError()
        
    def _even_parallelization(self, lst):
        return self._pool.imap_unordered(_perform_analysis, 
                                         list(enumerate(lst)),
                                         self._chunksize)
    
    def __call__(self, lst):
        if self._ptype == 'balanced':
            final_res = [None for i in range(len(lst))]
            if self._progress_bar is None:
                results = self._even_parallelization(lst)
            else:
                results = self._progress_bar(self._even_parallelization(lst), total=len(lst))
                
            for i, res in results:
                final_res[i] = res

            return final_res
        
        elif self._ptype == 'even':
            chunks = split_equally(lst, len(self._processors))
        
            async_results = []
            for i in range(len(chunks)):
                async_results.append(self._pool.apply_async(_process_chunk, 
                                                            args = (chunks[i], 
                                                                    self._processors[i])))

            result = []
            for i in range(len(chunks)):
                res = async_results[i].get()
                result += res

            return result
    