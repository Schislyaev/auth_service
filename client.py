import grpc

from grpc_src.messages import permissions_pb2, permissions_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = permissions_pb2_grpc.PermissionStub(channel)
        response = stub.CheckPermission(permissions_pb2.PermissionRequest(token="123123123", url='/shrek'))
        print(response)


if __name__ == '__main__':
    run()
