from . import annotation_pb2 as pb
from . import annotation_pb2_grpc
from . import annotation_to_protobuf
from . import annotation_from_protobuf

import grpc
import logging


logger = logging.getLogger('isanlp')


class NlpService(annotation_pb2_grpc.NlpServiceServicer):
    """Basic NLP gRPC annotation service.
    
    Args:
        ppls: dictionary {<pipeline name> : <pipeline object>}
    """
    
    def __init__(self, ppls):
        self._ppls = ppls
    
    def process(self, request, context):
        """(gRPC method) Processes text document with a specified pipeline.
        
        The request contains the name of a pipeline to invoke and required annotations.
        """
        
        logger.info('Processing incoming request with "{}"...'.format(request.pipeline_name))
        ppl = self._ppls[request.pipeline_name]
        input_annotations = annotation_from_protobuf.convert_annotation(request.input_annotations)
        res = ppl(*input_annotations)
        logger.info('Done.')
        
        pb_res = annotation_to_protobuf.convert_annotation(res)
        reply = pb.ProcessReply()
        reply.output_annotations.Pack(pb_res)
        
        return reply
    
    def get_registered_pipelines(self, request, context):
        """(gRPC method) Outputs pipelines registered in the service."""
        
        repl = RegisteredPipelinesReply()
        for e in self._ppl.keys():
            repl.add(e)
        return repl
    
    def add_to_server(self, server):
        """Is required for adding service to server.
        
        Is invoked by NlpServiceServer.
        """
        
        annotation_pb2_grpc.add_NlpServiceServicer_to_server(self, server)
