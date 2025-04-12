# # compiler.py
# # Implements compilers for C, Java, and C++ contracts with basic operations
# # compiler.py
# # Implements compilers for C, Java, C++, and Solidity contracts with basic operations

# import re
# import hashlib
# from typing import Tuple, Optional, Dict, Set
# import logging

# from opcodes import CoolOps

# logger = logging.getLogger(__name__)

# class Compiler:
#     @staticmethod
#     def brew(code: str) -> Tuple[bytes, int, Optional[str], Set[bytes], Set[bytes]]:
#         """Base method for compiling code, returning bytecode, gas, error, read_keys, write_keys."""
#         raise NotImplementedError

# class CCompiler(Compiler):
#     @staticmethod
#     def brew(code: str) -> Tuple[bytes, int, Optional[str], Set[bytes], Set[bytes]]:
#         logger.info("Compiling C contract")
#         bytecode = bytearray()
#         gas_cost = 0
#         read_keys: Set[bytes] = set()
#         write_keys: Set[bytes] = set()

#         # Find any function body (C, Java, or C++ syntax)
#         func_match = re.search(r"(void\s+\w+\s*\(\s*\)\s*\{([^}]*)\})|" \
#                                r"(public\s+\w+\s+\w+\s*\(\s*\)\s*\{([^}]*)\})", code, re.DOTALL)
#         if not func_match:
#             return b"", 0, "No valid function found (e.g., 'void myFunc() {...}')", set(), set()

#         func_body = (func_match.group(2) or func_match.group(4)).strip()
#         if not func_body:
#             return b"", 0, "Function body is empty", set(), set()

#         # Split statements, preserving structure within braces
#         def split_statements(body: str) -> list:
#             statements = []
#             buffer = ""
#             brace_count = 0
#             for char in body:
#                 if char == '{':
#                     brace_count += 1
#                     buffer += char
#                 elif char == '}':
#                     brace_count -= 1
#                     buffer += char
#                 elif char == ';' and brace_count == 0:
#                     if buffer.strip():
#                         statements.append(buffer.strip())
#                     buffer = ""
#                 else:
#                     buffer += char
#             if buffer.strip():  # Catch any remaining statement
#                 statements.append(buffer.strip())
#             return statements

#         statements = split_statements(func_body)
#         logger.debug(f"Parsed statements: {statements}")

#         # Track variables and their storage keys
#         var_to_key: Dict[str, bytes] = {}

#         def get_storage_key(var_name: str) -> bytes:
#             """Generate a 32-byte storage key from variable name."""
#             if var_name not in var_to_key:
#                 key = hashlib.sha256(var_name.encode()).digest()
#                 var_to_key[var_name] = key
#             return var_to_key[var_name]

#         for stmt in statements:
#             logger.debug(f"Processing statement: '{stmt}'")

#             # Assignment with addition (e.g., x = 10 + 20)
#             add_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\+\s*(\d+)", stmt)
#             if add_match:
#                 var, a, b = add_match.groups()
#                 a, b = int(a), int(b)
#                 key = get_storage_key(var)
#                 bytecode.extend([CoolOps.PUSH1, a])
#                 gas_cost += 3
#                 bytecode.extend([CoolOps.PUSH1, b])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.ADD)
#                 gas_cost += 3
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(key)
#                 gas_cost += 20000
#                 write_keys.add(key)
#                 logger.debug(f"Compiled {var} = {a} + {b} at {key.hex()}")
#                 continue

#             # Assignment with subtraction (e.g., x = 30 - 15)
#             sub_match = re.match(r"(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", stmt)
#             if sub_match:
#                 var, a, b = sub_match.groups()
#                 a, b = int(a), int(b)
#                 key = get_storage_key(var)
#                 bytecode.extend([CoolOps.PUSH1, a])
#                 gas_cost += 3
#                 bytecode.extend([CoolOps.PUSH1, b])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.SUB)
#                 gas_cost += 5
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(key)
#                 gas_cost += 20000
#                 write_keys.add(key)
#                 logger.debug(f"Compiled {var} = {a} - {b} at {key.hex()}")
#                 continue
#             # Assignment with multiplication (e.g., x = 10 * 20)
#             mul_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\*\s*(\d+)", stmt)
#             if mul_match:
#                 var, a, b = mul_match.groups()
#                 a, b = int(a), int(b)
#                 key = get_storage_key(var)
#                 bytecode.extend([CoolOps.PUSH1, a])
#                 gas_cost += 3
#                 bytecode.extend([CoolOps.PUSH1, b])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.MUL)
#                 gas_cost += 5
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(key)
#                 gas_cost += 20000
#                 write_keys.add(key)
#                 logger.debug(f"Compiled {var} = {a} * {b} at {key.hex()}")
#                 continue
#             # Assignment from variable (e.g., x = y)
#             assign_match = re.match(r"(\w+)\s*=\s*(\w+)", stmt)
#             if assign_match:
#                 target, source = assign_match.groups()
#                 if target == source:
#                     continue  # Skip self-assignment
#                 target_key = get_storage_key(target)
#                 source_key = get_storage_key(source)
#                 bytecode.append(CoolOps.SLOAD)
#                 bytecode.extend(source_key)
#                 gas_cost += 200
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(target_key)
#                 gas_cost += 20000
#                 read_keys.add(source_key)
#                 write_keys.add(target_key)
#                 logger.debug(f"Compiled {target} = {source}")
#                 continue

#             if stmt:  # Non-empty unsupported statement
#                 return b"", 0, f"Unsupported statement: {stmt}", read_keys, write_keys

#         bytecode.append(CoolOps.STOP)
#         gas_cost += 0
#         logger.info(f"Compiled bytecode: {bytecode.hex()}, Gas: {gas_cost}")
#         return bytes(bytecode), gas_cost, None, read_keys, write_keys

# class JavaCompiler(CCompiler):
#     pass

# class CppCompiler(CCompiler):
#     pass

# class SolidityCompiler(Compiler):
#     @staticmethod
#     def brew(code: str) -> Tuple[bytes, int, Optional[str], Set[bytes], Set[bytes]]:
#         logger.info("Compiling Solidity contract")
#         bytecode = bytearray()
#         gas_cost = 0
#         read_keys: Set[bytes] = set()
#         write_keys: Set[bytes] = set()

#         # Find the calc function in Solidity syntax
#         func_match = re.search(r"function\s+calc\s*\(\s*\)\s*public\s*\{([^}]*)\}", code, re.DOTALL)
#         if not func_match:
#             return b"", 0, "No 'function calc() public {...}' found in Solidity code", set(), set()

#         func_body = func_match.group(1).strip()
#         if not func_body:
#             return b"", 0, "Function calc() body is empty", set(), set()

#         # Split statements, similar to CCompiler
#         def split_statements(body: str) -> list:
#             statements = []
#             buffer = ""
#             brace_count = 0
#             for char in body:
#                 if char == '{':
#                     brace_count += 1
#                     buffer += char
#                 elif char == '}':
#                     brace_count -= 1
#                     buffer += char
#                 elif char == ';' and brace_count == 0:
#                     if buffer.strip():
#                         statements.append(buffer.strip())
#                     buffer = ""
#                 else:
#                     buffer += char
#             if buffer.strip():
#                 statements.append(buffer.strip())
#             return statements

#         statements = split_statements(func_body)
#         logger.debug(f"Parsed Solidity statements: {statements}")

#         # Track variables and their storage keys
#         var_to_key: Dict[str, bytes] = {}

#         def get_storage_key(var_name: str) -> bytes:
#             """Generate a 32-byte storage key from variable name."""
#             if var_name not in var_to_key:
#                 key = hashlib.sha256(var_name.encode()).digest()
#                 var_to_key[var_name] = key
#             return var_to_key[var_name]

#         # Parse state variables (e.g., uint256 public foo)
#         state_vars = re.findall(r"uint256\s+public\s+(\w+)\s*;", code)
#         logger.debug(f"Detected state variables: {state_vars}")
#         for var in state_vars:
#             get_storage_key(var)  # Pre-register state variable keys

#         for stmt in statements:
#             logger.debug(f"Processing statement: '{stmt}'")

#             # Assignment with addition (e.g., foo = 10 + 20)
#             add_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\+\s*(\d+)", stmt)
#             if add_match:
#                 var, a, b = add_match.groups()
#                 a, b = int(a), int(b)
#                 key = get_storage_key(var)
#                 bytecode.extend([CoolOps.PUSH1, a])
#                 gas_cost += 3
#                 bytecode.extend([CoolOps.PUSH1, b])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.ADD)
#                 gas_cost += 3
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(key)
#                 gas_cost += 20000
#                 write_keys.add(key)
#                 logger.debug(f"Compiled {var} = {a} + {b} at {key.hex()}")
#                 continue

#             # Assignment with subtraction (e.g., foo = 30 - 15)
#             sub_match = re.match(r"(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", stmt)
#             if sub_match:
#                 var, a, b = sub_match.groups()
#                 a, b = int(a), int(b)
#                 key = get_storage_key(var)
#                 bytecode.extend([CoolOps.PUSH1, a])
#                 gas_cost += 3
#                 bytecode.extend([CoolOps.PUSH1, b])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.SUB)
#                 gas_cost += 5
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(key)
#                 gas_cost += 20000
#                 write_keys.add(key)
#                 logger.debug(f"Compiled {var} = {a} - {b} at {key.hex()}")
#                 continue
            
#             # Assignment with multiplication (e.g., x = 10 * 20)
#             mul_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\*\s*(\d+)", stmt)
#             if mul_match:
#                 var, a, b = mul_match.groups()
#                 a, b = int(a), int(b)
#                 key = get_storage_key(var)
#                 bytecode.extend([CoolOps.PUSH1, a])
#                 gas_cost += 3
#                 bytecode.extend([CoolOps.PUSH1, b])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.MUL)
#                 gas_cost += 5  # Gas cost for MUL, matching BVM's gas_costs
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(key)
#                 gas_cost += 20000
#                 write_keys.add(key)
#                 logger.debug(f"Compiled {var} = {a} * {b} at {key.hex()}")
#                 continue
            
#             # Assignment from variable (e.g., bar = foo)
#             assign_match = re.match(r"(\w+)\s*=\s*(\w+)", stmt)
#             if assign_match:
#                 target, source = assign_match.groups()
#                 if target == source:
#                     continue  # Skip self-assignment
#                 target_key = get_storage_key(target)
#                 source_key = get_storage_key(source)
#                 bytecode.append(CoolOps.SLOAD)
#                 bytecode.extend(source_key)
#                 gas_cost += 200
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(target_key)
#                 gas_cost += 20000
#                 read_keys.add(source_key)
#                 write_keys.add(target_key)
#                 logger.debug(f"Compiled {target} = {source}")
#                 continue
            

#             if stmt:  # Non-empty unsupported statement
#                 return b"", 0, f"Unsupported statement: {stmt}", read_keys, write_keys

#         bytecode.append(CoolOps.STOP)
#         gas_cost += 0
#         logger.info(f"Compiled bytecode: {bytecode.hex()}, Gas: {gas_cost}")
#         return bytes(bytecode), gas_cost, None, read_keys, write_keys





# compiler.py
# Implements compilers for C, Java, C++, and Solidity contracts with basic operations and if/else

# compiler.py
# Implements compilers for C, Java, C++, and Solidity contracts with basic operations and if/else

import re
import hashlib
from typing import Tuple, Optional, Dict, Set, List
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
        logger.info("Compiling C contract")
        bytecode = bytearray()
        gas_cost = 0
        read_keys: Set[bytes] = set()
        write_keys: Set[bytes] = set()

        # Find state variables (e.g., int foo;)
        var_pattern = r"int\s+(\w+)\s*;"
        state_vars = re.findall(var_pattern, code)
        logger.debug(f"Detected state variables: {state_vars}")

        # Find calc() function
        func_match = re.search(r"void\s+calc\s*\(\s*\)\s*\{([^}]*)\}", code, re.DOTALL)
        if not func_match:
            return b"", 0, "No 'void calc() {...}' found", set(), set()

        func_body = func_match.group(1).strip()
        if not func_body:
            return b"", 0, "Function calc() is empty", set(), set()

        # Split statements, preserving if/else structures
        def split_statements(body: str) -> List[str]:
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
                    if brace_count == 0 and buffer.strip():
                        statements.append(buffer.strip())
                        buffer = ""
                elif char == ';' and brace_count == 0:
                    if buffer.strip():
                        statements.append(buffer.strip())
                    buffer = ""
                else:
                    buffer += char
            if buffer.strip():
                statements.append(buffer.strip())
            return [s for s in statements if s]

        statements = split_statements(func_body)
        logger.debug(f"Parsed statements: {statements}")

        # Track variables and their storage keys
        var_to_key: Dict[str, bytes] = {}
        for var in state_vars:
            var_to_key[var] = hashlib.sha256(var.encode()).digest()

        def get_storage_key(var_name: str) -> bytes:
            """Generate a 32-byte storage key from variable name."""
            if var_name not in var_to_key:
                return b""
            return var_to_key[var_name]

        def compile_statement(stmt: str, bytecode: bytearray, gas_cost: int, read_keys: Set[bytes], write_keys: Set[bytes]) -> Tuple[int, Optional[str]]:
            logger.debug(f"Processing statement: '{stmt}'")

            # Assignment with addition (e.g., x = 10 + 20)
            add_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\+\s*(\d+)", stmt)
            if add_match:
                var, a, b = add_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
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
                return gas_cost, None

            # Assignment with subtraction (e.g., x = 30 - 15)
            sub_match = re.match(r"(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", stmt)
            if sub_match:
                var, a, b = sub_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
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
                return gas_cost, None

            # Assignment with multiplication (e.g., x = 10 * 20)
            mul_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\*\s*(\d+)", stmt)
            if mul_match:
                var, a, b = mul_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
                a, b = int(a), int(b)
                key = get_storage_key(var)
                bytecode.extend([CoolOps.PUSH1, a])
                gas_cost += 3
                bytecode.extend([CoolOps.PUSH1, b])
                gas_cost += 3
                bytecode.append(CoolOps.MUL)
                gas_cost += 5
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(key)
                gas_cost += 20000
                write_keys.add(key)
                logger.debug(f"Compiled {var} = {a} * {b} at {key.hex()}")
                return gas_cost, None

            # Assignment with number (e.g., x = 150)
            num_match = re.match(r"(\w+)\s*=\s*(\d+)", stmt)
            if num_match:
                var, num = num_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
                num = int(num)
                key = get_storage_key(var)
                bytecode.extend([CoolOps.PUSH1, num])
                gas_cost += 3
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(key)
                gas_cost += 20000
                write_keys.add(key)
                logger.debug(f"Compiled {var} = {num} at {key.hex()}")
                return gas_cost, None

            # Assignment from variable (e.g., x = y)
            assign_match = re.match(r"(\w+)\s*=\s*(\w+)", stmt)
            if assign_match:
                target, source = assign_match.groups()
                if target not in state_vars:
                    return gas_cost, f"Variable {target} not declared"
                if source not in state_vars:
                    return gas_cost, f"Variable {source} not declared"
                if target == source:
                    return gas_cost, None
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
                return gas_cost, None

            return gas_cost, f"Unsupported statement: {stmt}"

        for stmt in statements:
            # If/else statement (e.g., if (x > 100) { stmt } else { stmt })
            if_match = re.match(r"if\s*\(\s*(\w+)\s*>\s*(\d+)\s*\)\s*\{([^}]*)\}\s*else\s*\{([^}]*)\}", stmt, re.DOTALL)
            if if_match:
                var, num, if_body, else_body = if_match.groups()
                if var not in state_vars:
                    return b"", 0, f"Variable {var} not declared", read_keys, write_keys
                num = int(num)

                # Parse if and else statements
                if_statements = [s.strip() for s in if_body.split(';') if s.strip()]
                else_statements = [s.strip() for s in else_body.split(';') if s.strip()]

                # Load condition: var > num
                var_key = get_storage_key(var)
                bytecode.append(CoolOps.SLOAD)
                bytecode.extend(var_key)
                gas_cost += 200
                read_keys.add(var_key)
                bytecode.extend([CoolOps.PUSH1, num])
                gas_cost += 3
                bytecode.append(CoolOps.GT)
                gas_cost += 3

                # Placeholder for JUMPI offset
                jumpi_pos = len(bytecode)
                bytecode.extend([CoolOps.JUMPI, 0x00, 0x00])
                gas_cost += 10

                # Compile if block
                bytecode.append(CoolOps.JUMPDEST)
                gas_cost += 1
                for if_stmt in if_statements:
                    gas_cost, error = compile_statement(if_stmt, bytecode, gas_cost, read_keys, write_keys)
                    if error:
                        return b"", 0, error, read_keys, write_keys

                # Jump to end
                bytecode.append(CoolOps.JUMP)
                jump_end_pos = len(bytecode)
                bytecode.extend([0x00, 0x00])
                gas_cost += 8

                # Else block
                else_start = len(bytecode)
                bytecode.append(CoolOps.JUMPDEST)
                gas_cost += 1
                for else_stmt in else_statements:
                    gas_cost, error = compile_statement(else_stmt, bytecode, gas_cost, read_keys, write_keys)
                    if error:
                        return b"", 0, error, read_keys, write_keys

                # End of conditional
                end_pos = len(bytecode)
                bytecode.append(CoolOps.JUMPDEST)
                gas_cost += 1

                # Set jump offsets
                bytecode[jumpi_pos + 1] = (else_start >> 8) & 0xFF
                bytecode[jumpi_pos + 2] = else_start & 0xFF
                bytecode[jump_end_pos + 1] = (end_pos >> 8) & 0xFF
                bytecode[jump_end_pos + 2] = end_pos & 0xFF

                logger.debug(f"Compiled if ({var} > {num}) {{ {if_body} }} else {{ {else_body} }}")
                continue

            # Other statements
            gas_cost, error = compile_statement(stmt, bytecode, gas_cost, read_keys, write_keys)
            if error:
                return b"", 0, error, read_keys, write_keys

        bytecode.append(CoolOps.STOP)
        gas_cost += 0
        logger.info(f"Compiled bytecode: {bytecode.hex()}, Gas: {gas_cost}")
        return bytes(bytecode), gas_cost, None, read_keys, write_keys

class JavaCompiler(CCompiler):
    pass

class CppCompiler(CCompiler):
    pass

class SolidityCompiler(Compiler):
    @staticmethod
    def brew(code: str) -> Tuple[bytes, int, Optional[str], Set[bytes], Set[bytes]]:
        logger.info("Compiling Solidity contract")
        bytecode = bytearray()
        gas_cost = 0
        read_keys: Set[bytes] = set()
        write_keys: Set[bytes] = set()

        # Find state variables (e.g., uint256 public foo;)
        var_pattern = r"uint256\s+public\s+(\w+)\s*;"
        state_vars = re.findall(var_pattern, code)
        logger.debug(f"Detected state variables: {state_vars}")

        # Find calc() function
        func_match = re.search(r"function\s+calc\s*\(\s*\)\s+public\s*\{([^}]*)\}", code, re.DOTALL)
        if not func_match:
            return b"", 0, "No 'function calc() public {...}' found", set(), set()

        func_body = func_match.group(1).strip()
        if not func_body:
            return b"", 0, "Function calc() is empty", set(), set()

        # Split statements, preserving if/else structures
        def split_statements(body: str) -> List[str]:
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
                    if brace_count == 0 and buffer.strip():
                        statements.append(buffer.strip())
                        buffer = ""
                elif char == ';' and brace_count == 0:
                    if buffer.strip():
                        statements.append(buffer.strip())
                    buffer = ""
                else:
                    buffer += char
            if buffer.strip():
                statements.append(buffer.strip())
            return [s for s in statements if s]

        statements = split_statements(func_body)
        logger.debug(f"Parsed Solidity statements: {statements}")

        # Track variables and their storage keys
        var_to_key: Dict[str, bytes] = {}
        for var in state_vars:
            var_to_key[var] = hashlib.sha256(var.encode()).digest()

        def get_storage_key(var_name: str) -> bytes:
            """Generate a 32-byte storage key from variable name."""
            if var_name not in var_to_key:
                return b""
            return var_to_key[var_name]

        def compile_statement(stmt: str, bytecode: bytearray, gas_cost: int, read_keys: Set[bytes], write_keys: Set[bytes]) -> Tuple[int, Optional[str]]:
            logger.debug(f"Processing statement: '{stmt}'")

            # Assignment with addition (e.g., foo = 10 + 20)
            add_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\+\s*(\d+)", stmt)
            if add_match:
                var, a, b = add_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
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
                return gas_cost, None

            # Assignment with subtraction (e.g., foo = 30 - 15)
            sub_match = re.match(r"(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", stmt)
            if sub_match:
                var, a, b = sub_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
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
                return gas_cost, None

            # Assignment with multiplication (e.g., foo = 10 * 20)
            mul_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\*\s*(\d+)", stmt)
            if mul_match:
                var, a, b = mul_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
                a, b = int(a), int(b)
                key = get_storage_key(var)
                bytecode.extend([CoolOps.PUSH1, a])
                gas_cost += 3
                bytecode.extend([CoolOps.PUSH1, b])
                gas_cost += 3
                bytecode.append(CoolOps.MUL)
                gas_cost += 5
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(key)
                gas_cost += 20000
                write_keys.add(key)
                logger.debug(f"Compiled {var} = {a} * {b} at {key.hex()}")
                return gas_cost, None

            # Assignment with number (e.g., foo = 150)
            num_match = re.match(r"(\w+)\s*=\s*(\d+)", stmt)
            if num_match:
                var, num = num_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
                num = int(num)
                key = get_storage_key(var)
                bytecode.extend([CoolOps.PUSH1, num])
                gas_cost += 3
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(key)
                gas_cost += 20000
                write_keys.add(key)
                logger.debug(f"Compiled {var} = {num} at {key.hex()}")
                return gas_cost, None

            # Assignment from variable (e.g., bar = foo)
            assign_match = re.match(r"(\w+)\s*=\s*(\w+)", stmt)
            if assign_match:
                target, source = assign_match.groups()
                if target not in state_vars:
                    return gas_cost, f"Variable {target} not declared"
                if source not in state_vars:
                    return gas_cost, f"Variable {source} not declared"
                if target == source:
                    return gas_cost, None
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
                return gas_cost, None

            return gas_cost, f"Unsupported statement: {stmt}"

        for stmt in statements:
            # If/else statement (e.g., if (x > 100) { stmt } else { stmt })
            if_match = re.match(r"if\s*\(\s*(\w+)\s*>\s*(\d+)\s*\)\s*\{([^}]*)\}\s*else\s*\{([^}]*)\}", stmt, re.DOTALL)
            if if_match:
                var, num, if_body, else_body = if_match.groups()
                if var not in state_vars:
                    return b"", 0, f"Variable {var} not declared", read_keys, write_keys
                num = int(num)

                # Parse if and else statements
                if_statements = [s.strip() for s in if_body.split(';') if s.strip()]
                else_statements = [s.strip() for s in else_body.split(';') if s.strip()]

                # Load condition: var > num
                var_key = get_storage_key(var)
                bytecode.append(CoolOps.SLOAD)
                bytecode.extend(var_key)
                gas_cost += 200
                read_keys.add(var_key)
                bytecode.extend([CoolOps.PUSH1, num])
                gas_cost += 3
                bytecode.append(CoolOps.GT)
                gas_cost += 3

                # Placeholder for JUMPI offset
                jumpi_pos = len(bytecode)
                bytecode.extend([CoolOps.JUMPI, 0x00, 0x00])
                gas_cost += 10

                # Compile if block
                bytecode.append(CoolOps.JUMPDEST)
                gas_cost += 1
                for if_stmt in if_statements:
                    gas_cost, error = compile_statement(if_stmt, bytecode, gas_cost, read_keys, write_keys)
                    if error:
                        return b"", 0, error, read_keys, write_keys

                # Jump to end
                bytecode.append(CoolOps.JUMP)
                jump_end_pos = len(bytecode)
                bytecode.extend([0x00, 0x00])
                gas_cost += 8

                # Else block
                else_start = len(bytecode)
                bytecode.append(CoolOps.JUMPDEST)
                gas_cost += 1
                for else_stmt in else_statements:
                    gas_cost, error = compile_statement(else_stmt, bytecode, gas_cost, read_keys, write_keys)
                    if error:
                        return b"", 0, error, read_keys, write_keys

                # End of conditional
                end_pos = len(bytecode)
                bytecode.append(CoolOps.JUMPDEST)
                gas_cost += 1

                # Set jump offsets
                bytecode[jumpi_pos + 1] = (else_start >> 8) & 0xFF
                bytecode[jumpi_pos + 2] = else_start & 0xFF
                bytecode[jump_end_pos + 1] = (end_pos >> 8) & 0xFF
                bytecode[jump_end_pos + 2] = end_pos & 0xFF

                logger.debug(f"Compiled if ({var} > {num}) {{ {if_body} }} else {{ {else_body} }}")
                continue

            # Other statements
            gas_cost, error = compile_statement(stmt, bytecode, gas_cost, read_keys, write_keys)
            if error:
                return b"", 0, error, read_keys, write_keys

        bytecode.append(CoolOps.STOP)
        gas_cost += 0
        logger.info(f"Compiled bytecode: {bytecode.hex()}, Gas: {gas_cost}")
        return bytes(bytecode), gas_cost, None, read_keys, write_keys