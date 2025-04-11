# opcodes.py
# Defines custom opcodes for the BVM

# class CoolOps:
#     STOP = 0x00      # Halts execution
#     PUSH1 = 0x60     # Pushes a 1-byte value
#     ADD = 0x01       # Adds top two stack items
#     SUB = 0x03       # Subtracts top two stack items
#     SSTORE = 0x55    # Stores to persistent storage
#     SLOAD = 0x54     # Loads from persistent storage
#     JUMPI = 0x57     # Conditional jump
#     JUMP = 0x56      # Unconditional jump
#     MUL = 0x02       #Multiplication

#     # opcodes.py
from enum import IntEnum

class CoolOps(IntEnum):
    # Control Flow (10 opcodes)
    STOP         = 0x00  # Halt execution
    JUMP         = 0x01  # Jump to address
    JUMPI        = 0x02  # Jump if condition
    JUMPDEST     = 0x03  # Mark valid jump destination
    IF           = 0x04  # Begin if block (pseudo-opcode, compiles to JUMPI)
    ELSE         = 0x05  # Begin else block (pseudo-opcode, compiles to JUMP)
    ENDIF        = 0x06  # End if/else block (pseudo-opcode, marks destination)
    WHILE        = 0x07  # Begin while loop (pseudo-opcode, compiles to JUMPI)
    ENDWHILE     = 0x08  # End while loop (pseudo-opcode, loops back)
    FOR          = 0x09  # Begin for loop (pseudo-opcode, complex jump logic)

    # Arithmetic (20 opcodes)
    ADD          = 0x0A  # Addition
    SUB          = 0x0B  # Subtraction
    MUL          = 0x0C  # Multiplication
    DIV          = 0x0D  # Division
    MOD          = 0x0E  # Modulus
    EXP          = 0x0F  # Exponentiation
    ADDMOD       = 0x10  # Add then mod
    MULMOD       = 0x11  # Multiply then mod
    SIGNEXTEND   = 0x12  # Sign-extend
    NEG          = 0x13  # Negate
    INC          = 0x14  # Increment
    DEC          = 0x15  # Decrement
    SHL          = 0x16  # Shift left
    SHR          = 0x17  # Shift right
    SAR          = 0x18  # Arithmetic shift right
    AND          = 0x19  # Bitwise AND
    OR           = 0x1A  # Bitwise OR
    XOR          = 0x1B  # Bitwise XOR
    NOT          = 0x1C  # Bitwise NOT
    BYTE         = 0x1D  # Extract byte

    # Comparison (10 opcodes)
    EQ           = 0x1E  # Equal
    NEQ          = 0x1F  # Not equal
    LT           = 0x20  # Less than
    GT           = 0x21  # Greater than
    LE           = 0x22  # Less than or equal
    GE           = 0x23  # Greater than or equal
    ISZERO       = 0x24  # Check if zero
    CMP          = 0x25  # General comparison
    MIN          = 0x26  # Minimum
    MAX          = 0x27  # Maximum

    # Stack Manipulation (20 opcodes)
    POP          = 0x28  # Remove top item
    DUP1         = 0x29  # Duplicate top item
    DUP2         = 0x2A  # Duplicate 2nd item
    DUP3         = 0x2B  # Duplicate 3rd item
    DUP4         = 0x2C  # Duplicate 4th item
    SWAP1        = 0x2D  # Swap top with 2nd
    SWAP2        = 0x2E  # Swap top with 3rd
    SWAP3        = 0x2F  # Swap top with 4th
    PUSH1        = 0x30  # Push 1-byte value
    PUSH2        = 0x31  # Push 2-byte value
    PUSH4        = 0x32  # Push 4-byte value
    PUSH8        = 0x33  # Push 8-byte value
    PUSH16       = 0x34  # Push 16-byte value
    PUSH32       = 0x35  # Push 32-byte value
    MLOAD        = 0x36  # Load from memory
    MSTORE       = 0x37  # Store to memory
    MSTORE8      = 0x38  # Store 8-bit to memory
    SLOAD        = 0x39  # Load from storage (existing)
    SSTORE       = 0x3A  # Store to storage (existing)
    PC           = 0x3B  # Push program counter

    # Memory and Storage (20 opcodes)
    MSIZE        = 0x3C  # Memory size
    MCOPY        = 0x3D  # Copy memory
    SLOAD1       = 0x3E  # Load 1-byte from storage
    SSTORE1      = 0x3F  # Store 1-byte to storage
    SLOAD2       = 0x40  # Load 2-byte from storage
    SSTORE2      = 0x41  # Store 2-byte to storage
    SLOAD4       = 0x42  # Load 4-byte from storage
    SSTORE4      = 0x43  # Store 4-byte to storage
    SLOAD8       = 0x44  # Load 8-byte from storage
    SSTORE8      = 0x45  # Store 8-byte to storage
    MLOAD1       = 0x46  # Load 1-byte from memory
    MSTORE1      = 0x47  # Store 1-byte to memory
    MLOAD2       = 0x48  # Load 2-byte from memory
    MSTORE2      = 0x49  # Store 2-byte to memory
    MLOAD4       = 0x4A  # Load 4-byte from memory
    MSTORE4      = 0x4B  # Store 4-byte to memory
    MLOAD8       = 0x4C  # Load 8-byte from memory
    MSTORE8X     = 0x4D  # Extended 8-bit memory store
    SCLEAR       = 0x4E  # Clear storage slot
    MCLEAR       = 0x4F  # Clear memory slot

    # Logical and Bitwise (10 opcodes)
    LAND         = 0x50  # Logical AND
    LOR          = 0x51  # Logical OR
    LXOR         = 0x52  # Logical XOR
    LNOT         = 0x53  # Logical NOT
    BITSET       = 0x54  # Set bit
    BITCLEAR     = 0x55  # Clear bit
    BITTEST      = 0x56  # Test bit
    SHL8         = 0x57  # Shift left 8 bits
    SHR8         = 0x58  # Shift right 8 bits
    SAR8         = 0x59  # Arithmetic shift right 8 bits

    # System and Environment (20 opcodes)
    GAS          = 0x5A  # Remaining gas
    ADDRESS      = 0x5B  # Current address
    BALANCE      = 0x5C  # Account balance
    CALLER       = 0x5D  # Caller address
    CALLVALUE    = 0x5E  # Call value
    CODESIZE     = 0x5F  # Code size
    CODECOPY     = 0x60  # Copy code
    RETURNDATASIZE = 0x61  # Return data size
    RETURNDATACOPY = 0x62  # Copy return data
    EXTCODESIZE  = 0x63  # External code size
    EXTCODECOPY  = 0x64  # Copy external code
    BLOCKHASH    = 0x65  # Block hash
    COINBASE     = 0x66  # Coinbase address
    TIMESTAMP    = 0x67  # Block timestamp
    NUMBER       = 0x68  # Block number
    DIFFICULTY   = 0x69  # Block difficulty
    GASLIMIT     = 0x6A  # Block gas limit
    CHAINID      = 0x6B  # Chain ID
    SELFBALANCE  = 0x6C  # Self balance
    BASEFEE      = 0x6D  # Base fee

    # Call and Return (20 opcodes)
    CALL         = 0x6E  # Call contract
    CALLCODE     = 0x6F  # Call code
    DELEGATECALL = 0x70  # Delegate call
    STATICCALL   = 0x71  # Static call
    RETURN       = 0x72  # Return data
    REVERT       = 0x73  # Revert execution
    SELFDESTRUCT = 0x74  # Self-destruct
    CREATE       = 0x75  # Create contract
    CREATE2      = 0x76  # Create contract with salt
    CALLDATASIZE = 0x77  # Call data size
    CALLDATACOPY = 0x78  # Copy call data
    CALLDATALOAD = 0x79  # Load call data
    RETURNDATA   = 0x7A  # Push return data
    LOG0         = 0x7B  # Log with 0 topics
    LOG1         = 0x7C  # Log with 1 topic
    LOG2         = 0x7D  # Log with 2 topics
    LOG3         = 0x7E  # Log with 3 topics
    LOG4         = 0x7F  # Log with 4 topics
    EVENT        = 0x80  # Emit event
    THROW        = 0x81  # Throw exception

    # Debugging and Misc (80 opcodes to reach 200)
    DEBUG        = 0x82  # Debug breakpoint
    TRACE        = 0x83  # Trace execution
    ASSERT       = 0x84  # Assert condition
    PRINT        = 0x85  # Print stack top
    NOP          = 0x86  # No operation
    TIME         = 0x87  # Current time
    RAND         = 0x88  # Random number
    HALT         = 0x89  # Alias for STOP
    # Reserved opcodes (0x8A to 0xC7)
    RESERVED_8A  = 0x8A
    RESERVED_8B  = 0x8B
    # ... (incrementing hex values)
    RESERVED_C6  = 0xC6
    RESERVED_C7  = 0xC7  # 200th opcode

    # Fill remaining opcodes dynamically
    @classmethod
    def _missing_(cls, value):
        if 0x8A <= value <= 0xC7:
            return cls(value)  # Treat as reserved
        raise ValueError(f"No opcode defined for {hex(value)}")