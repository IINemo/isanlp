import grpc
import time
from concurrent import futures
from .nlp_service import NlpService


class NlpServiceServer:
    """Implements gRPC server for NLP annotation service.

    Args:
        ppl(dict): Dictionary of pipelines that will be registered in the service.
        port(int): Serving port.
        max_workers(int): workers for gRPC server.
    """

    def __init__(self, ppls, port = 3333, max_workers = 1, no_multiprocessing=False):
        self._port = port
        self._max_workers = max_workers
        self._service = NlpService(ppls, max_workers, no_multiprocessing)

    def serve(self):
        """Initiates server for listening of incoming connections (blocking)."""

        server = grpc.server(futures.ThreadPoolExecutor(max_workers = self._max_workers))

        self._service.add_to_server(server)
        server.add_insecure_port('[::]:{}'.format(self._port))
        server.start()

        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            server.stop(0)
