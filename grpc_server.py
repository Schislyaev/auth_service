from concurrent import futures

import grpc

from core.settings import settings
from grpc_src.messages import permissions_pb2_grpc
from grpc_src.services import PermissionService


def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=settings.grpc_max_workers))

    service = PermissionService()
    permissions_pb2_grpc.add_PermissionServicer_to_server(service, server)

    server.add_insecure_port(f'[::]:{settings.grpc_port}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    grpc_server()
