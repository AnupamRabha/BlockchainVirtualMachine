
# # class CCompiler(Compiler):
# #     @staticmethod
# #     def brew(code: str) -> Tuple[bytes, int, Optional[str], Set[bytes], Set[bytes]]:
# #         logger.info("Compiling C contract")
# #         bytecode = bytearray()
# #         gas_cost = 0
# #         read_keys: Set[bytes] = set()
# #         write_keys: Set[bytes] = set()

# #         # Find state variables (e.g., int foo;)
# #         var_pattern = r"int\s+(\w+)\s*;"
# #         state_vars = re.findall(var_pattern, code)
# #         logger.debug(f"Detected state variables: {state_vars}")

# #         # Find calc() function
# #         func_match = re.search(r"void\s+calc\s*\(\s*\)\s*\{([^}]*)\}", code, re.DOTALL)
# #         if not func_match:
# #             return b"", 0, "No 'void calc() {...}' found", set(), set()

# #         func_body = func_match.group(1).strip()
# #         if not func_body:
# #             return b"", 0, "Function calc() is empty", set(), set()

# #         # Split statements, preserving if/else structures
# #         def split_statements(body: str) -> List[str]:
# #             statements = []
# #             buffer = ""
# #             brace_count = 0
# #             for char in body:
# #                 if char == '{':
# #                     brace_count += 1
# #                     buffer += char
# #                 elif char == '}':
# #                     brace_count -= 1
# #                     buffer += char
# #                     if brace_count == 0 and buffer.strip():
# #                         statements.append(buffer.strip())
# #                         buffer = ""
# #                 elif char == ';' and brace_count == 0:
# #                     if buffer.strip():
# #                         statements.append(buffer.strip())
# #                     buffer = ""
# #                 else:
# #                     buffer += char
# #             if buffer.strip():
# #                 statements.append(buffer.strip())
# #             return [s for s in statements if s]

# #         statements = split_statements(func_body)
# #         logger.debug(f"Parsed statements: {statements}")

# #         # Track variables and their storage keys
# #         var_to_key: Dict[str, bytes] = {}
# #         for var in state_vars:
# #             var_to_key[var] = hashlib.sha256(var.encode()).digest()

# #         def get_storage_key(var_name: str) -> bytes:
# #             """Generate a 32-byte storage key from variable name."""
# #             if var_name not in var_to_key:
# #                 return b""
# #             return var_to_key[var_name]

# #         def compile_statement(stmt: str, bytecode: bytearray, gas_cost: int, read_keys: Set[bytes], write_keys: Set[bytes]) -> Tuple[int, Optional[str]]:
# #             logger.debug(f"Processing statement: '{stmt}'")

# #             # Assignment with addition (e.g., x = 10 + 20)
# #             add_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\+\s*(\d+)", stmt)
# #             if add_match:
# #                 var, a, b = add_match.groups()
# #                 if var not in state_vars:
# #                     return gas_cost, f"Variable {var} not declared"
# #                 a, b = int(a), int(b)
# #                 key = get_storage_key(var)
# #                 bytecode.extend([CoolOps.PUSH1, a])
# #                 gas_cost += 3
# #                 bytecode.extend([CoolOps.PUSH1, b])
# #                 gas_cost += 3
# #                 bytecode.append(CoolOps.ADD)
# #                 gas_cost += 3
# #                 bytecode.append(CoolOps.SSTORE)
# #                 bytecode.extend(key)
# #                 gas_cost += 20000
# #                 write_keys.add(key)
# #                 logger.debug(f"Compiled {var} = {a} + {b} at {key.hex()}")
# #                 return gas_cost, None

# #             # Assignment with subtraction (e.g., x = 30 - 15)
# #             sub_match = re.match(r"(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", stmt)
# #             if sub_match:
# #                 var, a, b = sub_match.groups()
# #                 if var not in state_vars:
# #                     return gas_cost, f"Variable {var} not declared"
# #                 a, b = int(a), int(b)
# #                 key = get_storage_key(var)
# #                 bytecode.extend([CoolOps.PUSH1, a])
# #                 gas_cost += 3
# #                 bytecode.extend([CoolOps.PUSH1, b])
# #                 gas_cost += 3
# #                 bytecode.append(CoolOps.SUB)
# #                 gas_cost += 5
# #                 bytecode.append(CoolOps.SSTORE)
# #                 bytecode.extend(key)
# #                 gas_cost += 20000
# #                 write_keys.add(key)
# #                 logger.debug(f"Compiled {var} = {a} - {b} at {key.hex()}")
# #                 return gas_cost, None

# #             # Assignment with multiplication (e.g., x = 10 * 20)
# #             mul_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\*\s*(\d+)", stmt)
# #             if mul_match:
# #                 var, a, b = mul_match.groups()
# #                 if var not in state_vars:
# #                     return gas_cost, f"Variable {var} not declared"
# #                 a, b = int(a), int(b)
# #                 key = get_storage_key(var)
# #                 bytecode.extend([CoolOps.PUSH1, a])
# #                 gas_cost += 3
# #                 bytecode.extend([CoolOps.PUSH1, b])
# #                 gas_cost += 3
# #                 bytecode.append(CoolOps.MUL)
# #                 gas_cost += 5
# #                 bytecode.append(CoolOps.SSTORE)
# #                 bytecode.extend(key)
# #                 gas_cost += 20000
# #                 write_keys.add(key)
# #                 logger.debug(f"Compiled {var} = {a} * {b} at {key.hex()}")
# #                 return gas_cost, None

# #             # Assignment with number (e.g., x = 150)
# #             num_match = re.match(r"(\w+)\s*=\s*(\d+)", stmt)
# #             if num_match:
# #                 var, num = num_match.groups()
# #                 if var not in state_vars:
# #                     return gas_cost, f"Variable {var} not declared"
# #                 num = int(num)
# #                 key = get_storage_key(var)
# #                 bytecode.extend([CoolOps.PUSH1, num])
# #                 gas_cost += 3
# #                 bytecode.append(CoolOps.SSTORE)
# #                 bytecode.extend(key)
# #                 gas_cost += 20000
# #                 write_keys.add(key)
# #                 logger.debug(f"Compiled {var} = {num} at {key.hex()}")
# #                 return gas_cost, None

# #             # Assignment from variable (e.g., x = y)
# #             assign_match = re.match(r"(\w+)\s*=\s*(\w+)", stmt)
# #             if assign_match:
# #                 target, source = assign_match.groups()
# #                 if target not in state_vars:
# #                     return gas_cost, f"Variable {target} not declared"
# #                 if source not in state_vars:
# #                     return gas_cost, f"Variable {source} not declared"
# #                 if target == source:
# #                     return gas_cost, None
# #                 target_key = get_storage_key(target)
# #                 source_key = get_storage_key(source)
# #                 bytecode.append(CoolOps.SLOAD)
# #                 bytecode.extend(source_key)
# #                 gas_cost += 200
# #                 bytecode.append(CoolOps.SSTORE)
# #                 bytecode.extend(target_key)
# #                 gas_cost += 20000
# #                 read_keys.add(source_key)
# #                 write_keys.add(target_key)
# #                 logger.debug(f"Compiled {target} = {source}")
# #                 return gas_cost, None

# #             return gas_cost, f"Unsupported statement: {stmt}"

# #         for stmt in statements:
# #             # If/else statement (e.g., if (x > 100) { stmt } else { stmt })
# #             if_match = re.match(r"if\s*\(\s*(\w+)\s*([><=])\s*(\d+)\s*\)\s*\{([^}]*)\}\s*else\s*\{([^}]*)\}", stmt, re.DOTALL)
# #             print("Hi, ",stmt)
# #             if if_match:
# #                 var, op, num, if_body, else_body = if_match.groups()
# #                 if var not in state_vars:
# #                     return b"", 0, f"Variable {var} not declared", read_keys, write_keys
# #                 num = int(num)

# #                 # Parse if and else statements
# #                 if_statements = [s.strip() for s in if_body.split(';') if s.strip()]
# #                 else_statements = [s.strip() for s in else_body.split(';') if s.strip()]

# #                 # Load condition: var >/</= num
# #                 var_key = get_storage_key(var)
# #                 bytecode.append(CoolOps.SLOAD)
# #                 bytecode.extend(var_key)
# #                 gas_cost += 200
# #                 read_keys.add(var_key)
# #                 bytecode.extend([CoolOps.PUSH1, num])
# #                 gas_cost += 3
# #                 # Select comparison opcode
# #                 if op == '>':
# #                     bytecode.append(CoolOps.GT)
# #                 elif op == '<':
# #                     bytecode.append(CoolOps.LT)
# #                 elif op == '=':
# #                     bytecode.append(CoolOps.EQ)
# #                 gas_cost += 3

# #                 # Placeholder for JUMPI offset
# #                 jumpi_pos = len(bytecode)
# #                 bytecode.extend([CoolOps.JUMPI, 0x00, 0x00])
# #                 gas_cost += 10

# #                 # Compile if block
# #                 bytecode.append(CoolOps.JUMPDEST)
# #                 gas_cost += 1
# #                 for if_stmt in if_statements:
# #                     gas_cost, error = compile_statement(if_stmt, bytecode, gas_cost, read_keys, write_keys)
# #                     if error:
# #                         return b"", 0, error, read_keys, write_keys

# #                 # # Jump to end
# #                 # bytecode.append(CoolOps.JUMP)
# #                 # jump_end_pos = len(bytecode)
# #                 # bytecode.extend([0x00, 0x00])
# #                 # gas_cost += 8



# #                 if else_body:
# #                     bytecode.append(CoolOps.JUMP)
# #                     jump_end_pos = len(bytecode)
# #                     bytecode.extend([0x00, 0x00])
# #                     gas_cost += 8
# #                 else:
# #                     jump_end_pos = None

# #                 # Else block
# #                 else_start = len(bytecode)
# #                 if else_body:
# #                     bytecode.append(CoolOps.JUMPDEST)
# #                     gas_cost += 1
# #                     else_statements = [s.strip() for s in else_body.split(';') if s.strip()]
# #                     for else_stmt in else_statements:
# #                         gas_cost, error = compile_statement(else_stmt, bytecode, gas_cost, read_keys, write_keys)
# #                         if error:
# #                             return b"", 0, error, read_keys, write_keys
                    
# #                 # End of conditional
# #                 end_pos = len(bytecode)
# #                 bytecode.append(CoolOps.JUMPDEST)
# #                 gas_cost += 1

# #                 # Set jump offsets
# #                 bytecode[jumpi_pos + 1] = (else_start >> 8) & 0xFF
# #                 bytecode[jumpi_pos + 2] = else_start & 0xFF
# #                 if jump_end_pos:
# #                     bytecode[jump_end_pos + 1] = (end_pos >> 8) & 0xFF
# #                     bytecode[jump_end_pos + 2] = end_pos & 0xFF

# #                 logger.debug(f"Compiled if ({var} {op} {num}) {{ {if_body} }} else {{ {else_body} }}")
# #                 continue

# #             # Other statements
# #             gas_cost, error = compile_statement(stmt, bytecode, gas_cost, read_keys, write_keys)
# #             if error:
# #                 return b"", 0, error, read_keys, write_keys

# #         bytecode.append(CoolOps.STOP)
# #         gas_cost += 0
# #         logger.info(f"Compiled bytecode: {bytecode.hex()}, Gas: {gas_cost}")
# #         return bytes(bytecode), gas_cost, None, read_keys, write_keys

# import re
# import hashlib
# from typing import Tuple, Optional, Dict, Set, List
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

#         # Find state variables (e.g., int foo;)
#         var_pattern = r"int\s+(\w+)\s*;"
#         state_vars = re.findall(var_pattern, code)
#         logger.debug(f"Detected state variables: {state_vars}")

#         # Find calc() function
#         func_match = re.search(r"void\s+calc\s*\(\s*\)\s*\{([^}]*)\}", code, re.DOTALL)
#         if not func_match:
#             return b"", 0, "No 'void calc() {...}' found", set(), set()

#         func_body = func_match.group(1).strip()
#         if not func_body:
#             return b"", 0, "Function calc() is empty", set(), set()

#         # Split statements, preserving if/else structures
#         def split_statements(body: str) -> List[str]:
#             statements = []
#             buffer = ""
#             brace_count = 0
#             i = 0
#             while i < len(body):
#                 char = body[i]

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

#                 i += 1
#                 print(brace_count , buffer.strip().startswith('if') )
#                 # Handle if/else blocks explicitly
#                 if buffer.strip().startswith('if') and brace_count == 0:
#                     # Look ahead for the full if/else block
#                     if_start = i - len(buffer)
#                     temp_buffer = buffer
#                     temp_brace_count = brace_count
#                     j = i
#                     while j < len(body):
#                         c = body[j]
#                         temp_buffer += c
#                         if c == '{':
#                             temp_brace_count += 1
#                         elif c == '}':
#                             temp_brace_count -= 1
#                             if temp_brace_count == 0:
#                                 # Check for else
#                                 else_start = j + 1
#                                 temp_buffer_stripped = temp_buffer.strip()
#                                 if temp_buffer_stripped.endswith('}'):
#                                     k = else_start
#                                     while k < len(body) and body[k].isspace():
#                                         k += 1
#                                     if k + 4 < len(body) and body[k:k+4] == 'else':
#                                         # Include else block
#                                         temp_brace_count = 0
#                                         j = k
#                                         while j < len(body):
#                                             c = body[j]
#                                             temp_buffer += c
#                                             if c == '{':
#                                                 temp_brace_count += 1
#                                             elif c == '}':
#                                                 temp_brace_count -= 1
#                                                 if temp_brace_count == 0:
#                                                     break
#                                             j += 1
#                                         j += 1
#                                 break
#                         j += 1
#                     if temp_buffer.strip():
#                         statements.append(temp_buffer.strip())
#                         buffer = ""
#                         i = j

#             if buffer.strip():
#                 statements.append(buffer.strip())
#             return [s for s in statements if s]

#         statements = split_statements(func_body)
#         logger.debug(f"Parsed statements: {statements}")

#         # Track variables and their storage keys
#         var_to_key: Dict[str, bytes] = {}
#         for var in state_vars:
#             var_to_key[var] = hashlib.sha256(var.encode()).digest()

#         def get_storage_key(var_name: str) -> bytes:
#             """Generate a 32-byte storage key from variable name."""
#             if var_name not in var_to_key:
#                 return b""
#             return var_to_key[var_name]

#         def compile_statement(stmt: str, bytecode: bytearray, gas_cost: int, read_keys: Set[bytes], write_keys: Set[bytes]) -> Tuple[int, Optional[str]]:
#             logger.debug(f"Processing statement: '{stmt}'")

#             # Assignment with addition (e.g., x = 10 + 20)
#             add_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\+\s*(\d+)", stmt)
#             if add_match:
#                 var, a, b = add_match.groups()
#                 if var not in state_vars:
#                     return gas_cost, f"Variable {var} not declared"
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
#                 return gas_cost, None

#             # Assignment with subtraction (e.g., x = 30 - 15)
#             sub_match = re.match(r"(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", stmt)
#             if sub_match:
#                 var, a, b = sub_match.groups()
#                 if var not in state_vars:
#                     return gas_cost, f"Variable {var} not declared"
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
#                 return gas_cost, None

#             # Assignment with multiplication (e.g., x = 10 * 20)
#             mul_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\*\s*(\d+)", stmt)
#             if mul_match:
#                 var, a, b = mul_match.groups()
#                 if var not in state_vars:
#                     return gas_cost, f"Variable {var} not declared"
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
#                 return gas_cost, None

#             # Assignment with number (e.g., x = 150)
#             num_match = re.match(r"(\w+)\s*=\s*(\d+)", stmt)
#             if num_match:
#                 var, num = num_match.groups()
#                 if var not in state_vars:
#                     return gas_cost, f"Variable {var} not declared"
#                 num = int(num)
#                 key = get_storage_key(var)
#                 bytecode.extend([CoolOps.PUSH1, num])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(key)
#                 gas_cost += 20000
#                 write_keys.add(key)
#                 logger.debug(f"Compiled {var} = {num} at {key.hex()}")
#                 return gas_cost, None

#             # Assignment from variable (e.g., x = y)
#             assign_match = re.match(r"(\w+)\s*=\s*(\w+)", stmt)
#             if assign_match:
#                 target, source = assign_match.groups()
#                 if target not in state_vars:
#                     return gas_cost, f"Variable {target} not declared"
#                 if source not in state_vars:
#                     return gas_cost, f"Variable {source} not declared"
#                 if target == source:
#                     return gas_cost, None
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
#                 return gas_cost, None

#             return gas_cost, f"Unsupported statement: {stmt}"

#         for stmt in statements:
#             # If/else statement (e.g., if (x > 100) { stmt } [else { stmt }])
#             if_match = re.match(r"if\s*\(\s*(\w+)\s*([><=])\s*(\d+)\s*\)\s*\{([^}]*)\}\s*(?:else\s*\{([^}]*)\})?", stmt, re.DOTALL | re.MULTILINE)
#             logger.debug(f"Checking if statement: '{stmt}'")
#             if if_match:
#                 logger.debug(f"If match groups: {if_match.groups()}")
#                 var, op, num, if_body, else_body = if_match.groups()
#                 if var not in state_vars:
#                     return b"", 0, f"Variable {var} not declared", read_keys, write_keys
#                 num = int(num)
#                 else_body = else_body or ""  # Handle optional else

#                 # Parse if and else statements
#                 if_statements = [s.strip() for s in if_body.split(';') if s.strip()]
#                 else_statements = [s.strip() for s in else_body.split(';') if s.strip()]
#                 logger.debug(f"If statements: {if_statements}, Else statements: {else_statements}")

#                 # Load condition: var >/</= num
#                 var_key = get_storage_key(var)
#                 bytecode.append(CoolOps.SLOAD)
#                 bytecode.extend(var_key)
#                 gas_cost += 200
#                 read_keys.add(var_key)
#                 bytecode.extend([CoolOps.PUSH1, num])
#                 gas_cost += 3
#                 # Select comparison opcode
#                 if op == '>':
#                     bytecode.append(CoolOps.GT)
#                 elif op == '<':
#                     bytecode.append(CoolOps.LT)
#                 elif op == '=':
#                     bytecode.append(CoolOps.EQ)
#                 gas_cost += 3

#                 # Placeholder for JUMPI offset
#                 jumpi_pos = len(bytecode)
#                 bytecode.extend([CoolOps.JUMPI, 0x00, 0x00])
#                 gas_cost += 10

#                 # Compile if block
#                 bytecode.append(CoolOps.JUMPDEST)
#                 gas_cost += 1
#                 for if_stmt in if_statements:
#                     gas_cost, error = compile_statement(if_stmt, bytecode, gas_cost, read_keys, write_keys)
#                     if error:
#                         return b"", 0, error, read_keys, write_keys

#                 # Handle else block jump
#                 if else_body:
#                     bytecode.append(CoolOps.JUMP)
#                     jump_end_pos = len(bytecode)
#                     bytecode.extend([0x00, 0x00])
#                     gas_cost += 8
#                 else:
#                     jump_end_pos = None

#                 # Else block
#                 else_start = len(bytecode)
#                 if else_body:
#                     bytecode.append(CoolOps.JUMPDEST)
#                     gas_cost += 1
#                     for else_stmt in else_statements:
#                         gas_cost, error = compile_statement(else_stmt, bytecode, gas_cost, read_keys, write_keys)
#                         if error:
#                             return b"", 0, error, read_keys, write_keys

#                 # End of conditional
#                 end_pos = len(bytecode)
#                 bytecode.append(CoolOps.JUMPDEST)
#                 gas_cost += 1

#                 # Set jump offsets
#                 bytecode[jumpi_pos + 1] = (else_start >> 8) & 0xFF
#                 bytecode[jumpi_pos + 2] = else_start & 0xFF
#                 if jump_end_pos:
#                     bytecode[jump_end_pos + 1] = (end_pos >> 8) & 0xFF
#                     bytecode[jump_end_pos + 2] = end_pos & 0xFF

#                 logger.debug(f"Compiled if ({var} {op} {num}) {{ {if_body} }} else {{ {else_body} }}")
#                 continue

#             # Other statements
#             gas_cost, error = compile_statement(stmt, bytecode, gas_cost, read_keys, write_keys)
#             if error:
#                 logger.error(f"Compilation failed: {error}")
#                 return b"", 0, error, read_keys, write_keys

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

#         # Find state variables (e.g., uint256 public foo;)
#         var_pattern = r"uint256\s+public\s+(\w+)\s*;"
#         state_vars = re.findall(var_pattern, code)
#         logger.debug(f"Detected state variables: {state_vars}")

#         # Find calc() function
#         func_match = re.search(r"function\s+calc\s*\(\s*\)\s+public\s*\{([^}]*)\}", code, re.DOTALL)
#         if not func_match:
#             return b"", 0, "No 'function calc() public {...}' found", set(), set()

#         func_body = func_match.group(1).strip()
#         if not func_body:
#             return b"", 0, "Function calc() is empty", set(), set()

#         # Split statements, preserving if/else structures
#         def split_statements(body: str) -> List[str]:
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
#                     if brace_count == 0 and buffer.strip():
#                         statements.append(buffer.strip())
#                         buffer = ""
#                 elif char == ';' and brace_count == 0:
#                     if buffer.strip():
#                         statements.append(buffer.strip())
#                     buffer = ""
#                 else:
#                     buffer += char
#             if buffer.strip():
#                 statements.append(buffer.strip())
#             return [s for s in statements if s]

#         statements = split_statements(func_body)
#         logger.debug(f"Parsed Solidity statements: {statements}")

#         # Track variables and their storage keys
#         var_to_key: Dict[str, bytes] = {}
#         for var in state_vars:
#             var_to_key[var] = hashlib.sha256(var.encode()).digest()

#         def get_storage_key(var_name: str) -> bytes:
#             """Generate a 32-byte storage key from variable name."""
#             if var_name not in var_to_key:
#                 return b""
#             return var_to_key[var_name]

#         def compile_statement(stmt: str, bytecode: bytearray, gas_cost: int, read_keys: Set[bytes], write_keys: Set[bytes]) -> Tuple[int, Optional[str]]:
#             logger.debug(f"Processing statement: '{stmt}'")

#             # Assignment with addition (e.g., foo = 10 + 20)
#             add_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\+\s*(\d+)", stmt)
#             if add_match:
#                 var, a, b = add_match.groups()
#                 if var not in state_vars:
#                     return gas_cost, f"Variable {var} not declared"
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
#                 return gas_cost, None

#             # Assignment with subtraction (e.g., foo = 30 - 15)
#             sub_match = re.match(r"(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", stmt)
#             if sub_match:
#                 var, a, b = sub_match.groups()
#                 if var not in state_vars:
#                     return gas_cost, f"Variable {var} not declared"
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
#                 return gas_cost, None

#             # Assignment with multiplication (e.g., foo = 10 * 20)
#             mul_match = re.match(r"(\w+)\s*=\s*(\d+)\s*\*\s*(\d+)", stmt)
#             if mul_match:
#                 var, a, b = mul_match.groups()
#                 if var not in state_vars:
#                     return gas_cost, f"Variable {var} not declared"
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
#                 return gas_cost, None

#             # Assignment with number (e.g., foo = 150)
#             num_match = re.match(r"(\w+)\s*=\s*(\d+)", stmt)
#             if num_match:
#                 var, num = num_match.groups()
#                 if var not in state_vars:
#                     return gas_cost, f"Variable {var} not declared"
#                 num = int(num)
#                 key = get_storage_key(var)
#                 bytecode.extend([CoolOps.PUSH1, num])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.SSTORE)
#                 bytecode.extend(key)
#                 gas_cost += 20000
#                 write_keys.add(key)
#                 logger.debug(f"Compiled {var} = {num} at {key.hex()}")
#                 return gas_cost, None

#             # Assignment from variable (e.g., bar = foo)
#             assign_match = re.match(r"(\w+)\s*=\s*(\w+)", stmt)
#             if assign_match:
#                 target, source = assign_match.groups()
#                 if target not in state_vars:
#                     return gas_cost, f"Variable {target} not declared"
#                 if source not in state_vars:
#                     return gas_cost, f"Variable {source} not declared"
#                 if target == source:
#                     return gas_cost, None
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
#                 return gas_cost, None

#             return gas_cost, f"Unsupported statement: {stmt}"

#         for stmt in statements:
#             # If/else statement (e.g., if (x > 100) { stmt } else { stmt })
#             if_match = re.match(r"if\s*\(\s*(\w+)\s*>\s*(\d+)\s*\)\s*\{([^}]*)\}\s*else\s*\{([^}]*)\}", stmt, re.DOTALL)
#             from logging_config import configure_logging
#             configure_logging()
#             logger = logging.getLogger(__name__)
#             logger.setLevel(logging.DEBUG) 
#             logger.info("HI, ",stmt)
#             if if_match:
#                 var, num, if_body, else_body = if_match.groups()
#                 if var not in state_vars:
#                     return b"", 0, f"Variable {var} not declared", read_keys, write_keys
#                 num = int(num)

#                 # Parse if and else statements
#                 if_statements = [s.strip() for s in if_body.split(';') if s.strip()]
#                 else_statements = [s.strip() for s in else_body.split(';') if s.strip()]

#                 # Load condition: var > num
#                 var_key = get_storage_key(var)
#                 bytecode.append(CoolOps.SLOAD)
#                 bytecode.extend(var_key)
#                 gas_cost += 200
#                 read_keys.add(var_key)
#                 bytecode.extend([CoolOps.PUSH1, num])
#                 gas_cost += 3
#                 bytecode.append(CoolOps.GT)
#                 gas_cost += 3

#                 # Placeholder for JUMPI offset
#                 jumpi_pos = len(bytecode)
#                 bytecode.extend([CoolOps.JUMPI, 0x00, 0x00])
#                 gas_cost += 10

#                 # Compile if block
#                 bytecode.append(CoolOps.JUMPDEST)
#                 gas_cost += 1
#                 for if_stmt in if_statements:
#                     gas_cost, error = compile_statement(if_stmt, bytecode, gas_cost, read_keys, write_keys)
#                     if error:
#                         return b"", 0, error, read_keys, write_keys

#                 # Jump to end
#                 bytecode.append(CoolOps.JUMP)
#                 jump_end_pos = len(bytecode)
#                 bytecode.extend([0x00, 0x00])
#                 gas_cost += 8

#                 # Else block
#                 else_start = len(bytecode)
#                 bytecode.append(CoolOps.JUMPDEST)
#                 gas_cost += 1
#                 for else_stmt in else_statements:
#                     gas_cost, error = compile_statement(else_stmt, bytecode, gas_cost, read_keys, write_keys)
#                     if error:
#                         return b"", 0, error, read_keys, write_keys

#                 # End of conditional
#                 end_pos = len(bytecode)
#                 bytecode.append(CoolOps.JUMPDEST)
#                 gas_cost += 1

#                 # Set jump offsets
#                 bytecode[jumpi_pos + 1] = (else_start >> 8) & 0xFF
#                 bytecode[jumpi_pos + 2] = else_start & 0xFF
#                 bytecode[jump_end_pos + 1] = (end_pos >> 8) & 0xFF
#                 bytecode[jump_end_pos + 2] = end_pos & 0xFF

#                 logger.debug(f"Compiled if ({var} > {num}) {{ {if_body} }} else {{ {else_body} }}")
#                 continue

#             # Other statements
#             gas_cost, error = compile_statement(stmt, bytecode, gas_cost, read_keys, write_keys)
#             if error:
#                 return b"", 0, error, read_keys, write_keys

#         bytecode.append(CoolOps.STOP)
#         gas_cost += 0
#         logger.info(f"Compiled bytecode: {bytecode.hex()}, Gas: {gas_cost}")
#         return bytes(bytecode), gas_cost, None, read_keys, write_keys

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

        # Split statements
        def split_statements(body: str) -> List[str]:
            statements = []
            buffer = ""
            brace_count = 0
            in_if = False
            i = 0

            while i < len(body):
                char = body[i]
                buffer += char

                if char == '{':
                    brace_count += 1
                    if buffer.strip().startswith('if'):
                        in_if = True
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and in_if:
                        statements.append(buffer.strip())
                        buffer = ""
                        in_if = False
                elif char == ';' and brace_count == 0:
                    if buffer.strip() and not in_if:
                        statements.append(buffer.strip().rstrip(';').strip())
                        buffer = ""
                i += 1

                # Handle remaining content
                if i == len(body) and buffer.strip():
                    if in_if:
                        statements.append(buffer.strip())
                    else:
                        lines = buffer.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                sub_statements = [s.strip() for s in line.split(';') if s.strip()]
                                statements.extend(sub_statements)

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
            
            # Assignment with division (e.g., x = 100 / 5)
            div_match = re.match(r"(\w+)\s*=\s*(\d+)\s*/\s*(\d+)", stmt)
            if div_match:
                var, a, b = div_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
                a, b = int(a), int(b)
                if b == 0:
                    return gas_cost, "Division by zero"
                key = get_storage_key(var)
                bytecode.extend([CoolOps.PUSH1, a])
                gas_cost += 3
                bytecode.extend([CoolOps.PUSH1, b])
                gas_cost += 3
                bytecode.append(CoolOps.DIV)
                gas_cost += 5
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(key)
                gas_cost += 20000
                write_keys.add(key)
                logger.debug(f"Compiled {var} = {a} / {b} at {key.hex()}")
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

            # If block (e.g., if (x > y) { z = 10; })
            if_match = re.match(r"if\s*\(\s*(\w+)\s*(>|==|!=|<)\s*(\w+|\d+)\s*\)\s*\{([\s\S]*)$", stmt, re.DOTALL)
            if if_match:
                left_var, op, right, block = if_match.groups()
                if left_var not in state_vars:
                    return gas_cost, f"Variable {left_var} not declared"
                
                # Log block content for debugging
                logger.debug(f"If block content: '{block}'")
                
                # Determine if right is a variable or literal
                right_is_var = right in state_vars
                if right_is_var and right not in state_vars:
                    return gas_cost, f"Variable {right} not declared"
                
                # Generate storage keys
                left_key = get_storage_key(left_var)
                right_key = get_storage_key(right) if right_is_var else None
                
                # Load left variable
                bytecode.append(CoolOps.SLOAD)
                bytecode.extend(left_key)
                gas_cost += 200
                read_keys.add(left_key)
                
                # Load right operand
                if right_is_var:
                    bytecode.append(CoolOps.SLOAD)
                    bytecode.extend(right_key)
                    gas_cost += 200
                    read_keys.add(right_key)
                else:
                    try:
                        num = int(right)
                        bytecode.extend([CoolOps.PUSH1, num])
                        gas_cost += 3
                    except ValueError:
                        return gas_cost, f"Invalid number {right}"
                
                # Comparison opcode
                if op == ">":
                    bytecode.append(CoolOps.GT)
                elif op == "<":
                    bytecode.append(CoolOps.LT)
                elif op == "==":
                    bytecode.append(CoolOps.EQ)
                elif op == "!=":
                    bytecode.extend([CoolOps.EQ, CoolOps.NOT])
                    gas_cost += 3  # Extra for NOT
                gas_cost += 3  # Comparison cost
                
                # Placeholder for jump destination
                jump_pos = len(bytecode)
                bytecode.extend([CoolOps.JUMPI, 0, 0])  # Dummy offset
                gas_cost += 10
                
                # Compile block statements
                block_statements = split_statements(block)
                logger.debug(f"Block statements after split: {block_statements}")
                
                if not block_statements:
                    # Fallback: split by newlines and semicolons
                    block_statements = []
                    lines = block.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            # Preserve semicolon for statements
                            sub_statements = [s.strip() for s in line.split(';') if s.strip()]
                            block_statements.extend(sub_statements)
                    logger.debug(f"Fallback block statements: {block_statements}")
                    if not block_statements:
                        return gas_cost, "If block is empty"
                
                for block_stmt in block_statements:
                    block_stmt = block_stmt.strip()
                    if block_stmt:
                        logger.debug(f"Compiling block statement: '{block_stmt}'")
                        gas_cost, error = compile_statement(block_stmt, bytecode, gas_cost, read_keys, write_keys)
                        if error:
                            return gas_cost, error
                
                # Set jump destination to skip block
                end_pos = len(bytecode)
                bytecode.append(CoolOps.JUMPDEST)
                gas_cost += 1
                
                # Update JUMPI offset
                offset = end_pos - (jump_pos + 3)
                bytecode[jump_pos + 1:jump_pos + 3] = offset.to_bytes(2, byteorder='big')
                
                logger.debug(f"Compiled if ({left_var} {op} {right}) {{ {block} }}")
                return gas_cost, None

            return gas_cost, f"Unsupported statement: {stmt}"

        for stmt in statements:
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

        # Split statements
        def split_statements(body: str) -> List[str]:
            statements = []
            buffer = ""
            brace_count = 0
            in_if = False
            i = 0

            while i < len(body):
                char = body[i]
                buffer += char

                if char == '{':
                    brace_count += 1
                    if buffer.strip().startswith('if'):
                        in_if = True
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and in_if:
                        statements.append(buffer.strip())
                        buffer = ""
                        in_if = False
                elif char == ';' and brace_count == 0:
                    if buffer.strip() and not in_if:
                        statements.append(buffer.strip().rstrip(';').strip())
                        buffer = ""
                i += 1

                # Handle remaining content
                if i == len(body) and buffer.strip():
                    if in_if:
                        statements.append(buffer.strip())
                    else:
                        lines = buffer.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                sub_statements = [s.strip() for s in line.split(';') if s.strip()]
                                statements.extend(sub_statements)

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

            # Assignment with division (e.g., foo = 100 / 5)
            div_match = re.match(r"(\w+)\s*=\s*(\d+)\s*/\s*(\d+)", stmt)
            if div_match:
                var, a, b = div_match.groups()
                if var not in state_vars:
                    return gas_cost, f"Variable {var} not declared"
                a, b = int(a), int(b)
                if b == 0:
                    return gas_cost, "Division by zero"
                key = get_storage_key(var)
                bytecode.extend([CoolOps.PUSH1, a])
                gas_cost += 3
                bytecode.extend([CoolOps.PUSH1, b])
                gas_cost += 3
                bytecode.append(CoolOps.DIV)
                gas_cost += 5
                bytecode.append(CoolOps.SSTORE)
                bytecode.extend(key)
                gas_cost += 20000
                write_keys.add(key)
                logger.debug(f"Compiled {var} = {a} / {b} at {key.hex()}")
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

            # If block (e.g., if (foo > bar) { baz = 10; })
            if_match = re.match(r"if\s*\(\s*(\w+)\s*(>|==|!=|<)\s*(\w+|\d+)\s*\)\s*\{([\s\S]*)$", stmt, re.DOTALL)
            if if_match:
                left_var, op, right, block = if_match.groups()
                if left_var not in state_vars:
                    return gas_cost, f"Variable {left_var} not declared"
                
                # Log block content for debugging
                logger.debug(f"If block content: '{block}'")
                
                # Determine if right is a variable or literal
                right_is_var = right in state_vars
                if right_is_var and right not in state_vars:
                    return gas_cost, f"Variable {right} not declared"
                
                # Generate storage keys
                left_key = get_storage_key(left_var)
                right_key = get_storage_key(right) if right_is_var else None
                
                # Load left variable
                bytecode.append(CoolOps.SLOAD)
                bytecode.extend(left_key)
                gas_cost += 200
                read_keys.add(left_key)
                
                # Load right operand
                if right_is_var:
                    bytecode.append(CoolOps.SLOAD)
                    bytecode.extend(right_key)
                    gas_cost += 200
                    read_keys.add(right_key)
                else:
                    try:
                        num = int(right)
                        bytecode.extend([CoolOps.PUSH1, num])
                        gas_cost += 3
                    except ValueError:
                        return gas_cost, f"Invalid number {right}"
                
                # Comparison opcode
                if op == ">":
                    bytecode.append(CoolOps.GT)
                elif op == "<":
                    bytecode.append(CoolOps.LT)
                elif op == "==":
                    bytecode.append(CoolOps.EQ)
                elif op == "!=":
                    bytecode.extend([CoolOps.EQ, CoolOps.NOT])
                    gas_cost += 3  # Extra for NOT
                gas_cost += 3  # Comparison cost
                
                # Placeholder for jump destination
                jump_pos = len(bytecode)
                bytecode.extend([CoolOps.JUMPI, 0, 0])  # Dummy offset
                gas_cost += 10
                
                # Compile block statements
                block_statements = split_statements(block)
                logger.debug(f"Block statements after split: {block_statements}")
                
                if not block_statements:
                    # Fallback: split by newlines and semicolons
                    block_statements = []
                    lines = block.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            sub_statements = [s.strip() for s in line.split(';') if s.strip()]
                            block_statements.extend(sub_statements)
                    logger.debug(f"Fallback block statements: {block_statements}")
                    if not block_statements:
                        return gas_cost, "If block is empty"
                
                for block_stmt in block_statements:
                    block_stmt = block_stmt.strip()
                    if block_stmt:
                        logger.debug(f"Compiling block statement: '{block_stmt}'")
                        gas_cost, error = compile_statement(block_stmt, bytecode, gas_cost, read_keys, write_keys)
                        if error:
                            return gas_cost, error
                
                # Set jump destination to skip block
                end_pos = len(bytecode)
                bytecode.append(CoolOps.JUMPDEST)
                gas_cost += 1
                
                # Update JUMPI offset
                offset = end_pos - (jump_pos + 3)
                bytecode[jump_pos + 1:jump_pos + 3] = offset.to_bytes(2, byteorder='big')
                
                logger.debug(f"Compiled if ({left_var} {op} {right}) {{ {block} }}")
                return gas_cost, None

            return gas_cost, f"Unsupported statement: {stmt}"

        for stmt in statements:
            gas_cost, error = compile_statement(stmt, bytecode, gas_cost, read_keys, write_keys)
            if error:
                return b"", 0, error, read_keys, write_keys

        bytecode.append(CoolOps.STOP)
        gas_cost += 0
        logger.info(f"Compiled bytecode: {bytecode.hex()}, Gas: {gas_cost}")
        return bytes(bytecode), gas_cost, None, read_keys, write_keys