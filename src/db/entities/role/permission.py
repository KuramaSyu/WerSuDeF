from enum import Flag, auto

class RolePermission(Flag):
    READ = auto()       #0b0001
    WRITE = auto()      #0b0010
    EXECUTE = auto()    #0b0100
    ALL = READ | WRITE | EXECUTE