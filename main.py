# main.py
import logging
import os
from typing import Tuple, Optional

from opcodes import CoolOps
from transaction import Transaction
from compiler import CCompiler, JavaCompiler, CppCompiler
from blockchain import Blockchain

logger = logging.getLogger(__name__)

def get_user_contract() -> Tuple[str, str, Optional[callable]]:
    print("Select a programming language for the smart contract:")
    print("1. C (expects .c file)")
    print("2. Java (expects .java file)")
    print("3. C++ (expects .cpp file)")
    choice = input("Enter 1, 2, or 3: ").strip()

    language_map = {
        "1": ("C", CCompiler.brew, ".c"),
        "2": ("Java", JavaCompiler.brew, ".java"),
        "3": ("C++", CppCompiler.brew, ".cpp")
    }

    if choice not in language_map:
        raise ValueError("Invalid language choice. Please select 1, 2, or 3.")

    language, compiler, expected_extension = language_map[choice]

    print(f"\nProvide a {language} smart contract file with a {expected_extension} extension.")
    print("Supported operations:")
    print("- Addition: var = a + b")
    print("- Subtraction: var = a - b")
    print("- Assignment: var = other_var")
    print("- Any variable names and function names are allowed")
    print("- Storage: Variables are mapped to unique 32-byte keys")
    print("Conditionals (if/else) and other operations are not supported.")
    print(f"Example {language} file content:")
    if language == "C":
        print("""
        #include <stdint.h>
        int foo;
        int bar;
        void calc() {
            foo = 100 - 30;
            bar = foo;
            foo = 20 + 10;
        }
        """)
    elif language == "Java":
        print("""
        public class Contract {
            public int foo;
            public int bar;
            public void calc() {
                foo = 100 - 30;
                bar = foo;
                foo = 20 + 10;
            }
        }
        """)
    else:  # C++
        print("""
        #include <cstdint>
        class Contract {
        public:
            int32_t foo;
            int32_t bar;
            void calc() {
                foo = 100 - 30;
                bar = foo;
                foo = 20 + 10;
            }
        };
        """)
    file_path = input(f"Enter the full path to your {language} contract file (e.g., D:\\path\\contract{expected_extension}): ").strip()

    if not file_path.lower().endswith(expected_extension):
        raise ValueError(f"File must have a {expected_extension} extension for {language} contracts.")

    if not os.path.isfile(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            contract_code = f.read().strip()
    except IOError as e:
        raise ValueError(f"Error reading file {file_path}: {e}")

    if not contract_code:
        raise ValueError(f"File {file_path} is empty.")

    return language, contract_code, compiler

def main():
    try:
        language, contract_code, compiler = get_user_contract()
        logger.info(f"\n--- Processing {language} Contract ---")
        bytecode, gas_cost, error, read_keys, write_keys = compiler(contract_code)
        if error:
            logger.error(f"Compilation failed: {error}")
            return

        read_transactions = [
            Transaction(
                bytecode=bytes([CoolOps.SLOAD, *key, CoolOps.STOP]),
                call_data=b"",
                read_keys={key},
                write_keys=set()
            ) for key in write_keys
        ]

        blockchain = Blockchain()
        transactions = [
            Transaction(
                bytecode=bytecode,
                call_data=b"",
                read_keys=read_keys,
                write_keys=write_keys
            )
        ] + read_transactions

        receipts = blockchain.process_transactions(transactions)
        logger.info("Final Global Storage:")
        logger.info(blockchain.global_storage)

    except ValueError as e:
        logger.error(f"Input error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    from logging_config import configure_logging
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Uncomment for verbose output
    main()