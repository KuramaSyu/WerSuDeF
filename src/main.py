import asyncio
import grpc
from grpc_mod import add_NoteServiceServicer_to_server, GRPCNoteService, GRPCUserService
from db.repos import NoteRepoABC, NotePostgreRepo
from db import Database
from db.repos.user.user import UserRepoABC, UserPostgresRepo
from grpc_mod.proto.user_pb2_grpc import add_UserServiceServicer_to_server


async def serve():
    # create server 
    server = grpc.aio.server()

    # connect to database
    db = Database(dsn="postgres://postgres:postgres@localhost:5433/db?sslmode=disable")
    await db.init_db()

    # note service
    repo: NotePostgreRepo = NotePostgreRepo(db=db)
    note_service = GRPCNoteService(repo=repo)
    add_NoteServiceServicer_to_server(note_service, server)

    # user service
    user_repo: UserRepoABC = UserPostgresRepo(db=db)
    user_service = GRPCUserService(user_repo=user_repo)
    add_UserServiceServicer_to_server(user_service, server)

    # configure server
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    print(f"gRPC server listening on {listen_addr}")

    # Start the server
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())