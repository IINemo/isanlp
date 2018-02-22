from . import annotation_pb2
from . import annotation_pb2_grpc
from . import annotation_to_protobuf
from . import annotation_from_protobuf

import grpc
from google.protobuf.any_pb2 import Any
import copy


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
    
    def __getstate__(self):
        # capture what is normally pickled
        #state = copy.deepcopy(self.__dict__)
        state = self.__dict__.copy()
        # replace the `value` key (now an EnumValue instance), with it's index:
        del state['_channel']
        # what we return here will be stored in the pickle
        del state['_stub']
        return state
    
    def __setstate__(self, newstate):
        # re-create the EnumState instance based on the stored index
        #newstate['_channel'] = grpc.insecure_channel('{}:{}'.format(newstate['_host'], newstate['_port']))
        self._channel = grpc.insecure_channel('{}:{}'.format(newstate['_host'], newstate['_port']))
        #newstate['_stub'] = annotation_pb2_grpc.NlpServiceStub(newstate['_channel'])
        self._stub = annotation_pb2_grpc.NlpServiceStub(self._channel)
        # re-instate our __dict__ state from the pickled state
        self.__dict__.update(newstate)
