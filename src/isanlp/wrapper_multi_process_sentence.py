from multiprocessing import current_process, Pool
import math


def _process_chunk(chunk, proc):
    return proc(*chunk)

    
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
    

class WrapperMultiProcessSentence:
    """Executes processors or pipelines in parallel on different chunks of sentences.
    
    The function splits input sentence axis into chunks, executes processors or pipelines on chunks and
    finally aggregates data as it was a result of a single process/pipeline.
    
    Args:
        processors(list): The list of processor objects for each thread (process). All processors
            should aquire and return similar result formats.
        split_annotations(list): List of numbers of arguments that should be split by sentences.
    """
    
    def __init__(self, processors, split_annotations):
        self._processors = processors
        self._split_annotations = split_annotations
        self._pool = Pool(len(self._processors))
    
    def _make_chunks(self, split_annotations, args):
        axises = []
        n_chunks = len(split_equally(args[split_annotations[0]], len(self._processors)))
        
        for axis in range(len(args)):
            if axis in split_annotations:
                axises.append(split_equally(args[axis], len(self._processors)))    
            else:
                axises.append([args[axis]] * n_chunks)
                
        return list(zip(*tuple(axises)))
    
    def __call__(self, *args):
        chunks = self._make_chunks(self._split_annotations, args)
        
        async_results = []
        for i in range(len(chunks)):
            async_results.append(self._pool.apply_async(_process_chunk, 
                                                        args = (chunks[i], 
                                                                self._processors[i])))
        
        result = None
        for i in range(len(chunks)):
            res = async_results[i].get()
            if type(res) is list:
                if result is None:
                    result = []
                result += res
            elif type(res) is tuple:
                if result is None:
                    result = res
                else:
                    for result_axis, res_axis in zip(result, res):
                        result_axis += res_axis
            elif type(res) is dict:
                if result is None:
                    result = res
                else:
                    for k,v in res.items():
                        result[k] += v
            
        return result
