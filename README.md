
# 🧠 Blockchain Compiler Suite

## Overview

This project is a **compiler suite** that translates high-level smart contract code written in **C**, **C++**, **Java**, and **Solidity** into **bytecode** for execution on a custom-built **Blockchain Virtual Machine (BVM)**.

It supports:
- Arithmetic operations (`+`, `-`, `*`, `/`)
- Variable assignments
- Efficient bytecode generation with **gas tracking**, **storage key hashing**, and **error handling** for blockchain-ready deployment.

---

## 📦 Project Structure

```
blockchain-compiler/
├── blockchain.py         # Blockchain state management
├── compiler.py           # Language-specific compiler implementations
├── logging_config.py     # Logging configuration
├── main.py               # Main entry point
├── opcodes.py            # Custom opcode definitions
├── transaction.py        # Transaction processing logic
├── vm.py                 # Blockchain Virtual Machine
├── contract.c            # Example contract (C)
└── README.md             # This file
```

---

## 🚀 Features

### ✅ Language Support

| Language | Features Supported |
|---------|--------------------|
| **C / C++ / Java** | `int` state variables, arithmetic ops, assignments, `if` conditions |
| **Solidity** | `uint256` public variables, same operations as C |

> ℹ️ Java and C++ currently inherit behavior from the C compiler.

---

### ⚙️ Bytecode Generation

- Uses opcodes like: `PUSH1`, `SSTORE`, `SLOAD`, `GT`, `JUMPI`, etc.
- **Gas cost tracking** per operation:
  - `SSTORE`: 20,000 gas
  - `SLOAD`: 200 gas
- **Storage key management** using SHA-256 hashing of variable names.

---

### ❌ Current Limitations

- No support for:
  - `<`, `==`, `!=`, `>=`, `<=` in conditionals
  - `if`, `else` clauses
  - Loops (`for`, `while`)
  - Solidity-specific features like `require`, `events`, `mappings`

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AnupamRabha/BlockchainVirtualMachine.git
cd BlockchainVirtualMachine
```

### 2. (Optional) Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

---

## 📝 Example Contracts

### C Example (`contract.c`)
```c
#include <stdint.h>
int foo;
int bar;
void calc() {
    foo = 10 / 2;
    bar = 17 + 78;
}
```
`

---

## ▶️ Usage

Compile and execute your smart contract using:

```bash
python main.py contract.c
```

### Sample Output

```
--- Processing C Contract ---
INFO: Compiling C contract
DEBUG: Detected state variables: ['foo', 'bar']
DEBUG: Parsed statements: ['foo = 10 / 2', 'bar = 17 + 78']
DEBUG: Processing statement: 'foo = 10 / 2'
DEBUG: Compiled foo = 10 / 2 at 2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae
DEBUG: Processing statement: 'bar = 17 + 78'
DEBUG: Compiled bar = 17 + 78 at fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9
INFO: Compiled bytecode: 300a30020d3a2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae3011304e0a3afcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb900, Gas: 40020
INFO: Starting transaction processing
INFO: Created 2 batches .....

---

## 💡 Gas Costs

| Opcode     | Gas |
|------------|-----|
| `PUSH1`    | 3   |
| `ADD`      | 3   |
| `SUB`      | 5   |
| `MUL`      | 5   |
| `DIV`      | 5   |
| `SLOAD`    | 200 |
| `SSTORE`   | 20,000 |
| `GT`       | 3   |
| `JUMPI`    | 10  |
| `JUMP`     | 8   |
| `JUMPDEST` | 1   |
| `STOP`     | 0   |

🧮 Example contract gas usage: ~60,440 gas (varies with operations).

---
```

###  Test Locally
```bash
python main.py
```
---

## 🔭 Future Enhancements

- [ ] Add support for `<`, `==`, `!=`, `>=`, `<=` in `if` conditions
- [ ] Add `else` clause support
- [ ] Add loops (`for`, `while`)
- [ ] Implement function calls and local variables
- [ ] Add advanced Solidity support (`require`, `events`, `mappings`)
- [ ] Optimize gas usage for frequent ops
- [ ] Add unit tests for compilers and the BVM

---
---

## 📬 Contact

For feedback or questions, open an issue or reach out at **[anupam123rabha@gmail.com]**.

---
