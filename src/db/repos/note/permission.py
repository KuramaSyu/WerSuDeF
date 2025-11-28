from abc import ABC, abstractmethod
from entities import NotePermissionEntity

class NotePermissionRepo(ABC):

    @abstractmethod
    async def insert(
        self,
        permission: NotePermissionEntity,
    ) -> NotePermissionEntity:
        """inserts permission
        
        Args:
        -----
        permission: `NotePermissionEntity`
            the permission of a note

        Returns:
        --------
        `NotePermissionEntity`:
            the updated entity (updated ID)
        """
        ...

    @abstractmethod
    async def update(
        self,
        permission: NotePermissionEntity,
    ) -> NotePermissionEntity:
        """updates permission
        
        Args:
        -----
        permission: `NotePermissionEntity`
            the permission of a note

        Returns:
        --------
        `NotePermissionEntity`:
            the updated entity
        """
        ...

    @abstractmethod
    async def delete(
        self,
        permission: NotePermissionEntity,
    ) -> NotePermissionEntity:
        """delete permission
        
        Args:
        -----
        permission: `NotePermissionEntity`
            the permission of a note

        Returns:
        --------
        `NotePermissionEntity`:
            the updated entity
        """
        ...


    @abstractmethod
    async def select(
        self,
        permission: NotePermissionEntity,
    ) -> NotePermissionEntity:
        """select permission
        
        Args:
        -----
        permission: `NotePermissionEntity`
            the permission of a note

        Returns:
        --------
        `NotePermissionEntity`:
            the updated entity
        """
        ...

    

    