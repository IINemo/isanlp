from multiprocessing import current_process, Pool
import math


def _process_chunk(chunk, proc):
    return [proc(doc) for doc in chunk]

    
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
    

class WrapperMultiProcessDocument:
    def __init__(self, processors):
        self._processors = processors
        self._pool = Pool(len(self._processors))
    
    def __call__(self, args):
        chunks = split_equally(args, len(self._processors))
        
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