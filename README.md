<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blockchain Compiler Project</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 text-gray-800">
    <header class="bg-blue-900 text-white p-6 shadow-lg">
        <h1 class="text-3xl font-bold">Blockchain Compiler Project</h1>
        <p class="text-lg mt-2">Compile Smart Contracts into Executable Blockchain Bytecode</p>
    </header>

    <main class="p-6 space-y-6">
        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold mb-4">Overview</h2>
            <p>This project is a compiler suite designed to translate high-level smart contract code written in C, Java, C++, and Solidity into bytecode executable on a custom Blockchain Virtual Machine (BVM).</p>
            <ul class="list-disc ml-6 mt-2">
                <li>Compilers for C, Java, C++, and Solidity</li>
                <li>BVM to execute bytecode</li>
                <li>Transaction and blockchain management</li>
                <li>Custom opcodes and gas tracking</li>
                <li>Logging and debugging support</li>
            </ul>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold mb-4">Features</h2>
            <ul class="list-disc ml-6">
                <li>Language support: C, Java, C++, Solidity</li>
                <li>Bytecode generation with gas calculation</li>
                <li>Storage key tracking using SHA256</li>
                <li>Error handling with detailed messages</li>
                <li>Modular design for extensibility</li>
            </ul>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold mb-4">Installation</h2>
            <pre class="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
$ git clone https://github.com/yourusername/blockchain-compiler.git
$ cd blockchain-compiler
$ python -m venv venv
$ source venv/bin/activate  # Windows: venv\Scripts\activate</pre>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold mb-4">Usage</h2>
            <p>Create a contract file, then compile and run it:</p>
            <pre class="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
$ python main.py contract.c</pre>
            <p>Example contract (C):</p>
            <pre class="bg-gray-200 p-4 rounded text-sm overflow-x-auto">
#include &lt;stdint.h&gt;
int foo;
int bar;
void calc() {
    foo = 100 - 30;
    bar = foo * 2;
    if (bar > 50) {
        foo = 100 / 5;
    }
}</pre>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold mb-4">Gas Costs</h2>
            <ul class="list-disc ml-6">
                <li>PUSH1: 3 gas</li>
                <li>ADD: 3 gas</li>
                <li>SUB: 5 gas</li>
                <li>MUL: 5 gas</li>
                <li>DIV: 5 gas</li>
                <li>SLOAD: 200 gas</li>
                <li>SSTORE: 20,000 gas</li>
                <li>GT: 3 gas</li>
                <li>JUMPI: 10 gas</li>
                <li>JUMP: 8 gas</li>
                <li>JUMPDEST: 1 gas</li>
                <li>STOP: 0 gas</li>
            </ul>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold mb-4">Future Enhancements</h2>
            <ul class="list-disc ml-6">
                <li>Support for comparison operators (&lt;, ==, &gt;=, &lt;=, !=)</li>
                <li>Support for else clauses</li>
                <li>Loops (for, while)</li>
                <li>Function calls and local variables</li>
                <li>Solidity features like require, events, mappings</li>
                <li>Gas optimization for common operations</li>
            </ul>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold mb-4">Contributing</h2>
            <pre class="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
$ git checkout -b feature/your-feature
# Make changes and test
$ git push origin feature/your-feature
# Submit a Pull Request</pre>
        </section>

        <section class="bg-white rounded-xl shadow-md p-6">
            <h2 class="text-2xl font-bold mb-4">License & Contact</h2>
            <p>MIT License. See LICENSE for details.</p>
            <p>For feedback, open an issue or contact: <code>your.email@example.com</code></p>
        </section>
    </main>

    <footer class="text-center p-4 text-sm text-gray-600">
        &copy; 2025 Blockchain Compiler Project. All rights reserved.
    </footer>
</body>
</html>
