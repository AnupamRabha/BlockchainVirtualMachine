# opcodes.py
# Defines custom opcodes for the BVM

class CoolOps:
    STOP = 0x00      # Halts execution
    PUSH1 = 0x60     # Pushes a 1-byte value
    ADD = 0x01       # Adds top two stack items
    SUB = 0x03       # Subtracts top two stack items
    SSTORE = 0x55    # Stores to persistent storage
    SLOAD = 0x54     # Loads from persistent storage
    JUMPI = 0x57     # Conditional jump
    JUMP = 0x56      # Unconditional jump
    MUL = 0x02       #Multiplication