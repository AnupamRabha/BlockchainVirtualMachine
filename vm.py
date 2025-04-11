# vm.py
# Implements the Blockchain Virtual Machine (BVM) with dynamic storage keys

import copy
import logging
from typing import List, Dict, Set

from opcodes import CoolOps
from instruction import Instruction
from transaction import Receipt

logger = logging.getLogger(__name__)

class BVM:
    def __init__(self, bytecode: bytes, gas_limit: int, call_data: bytes, read_keys: Set[bytes], write_keys: Set[bytes]):
        logger.info("Initializing BVM")
        self.stack: List[int] = []
        self.storage: Dict[bytes, int] = {}
        self.pc: int = 0
        self.gas_limit: int = gas_limit
        self.gas_used: int = 0
        self.instructions: List[Instruction] = self.parse_bytecode(bytecode)
        self.running: bool = True
        self.failed: bool = False
        self.call_data: bytes = call_data
        self.logs: List[str] = []
        self.read_keys: Set[bytes] = read_keys
        self.write_keys: Set[bytes] = write_keys
        logger.info(f"Gas Limit: {self.gas_limit}, Instructions: {len(self.instructions)}")

    def gas_costs(self) -> Dict[int, int]:
        """Define gas costs for opcodes."""
        return {
            CoolOps.STOP: 0,
            CoolOps.PUSH1: 3,
            CoolOps.ADD: 3,
            CoolOps.SUB: 5,
            CoolOps.MUL: 5,   # New: Gas cost for MUL, similar to EVM
            CoolOps.SSTORE: 20000,  # Simplified; could be dynamic
            CoolOps.SLOAD: 200,
            CoolOps.JUMPI: 10,
            CoolOps.JUMP: 8,
        }

    def parse_bytecode(self, bytecode: bytes) -> List[Instruction]:
        """Parse bytecode into instructions."""
        logger.info("Parsing bytecode")
        instructions = []
        i = 0
        while i < len(bytecode):
            opcode = bytecode[i]
            if opcode == CoolOps.PUSH1:
                data = bytecode[i + 1:i + 2] if i + 1 < len(bytecode) else b"\x00"
                step = 2
            elif opcode in (CoolOps.SSTORE, CoolOps.SLOAD):
                data = bytecode[i + 1:i + 33] if i + 33 <= len(bytecode) else b"\x00" * 32
                if len(data) != 32:
                    logger.error("Invalid storage key length")
                    raise ValueError("Storage key must be 32 bytes")
                step = 33
            elif opcode in (CoolOps.JUMPI, CoolOps.JUMP):
                data = bytecode[i + 1:i + 3] if i + 3 <= len(bytecode) else b"\x00\x00"
                step = 3
            else:
                data = b""
                step = 1
            instruction = Instruction(opcode, data)
            instructions.append(instruction)
            logger.debug(f"Parsed: {instruction}")
            i += step
        return instructions

    def consume_gas(self, opcode: int) -> bool:
        """Consume gas for an opcode."""
        cost = self.gas_costs().get(opcode, 0)
        logger.debug(f"Consuming {cost} gas for opcode {hex(opcode)}")
        if self.gas_used + cost > self.gas_limit:
            self.fail("Out of gas")
            return False
        self.gas_used += cost
        logger.debug(f"Gas Used: {self.gas_used}, Remaining: {self.gas_limit - self.gas_used}")
        return True

    def fail(self, reason: str):
        """Mark execution as failed."""
        logger.error(f"Execution failed: {reason}")  
        self.running = False
        self.failed = True

    def step(self):
        """Execute one instruction."""
        if not self.running or self.pc >= len(self.instructions):
            logger.info("Execution complete or invalid PC")
            self.running = False
            return

        logger.debug(f"PC={self.pc}, Stack={self.stack}, Storage={self.storage}")
        instruction = self.instructions[self.pc]
        logger.info(f"Executing: {instruction}")

        if not self.consume_gas(instruction.opcode):
            return

        if instruction.opcode == CoolOps.STOP:
            logger.info("Stopping execution")
            self.running = False
        elif instruction.opcode == CoolOps.PUSH1:
            value = int.from_bytes(instruction.data, "big")
            self.stack.append(value)
            logger.debug(f"Pushed {value}")
            self.pc += 1
        elif instruction.opcode == CoolOps.ADD:
            if len(self.stack) >= 2:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
                logger.debug(f"Added {a} + {b} = {a + b}")
                self.pc += 1
            else:
                self.fail("Stack underflow")
        elif instruction.opcode == CoolOps.MUL:  # New: Handle MUL
            if len(self.stack) >= 2:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)
                logger.debug(f"Multiplied {a} * {b} = {a * b}")
                self.pc += 1
            else:
                self.fail("Stack underflow")
        elif instruction.opcode == CoolOps.SUB:
            if len(self.stack) >= 2:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)
                logger.debug(f"Subtracted {a} - {b} = {a - b}")
                self.pc += 1
            else:
                self.fail("Stack underflow")
        elif instruction.opcode == CoolOps.SSTORE:
            if len(self.stack) >= 1:
                value = self.stack.pop()
                key = instruction.data
                if key in self.write_keys:
                    self.storage[key] = value
                    self.logs.append(f"Stored {value} at {key.hex()}")
                    logger.info(f"Stored {value} at {key.hex()}")
                else:
                    self.fail(f"Write to unauthorized key {key.hex()}")
                self.pc += 1
            else:
                self.fail("Stack underflow")
        elif instruction.opcode == CoolOps.SLOAD:
            key = instruction.data
            if key in self.read_keys:
                value = self.storage.get(key, 0)
                self.stack.append(value)
                logger.debug(f"Loaded {value} from {key.hex()}")
                self.pc += 1
            else:
                self.fail(f"Read from unauthorized key {key.hex()}")
        elif instruction.opcode == CoolOps.JUMPI:
            if len(self.stack) >= 1:
                condition = self.stack.pop()
                dest = int.from_bytes(instruction.data, "big")
                if condition != 0 and 0 <= dest < len(self.instructions):
                    logger.debug(f"Jumping to PC={dest}")
                    self.pc = dest
                else:
                    logger.debug("No jump")
                    self.pc += 1
            else:
                self.fail("Stack underflow")
        elif instruction.opcode == CoolOps.JUMP:
            dest = int.from_bytes(instruction.data, "big")
            if 0 <= dest < len(self.instructions):
                logger.debug(f"Jumping to PC={dest}")
                self.pc = dest
            else:
                self.fail(f"Invalid jump destination {dest}")
        else:
            self.fail(f"Unknown opcode {hex(instruction.opcode)}")

    def execute(self) -> Receipt:
        """Execute all instructions and return a receipt."""
        logger.info("Starting execution")
        # logger.debug(f"Stack before transaction(vm): {self.stack}")  # Log stack before
        while self.running:
            self.step()
        # logger.debug(f"Stack after transaction(vm): {self.stack}")  # Log stack after
        return Receipt(
            success=not self.failed,
            gas_used=self.gas_used,
            logs=self.logs,
            storage=copy.deepcopy(self.storage)
        )