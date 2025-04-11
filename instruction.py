# instruction.py
# Defines the Instruction dataclass for bytecode instructions

from dataclasses import dataclass

@dataclass
class Instruction:
    opcode: int
    data: bytes

    def __str__(self):
        return f"Opcode: {hex(self.opcode)}, Data: {self.data.hex() if self.data else 'None'}"