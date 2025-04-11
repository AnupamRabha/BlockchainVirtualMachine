# transaction.py
# Defines Transaction and Receipt dataclasses with flexible storage keys

from dataclasses import dataclass
from typing import List, Dict, Set

@dataclass
class Transaction:
    bytecode: bytes
    call_data: bytes
    read_keys: Set[bytes]  # Changed to Set for uniqueness
    write_keys: Set[bytes]  # Changed to Set for uniqueness

@dataclass
class Receipt:
    success: bool
    gas_used: int
    logs: List[str]
    storage: Dict[bytes, int]