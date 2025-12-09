import logging
from logging import getLogger, basicConfig
import sys

import asyncio
from typing import Optional, Callable
import grpc
from colorama import Fore, Style, init


from ai.embedding_generator import EmbeddingGenerator, Models
from db import table
from db.repos import NoteRepoFacadeABC, NoteRepoFacade
from db import Database
from db.repos.note.embedding import NoteEmbeddingPostgresRepo
from db.repos.note.permission import NotePermissionPostgresRepo
from db.repos.user.user import UserRepoABC, UserPostgresRepo
from db.table import Table, setup_table_logging
from grpc_mod.proto.user_pb2_grpc import add_UserServiceServicer_to_server
from grpc_mod import add_NoteServiceServicer_to_server, GrpcNoteService, GrpcUserService
from db.repos.note.content import NoteContentPostgresRepo


def logging_provider(file: str, cls_instance: Optional[object] = None) -> logging.Logger:
    """provides a logger for the given file and class name"""
    logger_name = f"{file}"
    if cls_instance:
        logger_name += f".{cls_instance.__class__.__qualname__}"
    log = getLogger(logger_name)
    log.setLevel(logging.DEBUG)

        # Colored formatter for stdout
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA,
        }
        
        def format(self, record):
            levelname = record.levelname[0]  # First letter only
            color = self.COLORS.get(record.levelname, '')
            
            # For DEBUG, use thin text for message
            if record.levelname == 'DEBUG':
                record.levelname = f"{Style.BRIGHT}{color}{levelname}{Style.RESET_ALL}"
                formatted = super().format(record)
                # Apply dim white to message only (after the last ": ")
                parts = formatted.split(': ', 1)
                if len(parts) == 2:
                    return Style.BRIGHT + parts[0] + Style.RESET_ALL + ': ' + Style.DIM + Fore.WHITE + parts[1] + Style.RESET_ALL
                return formatted
            else:
                record.levelname = f"{Style.BRIGHT}{color}{levelname}{Style.RESET_ALL}"
                formatted = super().format(record)
                # Make everything before message bright, message grey
                parts = formatted.split(': ', 1)
                if len(parts) == 2:
                    return Style.BRIGHT + parts[0] + Style.RESET_ALL + ': ' + Fore.LIGHTBLACK_EX + parts[1] + Style.RESET_ALL
                return formatted


    # common format
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s: %(message)s"
    )

    # file handler
    file_handler = logging.FileHandler("grpc_server.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # stdout handler (with colors)
    stdout_formatter = ColoredFormatter(
        "%(levelname)s %(asctime)s %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(stdout_formatter)

    # attach both
    log.addHandler(file_handler)
    log.addHandler(stdout_handler)
    return log



async def serve():
    # setup logging
    log = logging_provider(__name__)
    setup_table_logging(logging_provider)

    # create server 
    server = grpc.aio.server()

    # connect to database
    log.info("Connecting to database...")
    db = Database(
        dsn="postgres://postgres:postgres@localhost:5433/db?sslmode=disable",
        log=logging_provider
    )
    await db.init_db()

    # setup db tables and their primary keys
    log.info("Setting up database tables...")
    common_table_kwargs = {"db": db, "logging_provider": logging_provider}
    content_table = Table(
        **common_table_kwargs, 
        table_name="note.content", 
        id_fields=["id"]
    )
    permission_table = Table(
        **common_table_kwargs, 
        table_name="note.permission", 
        id_fields=["note_id", "role_id"]
    )
    embedding_table = Table(
        **common_table_kwargs,
        table_name="note.embedding",
        id_fields=["note_id", "model"]
    )

    # setup note repo via DI
    log.info("Setting up NoteRepoFacade, sub repos and embedding generator...")
    repo: NoteRepoFacade = NoteRepoFacade(
        db=db,
        content_repo=NoteContentPostgresRepo(content_table),
        embedding_repo=NoteEmbeddingPostgresRepo(
            table=embedding_table,
            embedding_generator=EmbeddingGenerator(
                model_name=Models.MINI_LM_L6_V2, 
                logging_provider=logging_provider
            )
        ),
        permission_repo=NotePermissionPostgresRepo(permission_table),
    )

    # setup gRPC note service
    log.info("Setting up gRPC services...")
    note_service = GrpcNoteService(repo=repo, log=logging_provider)
    add_NoteServiceServicer_to_server(note_service, server)

    # setup gRPC user service
    user_repo: UserRepoABC = UserPostgresRepo(db=db)
    user_service = GrpcUserService(user_repo=user_repo, log=logging_provider)
    add_UserServiceServicer_to_server(user_service, server)

    # configure server
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    log.info(f"gRPC server listening on {listen_addr}")

    # Start the server
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())