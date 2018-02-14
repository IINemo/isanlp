from . import annotation_pb2
from . import annotation_pb2_grpc
from . import annotation_to_protobuf
from . import annotation_from_protobuf

import grpc
from google.protobuf.any_pb2 import Any


class ProcessorRemote:
    """Calls remote pipeline using gRPC.
    
    Args:
        host(str): hostname of the gRPC server.
        port(int): port of the gRPC server.
        pipeline_name(str): name of the registered pipeline (or processor) to invoke.
    """
    
    def __init__(self, host, port, pipeline_name):
        self._host = host
        self._port = port
        self._pipeline_name = pipeline_name
        self._channel = grpc.insecure_channel('{}:{}'.format(self._host, self._port))
        self._stub = annotation_pb2_grpc.NlpServiceStub(self._channel)
    
    def __call__(self, *input_data):
        """ Calls remote pipeline via gRPC.
        
        Args:
            *input_data: the input data for the remote pipeline.
        
        Returns:
            Result of the remote pipeline.
        """
        
        pb_ann = Any()
        pb_ann.Pack(annotation_to_protobuf.convert_annotation(input_data))
        request = annotation_pb2.ProcessRequest(pipeline_name = self._pipeline_name, 
                                                input_annotations = pb_ann)
        
        response = self._stub.process(request)
        return annotation_from_protobuf.convert_annotation(response.output_annotations)
