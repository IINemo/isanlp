import multiprocessing

from . import annotation_pb2 as pb
from . import annotation_pb2_grpc
from . import annotation_to_protobuf
from . import annotation_from_protobuf
from .pipeline_common import PipelineCommon

import grpc

import logging
logger = logging.getLogger('isanlp')


def _expand_ppl(ppl):
    res_dict = {k : v[0] for k, v in ppl.get_processors().items()}
    return res_dict


PPLS = None
def _init_process(ppls):
    global PPLS
    PPLS = ppls
    standalone_procs = {}
    for ppl in ppls.values():
        if not isinstance(ppl, PipelineCommon):
            continue
        for proc in ppl.processors_iter():
            if hasattr(proc, 'init'):
                proc.init()
        standalone_procs.update(_expand_ppl(ppl))
    PPLS.update(standalone_procs)

    
def _process_input(ppl_name, input_annotations):
    ppl = PPLS[ppl_name]
    print(ppl_name, ppl)
    return ppl(*input_annotations)


class NlpService(annotation_pb2_grpc.NlpServiceServicer):
    """Basic NLP gRPC annotation service.

    Args:
        ppls: dictionary {<pipeline name> : <pipeline object>}
    """

    def __init__(self, ppls, max_workers=1, no_multiprocessing=False):
        self._pool = None
        if no_multiprocessing:
            _init_process(ppls)
        else:
            #multiprocessing.set_start_method('spawn', force=True) # TODO: Fix multiprocessing for pytorch
            self._pool = multiprocessing.Pool(processes=max_workers,
                                              initializer=_init_process,
                                              initargs=(ppls,))

    def process(self, request, context):
        """(gRPC method) Processes text document with a specified pipeline.

        The request contains the name of a pipeline to invoke and required annotations.
        """
        input_annotations = annotation_from_protobuf.convert_annotation(request.input_annotations)

        logger.info('Processing incoming request with "{}"...'.format(request.pipeline_name))
        if self._pool is not None:
            res = self._pool.apply(_process_input, args=(request.pipeline_name, input_annotations))
        else:
            res = _process_input(request.pipeline_name, input_annotations)
        logger.info('Processing completed.')
        
        pb_res = annotation_to_protobuf.convert_annotation(res)
        reply = pb.ProcessReply()
        reply.output_annotations.Pack(pb_res)

        return reply

    def get_registered_pipelines(self, request, context):
        """(gRPC method) Outputs pipelines registered in the service."""

        repl = RegisteredPipelinesReply()
        #for e in self._ppl.keys():
        for e in PPLS.keys():
            repl.add(e)
        return repl

    def add_to_server(self, server):
        """Is required for adding service to server.

        Is invoked by NlpServiceServer.
        """

        annotation_pb2_grpc.add_NlpServiceServicer_to_server(self, server)
