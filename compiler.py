# compiler.py
# Implements compilers for C, Java, and C++ contracts with basic operations

import re
import hashlib
from typing import Tuple, Optional, Dict, Set
import logging

from opcodes import CoolOps

logger = logging.getLogger(__name__)

class Compiler:
    @staticmethod
    def brew(code: str) -> Tuple[bytes, int, Optional[str], Set[bytes], Set[bytes]]:
        """Base method for compiling code, returning bytecode, gas, error, read_keys, write_keys."""
        raise NotImplementedError

class CCompiler(Compiler):
    @staticmethod
    def brew(code: str) -> Tuple[bytes, int, Optional[str], Set[bytes], Set[bytes]]:
        logger.info("Compiling contract")
        bytecode = bytearray()
        gas_cost = 0
        read_keys: Set[bytes] = set()
        write_keys: Set[bytes] = set()

        # Find any function body (C, Java, or C++ syntax)
        func_match = re.search(r"(void\s+\w+\s*\(\s*\)\s*\{([^}]*)\})|" \
                               r"(public\s+\w+\s+\w+\s*\(\s*\)\s*\{([^}]*)\})", code, re.DOTALL)
        if not func_match:
            return b"", 0, "No valid function found (e.g., 'void myFunc() {...}')", set(), set()

        func_body = (func_match.group(2) or func_match.group(4)).strip()
        if not func_body:
            return b"", 0, "Function body is empty", set(), set()

        # Split statements, preserving structure within braces
        def split_statements(body: str) -> list:
            statements = []
            buffer = ""
            brace_count = 0
            for char in body:
                if char == '{':
                    brace_count += 1
                    buffer += char
                elif char == '}':
                    brace_count -= 1
                    buffer += char
                elif char == ';' and brace_count == 0:
                    if buffer.strip():
                        statements.append(buffer.strip())
                    buffer = ""
                else:
                    buffer += char
            if buffer.strip():  # Catch any remaining statement
                statements.append(buffer.strip())
            return statements

        statements = split_statements(func_body)
        logger.debug(f"Parsed statements: {statements}")

        # Track variables and their storage keys
        var_to_key: Dict[str, bytes] = {}

        def get_storage_key(var_name: str) -> bytes:
            """Generate a 32-byte storage key from variable name."""
            if var_name not in var_to_key:
                key = hashlib.sha256(var_name.encode()).digest()
                var_to_key[var_name] = key
            return var_to_key[var_name]

        for stmt in statements:
            logger.debug(f"Processing statement: '{stmt}'")

            # Assignment with addition (e.g., x = 10 + 20)
            add_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\+\s*(\d+)", stmt)
            if add_match:
                var, a, b = add_match.groups()
                a, b = int(a), int(b)
                key = get_storage_key(var)
                bytecode.extend([CoolOps.PUSH1, a])
                gas_cost += 3
                bytecode.extend([CoolOps.PUSH1, b])
                gas_cost += 3
                bytecode.append(CoolOps.ADD)
                gas_cost += 3
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(key)
                gas_cost += 20000
                write_keys.add(key)
                logger.debug(f"Compiled {var} = {a} + {b} at {key.hex()}")
                continue

            # Assignment with subtraction (e.g., x = 30 - 15)
            sub_match = re.match(r"(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", stmt)
            if sub_match:
                var, a, b = sub_match.groups()
                a, b = int(a), int(b)
                key = get_storage_key(var)
                bytecode.extend([CoolOps.PUSH1, a])
                gas_cost += 3
                bytecode.extend([CoolOps.PUSH1, b])
                gas_cost += 3
                bytecode.append(CoolOps.SUB)
                gas_cost += 5
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(key)
                gas_cost += 20000
                write_keys.add(key)
                logger.debug(f"Compiled {var} = {a} - {b} at {key.hex()}")
                continue

            # Assignment from variable (e.g., x = y)
            assign_match = re.match(r"(\w+)\s*=\s*(\w+)", stmt)
            if assign_match:
                target, source = assign_match.groups()
                if target == source:
                    continue  # Skip self-assignment
                target_key = get_storage_key(target)
                source_key = get_storage_key(source)
                bytecode.append(CoolOps.SLOAD)
                bytecode.extend(source_key)
                gas_cost += 200
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(target_key)
                gas_cost += 20000
                read_keys.add(source_key)
                write_keys.add(target_key)
                logger.debug(f"Compiled {target} = {source}")
                continue

            if stmt:  # Non-empty unsupported statement
                return b"", 0, f"Unsupported statement: {stmt}", read_keys, write_keys

        bytecode.append(CoolOps.STOP)
        gas_cost += 0
        logger.info(f"Compiled bytecode: {bytecode.hex()}, Gas: {gas_cost}")
        return bytes(bytecode), gas_cost, None, read_keys, write_keys

class JavaCompiler(CCompiler):
    pass

class CppCompiler(CCompiler):
    pass