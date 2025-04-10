// use std::collections::HashMap;
// use rayon::prelude::*;
// use std::sync::Mutex;

// // Define opcodes
// #[repr(u8)]
// enum Opcode {
//     Nop = 0x00,
//     Load = 0x01,
//     Add = 0x02,
//     Sub = 0x03,
//     Store = 0x04,
//     LoadState = 0x05,
//     JumpIfZero = 0x06,
//     Jump = 0x07,
//     CallExt = 0x08,
//     Halt = 0xff,
// }

// #[derive(Debug)]
// struct Instruction {
//     opcode: u8,
//     args: Vec<u8>,
// }

// #[derive(Debug, Clone)]
// struct Transaction {
//     bytecode: Vec<u8>,
//     reads: Vec<String>,
//     writes: Vec<String>,
// }

// struct RustBVM {
//     registers: [i32; 16],
//     program_counter: usize,
//     gas_remaining: u64,
//     gas_costs: HashMap<u8, u64>,
//     state: HashMap<String, i32>,
//     ir: Vec<Instruction>,
//     running: bool,
//     reverted: bool,
// }

// impl RustBVM {
//     fn new(bytecode: Vec<u8>, gas_limit: u64) -> Self {
//         let mut gas_costs = HashMap::new();
//         gas_costs.insert(Opcode::Nop as u8, 1);
//         gas_costs.insert(Opcode::Load as u8, 5);
//         gas_costs.insert(Opcode::Add as u8, 10);
//         gas_costs.insert(Opcode::Sub as u8, 10);
//         gas_costs.insert(Opcode::Store as u8, 20);
//         gas_costs.insert(Opcode::LoadState as u8, 15);
//         gas_costs.insert(Opcode::JumpIfZero as u8, 15);
//         gas_costs.insert(Opcode::Jump as u8, 10);
//         gas_costs.insert(Opcode::CallExt as u8, 100);
//         gas_costs.insert(Opcode::Halt as u8, 0);

//         let ir = Self::precompile(&bytecode);
//         RustBVM {
//             registers: [0; 16],
//             program_counter: 0,
//             gas_remaining: gas_limit,
//             gas_costs,
//             state: HashMap::new(),
//             ir,
//             running: true,
//             reverted: false,
//         }
//     }

//     fn precompile(bytecode: &[u8]) -> Vec<Instruction> {
//         let mut ir = Vec::new();
//         let mut pc = 0;
//         while pc < bytecode.len() {
//             let opcode = bytecode[pc];
//             let (args, len) = match opcode {
//                 op if op == Opcode::Load as u8 => (bytecode[pc + 1..pc + 6].to_vec(), 6),
//                 op if op == Opcode::Add as u8 => (bytecode[pc + 1..pc + 4].to_vec(), 4),
//                 op if op == Opcode::Sub as u8 => (bytecode[pc + 1..pc + 4].to_vec(), 4),
//                 op if op == Opcode::Store as u8 => {
//                     let key_len = bytecode[pc + 2] as usize;
//                     (bytecode[pc + 1..pc + 3 + key_len].to_vec(), 3 + key_len)
//                 }
//                 op if op == Opcode::LoadState as u8 => {
//                     let key_len = bytecode[pc + 2] as usize;
//                     (bytecode[pc + 1..pc + 3 + key_len].to_vec(), 3 + key_len)
//                 }
//                 op if op == Opcode::JumpIfZero as u8 => (bytecode[pc + 1..pc + 4].to_vec(), 4),
//                 op if op == Opcode::Jump as u8 => (bytecode[pc + 1..pc + 3].to_vec(), 3),
//                 _ => (vec![], 1),
//             };
//             ir.push(Instruction { opcode, args });
//             pc += len;
//         }
//         ir
//     }

//     fn consume_gas(&mut self, opcode: u8) -> bool {
//         if let Some(cost) = self.gas_costs.get(&opcode) {
//             if self.gas_remaining >= *cost {
//                 self.gas_remaining -= *cost;
//                 return true;
//             }
//         }
//         self.revert("Out of gas or unknown opcode");
//         false
//     }

//     fn revert(&mut self, reason: &str) {
//         println!("Reverted: {}", reason);
//         self.running = false;
//         self.reverted = true;
//     }

//     fn step(&mut self) {
//         if !self.running || self.program_counter >= self.ir.len() {
//             self.running = false;
//             return;
//         }

//         let opcode = self.ir[self.program_counter].opcode;
//         let args = self.ir[self.program_counter].args.clone();

//         if !self.consume_gas(opcode) {
//             return;
//         }

//         match opcode {
//             op if op == Opcode::Nop as u8 => self.program_counter += 1,
//             op if op == Opcode::Load as u8 => {
//                 let reg = args[0] as usize;
//                 let value = i32::from_le_bytes(args[1..5].try_into().unwrap());
//                 self.registers[reg] = value;
//                 self.program_counter += 1;
//             }
//             op if op == Opcode::Add as u8 => {
//                 let reg1 = args[0] as usize;
//                 let reg2 = args[1] as usize;
//                 let dest = args[2] as usize;
//                 self.registers[dest] = self.registers[reg1] + self.registers[reg2];
//                 self.program_counter += 1;
//             }
//             op if op == Opcode::Sub as u8 => {
//                 let reg1 = args[0] as usize;
//                 let reg2 = args[1] as usize;
//                 let dest = args[2] as usize;
//                 self.registers[dest] = self.registers[reg1] - self.registers[reg2];
//                 self.program_counter += 1;
//             }
//             op if op == Opcode::Store as u8 => {
//                 let reg = args[0] as usize;
//                 let key_len = args[1] as usize;
//                 let key = String::from_utf8(args[2..2 + key_len].to_vec()).unwrap();
//                 self.state.insert(key, self.registers[reg]);
//                 self.program_counter += 1;
//             }
//             op if op == Opcode::LoadState as u8 => {
//                 let reg = args[0] as usize;
//                 let key_len = args[1] as usize;
//                 let key = String::from_utf8(args[2..2 + key_len].to_vec()).unwrap();
//                 self.registers[reg] = *self.state.get(&key).unwrap_or(&0);
//                 self.program_counter += 1;
//             }
//             op if op == Opcode::JumpIfZero as u8 => {
//                 let reg = args[0] as usize;
//                 let target = u16::from_le_bytes(args[1..3].try_into().unwrap()) as usize;
//                 if self.registers[reg] == 0 {
//                     self.program_counter = target;
//                 } else {
//                     self.program_counter += 1;
//                 }
//             }
//             op if op == Opcode::Jump as u8 => {
//                 let target = u16::from_le_bytes(args[0..2].try_into().unwrap()) as usize;
//                 self.program_counter = target;
//             }
//             op if op == Opcode::CallExt as u8 => {
//                 println!("External call executed (placeholder)");
//                 self.program_counter += 1;
//             }
//             op if op == Opcode::Halt as u8 => self.running = false,
//             _ => self.revert("Unknown opcode"),
//         }
//     }

//     fn run(&mut self) {
//         while self.running {
//             self.step();
//         }
//     }
// }

// struct Compiler;

// impl Compiler {
//     fn compile(script: &str) -> Vec<u8> {
//         let mut bytecode = Vec::new();
//         let mut labels = HashMap::new();
//         let mut unresolved_jumps = Vec::new();
//         let mut pc = 0;

//         for (i, line) in script.lines().enumerate() {
//             let line = line.trim();
//             if line.is_empty() || line.starts_with('#') {
//                 continue;
//             }
//             if line.ends_with(':') {
//                 labels.insert(line[..line.len() - 1].to_string(), pc);
//                 continue;
//             }
//             let parts: Vec<&str> = line.split_whitespace().collect();
//             match parts[0] {
//                 "load" => {
//                     let reg = parts[1].parse::<u8>().unwrap();
//                     let value = parts[2].parse::<i32>().unwrap();
//                     bytecode.push(Opcode::Load as u8);
//                     bytecode.push(reg);
//                     bytecode.extend_from_slice(&value.to_le_bytes());
//                     pc += 6;
//                 }
//                 "add" => {
//                     let reg1 = parts[1].parse::<u8>().unwrap();
//                     let reg2 = parts[2].parse::<u8>().unwrap();
//                     let dest = parts[3].parse::<u8>().unwrap();
//                     bytecode.push(Opcode::Add as u8);
//                     bytecode.push(reg1);
//                     bytecode.push(reg2);
//                     bytecode.push(dest);
//                     pc += 4;
//                 }
//                 "sub" => {
//                     let reg1 = parts[1].parse::<u8>().unwrap();
//                     let reg2 = parts[2].parse::<u8>().unwrap();
//                     let dest = parts[3].parse::<u8>().unwrap();
//                     bytecode.push(Opcode::Sub as u8);
//                     bytecode.push(reg1);
//                     bytecode.push(reg2);
//                     bytecode.push(dest);
//                     pc += 4;
//                 }
//                 "store" => {
//                     let reg = parts[1].parse::<u8>().unwrap();
//                     let key = parts[2];
//                     bytecode.push(Opcode::Store as u8);
//                     bytecode.push(reg);
//                     bytecode.push(key.len() as u8);
//                     bytecode.extend_from_slice(key.as_bytes());
//                     pc += 3 + key.len();
//                 }
//                 "jz" => {
//                     let reg = parts[1].parse::<u8>().unwrap();
//                     let label = parts[2];
//                     bytecode.push(Opcode::JumpIfZero as u8);
//                     bytecode.push(reg);
//                     bytecode.extend_from_slice(&[0, 0]);
//                     unresolved_jumps.push((pc + 2, label.to_string(), i)); // Adjusted to point to target bytes
//                     pc += 4;
//                 }
//                 "jump" => {
//                     let label = parts[1];
//                     bytecode.push(Opcode::Jump as u8);
//                     bytecode.extend_from_slice(&[0, 0]);
//                     unresolved_jumps.push((pc + 1, label.to_string(), i));
//                     pc += 3;
//                 }
//                 "halt" => {
//                     bytecode.push(Opcode::Halt as u8);
//                     pc += 1;
//                 }
//                 _ => panic!("Unknown instruction: {} at line {}", parts[0], i + 1),
//             }
//         }

//         for (pos, label, line) in unresolved_jumps {
//             if let Some(&target) = labels.get(&label) {
//                 let target_bytes = (target as u16).to_le_bytes();
//                 bytecode[pos] = target_bytes[0];
//                 bytecode[pos + 1] = target_bytes[1];
//             } else {
//                 panic!("Unknown label '{}' at line {}", label, line + 1);
//             }
//         }

//         bytecode
//     }

//     fn disassemble(bytecode: &[u8]) -> String {
//         let mut result = String::new();
//         let mut pc = 0;
//         while pc < bytecode.len() {
//             let opcode = bytecode[pc];
//             result.push_str(&format!("{:04x}: ", pc));
//             match opcode {
//                 op if op == Opcode::Load as u8 => {
//                     let reg = bytecode[pc + 1];
//                     let value = i32::from_le_bytes(bytecode[pc + 2..pc + 6].try_into().unwrap());
//                     result.push_str(&format!("load {} {}\n", reg, value));
//                     pc += 6;
//                 }
//                 op if op == Opcode::Add as u8 => {
//                     let reg1 = bytecode[pc + 1];
//                     let reg2 = bytecode[pc + 2];
//                     let dest = bytecode[pc + 3];
//                     result.push_str(&format!("add {} {} {}\n", reg1, reg2, dest));
//                     pc += 4;
//                 }
//                 op if op == Opcode::Sub as u8 => {
//                     let reg1 = bytecode[pc + 1];
//                     let reg2 = bytecode[pc + 2];
//                     let dest = bytecode[pc + 3];
//                     result.push_str(&format!("sub {} {} {}\n", reg1, reg2, dest));
//                     pc += 4;
//                 }
//                 op if op == Opcode::Store as u8 => {
//                     let reg = bytecode[pc + 1];
//                     let key_len = bytecode[pc + 2] as usize;
//                     let key = String::from_utf8(bytecode[pc + 3..pc + 3 + key_len].to_vec()).unwrap();
//                     result.push_str(&format!("store {} {}\n", reg, key));
//                     pc += 3 + key_len;
//                 }
//                 op if op == Opcode::JumpIfZero as u8 => {
//                     let reg = bytecode[pc + 1];
//                     let target = u16::from_le_bytes(bytecode[pc + 2..pc + 4].try_into().unwrap());
//                     result.push_str(&format!("jz {} {:04x}\n", reg, target));
//                     pc += 4;
//                 }
//                 op if op == Opcode::Jump as u8 => {
//                     let target = u16::from_le_bytes(bytecode[pc + 1..pc + 3].try_into().unwrap());
//                     result.push_str(&format!("jump {:04x}\n", target));
//                     pc += 3;
//                 }
//                 op if op == Opcode::Halt as u8 => {
//                     result.push_str("halt\n");
//                     pc += 1;
//                 }
//                 _ => {
//                     result.push_str(&format!("unknown opcode {}\n", opcode));
//                     pc += 1;
//                 }
//             }
//         }
//         result
//     }
// }

// struct BlockchainSimulator {
//     state: Mutex<HashMap<String, i32>>,
// }

// impl BlockchainSimulator {
//     fn new() -> Self {
//         BlockchainSimulator {
//             state: Mutex::new(HashMap::new()),
//         }
//     }

//     fn execute_transactions(&self, txs: Vec<Transaction>) {
//         let mut independent_groups = Vec::new();
//         let mut current_group = Vec::new();

//         for tx in txs {
//             let conflicts = current_group.iter().any(|prev: &Transaction| {
//                 prev.writes.iter().any(|w| tx.reads.contains(w) || tx.writes.contains(w)) ||
//                 prev.reads.iter().any(|r| tx.writes.contains(r))
//             });
//             if conflicts && !current_group.is_empty() {
//                 independent_groups.push(current_group);
//                 current_group = Vec::new();
//             }
//             current_group.push(tx);
//         }
//         if !current_group.is_empty() {
//             independent_groups.push(current_group);
//         }

//         independent_groups.par_iter().for_each(|group| {
//             let results: Vec<_> = group.iter().map(|tx| {
//                 let mut vm = RustBVM::new(tx.bytecode.clone(), 1000);
//                 vm.state = self.state.lock().unwrap().clone();
//                 vm.run();
//                 (vm.reverted, vm.state)
//             }).collect();

//             let mut state = self.state.lock().unwrap();
//             for (reverted, vm_state) in results {
//                 if !reverted {
//                     for (key, value) in vm_state.iter() {
//                         state.insert(key.clone(), *value);
//                     }
//                 }
//             }
//         });
//     }
// }

// fn main() {
//     let bytecode = vec![
//         Opcode::Load as u8, 0, 42, 0, 0, 0,
//         Opcode::Load as u8, 1, 58, 0, 0, 0,
//         Opcode::Add as u8, 0, 1, 2,
//         Opcode::Store as u8, 2, 6, b'r', b'e', b's', b'u', b'l', b't',
//         Opcode::Halt as u8,
//     ];
//     println!("Bytecode disassembled:\n{}", Compiler::disassemble(&bytecode));
//     let mut vm = RustBVM::new(bytecode, 1000);
//     vm.run();
//     println!("State after execution: {:?}", vm.state);
//     println!("Gas remaining: {}", vm.gas_remaining);

//     let script = "
//         load 0 10
//         load 1 5
//         sub 0 1 2    # reg2 = 10 - 5
//     loop:
//         store 2 counter
//         sub 2 1 2    # reg2 -= 1
//         jz 2 done    # Jump to 'done' if reg2 == 0
//         jump loop    # Jump back to 'loop'
//     done:
//         halt
//     ";
//     let compiled = Compiler::compile(script);
//     println!("Compiled script bytecode:\n{}", Compiler::disassemble(&compiled));
//     let mut vm2 = RustBVM::new(compiled, 1000);
//     vm2.run();
//     println!("State after compiled script: {:?}", vm2.state);

//     let simulator = BlockchainSimulator::new();
//     let tx1 = Transaction {
//         bytecode: Compiler::compile("load 0 100\nstore 0 balance\nhalt"),
//         reads: vec![],
//         writes: vec!["balance".to_string()],
//     };
//     let tx2 = Transaction {
//         bytecode: Compiler::compile("load 0 200\nstore 0 balance\nhalt"),
//         reads: vec![],
//         writes: vec!["balance".to_string()],
//     };
//     let tx3 = Transaction {
//         bytecode: Compiler::compile("load 0 300\nstore 0 other\nhalt"),
//         reads: vec![],
//         writes: vec!["other".to_string()],
//     };
//     simulator.execute_transactions(vec![tx1, tx2, tx3]);
//     println!("Blockchain state after parallel txs: {:?}", simulator.state.lock().unwrap());
// }

use std::collections::HashMap;
use rayon::prelude::*; // For some cool parallel stuff
use std::sync::Mutex;

// My custom opcodes for the VM
#[repr(u8)]
enum MyOpcodes {
    Chill = 0x00,      // Do nothing, just vibe
    PushNum = 0x01,    // Push a number onto the stack
    AddEm = 0x02,      // Add the top two stack numbers
    SubEm = 0x03,      // Subtract the top two stack numbers
    SaveIt = 0x04,     // Save a value to state
    GrabMem = 0x05,    // Grab something from memory
    JumpIfNada = 0x06, // Jump if the top is zero
    JumpAlways = 0x07, // Jump no matter what
    CallOutside = 0x08,// Call something external (placeholder)
    Stop = 0xff,       // Halt the machine
}

// A little struct to hold my instructions
#[derive(Debug)]
struct MyInstruction {
    code: u8,
    extras: Vec<u8>, // Extra bytes for the instruction
}

// For transactions in my blockchain sim
#[derive(Debug, Clone)]
struct MyTx {
    code: Vec<u8>,
    reads: Vec<String>,
    writes: Vec<String>,
}

// My very own Blockchain VM!
struct MyBVM {
    stack: Vec<i32>,            // Where I keep my numbers
    mem: Vec<u8>,               // Some memory to play with
    pc: usize,                  // Program counter, keeps track of where I am
    gas_left: u64,              // How much gas I’ve got
    gas_prices: HashMap<u8, u64>, // How much each opcode costs
    storage: HashMap<String, i32>, // Where I save important stuff
    program: Vec<MyInstruction>,  // My bytecode lives here
    active: bool,               // Am I still running?
    oops: bool,                 // Did something go wrong?
}

impl MyBVM {
    // Start up my VM with some bytecode and gas
    fn kick_off(code: Vec<u8>, gas: u64) -> Self {
        let mut prices = HashMap::new();
        prices.insert(MyOpcodes::Chill as u8, 1);
        prices.insert(MyOpcodes::PushNum as u8, 5);
        prices.insert(MyOpcodes::AddEm as u8, 10);
        prices.insert(MyOpcodes::SubEm as u8, 10);
        prices.insert(MyOpcodes::SaveIt as u8, 20);
        prices.insert(MyOpcodes::GrabMem as u8, 15);
        prices.insert(MyOpcodes::JumpIfNada as u8, 15);
        prices.insert(MyOpcodes::JumpAlways as u8, 10);
        prices.insert(MyOpcodes::CallOutside as u8, 100);
        prices.insert(MyOpcodes::Stop as u8, 0);

        let program = Self::break_it_down(&code);
        MyBVM {
            stack: Vec::with_capacity(1024), // Big enough stack
            mem: vec![0; 1024],             // 1KB of memory to mess with
            pc: 0,                          // Start at the beginning
            gas_left: gas,                  // Gas to burn
            gas_prices: prices,             // My price list
            storage: HashMap::new(),        // Empty storage to start
            program,                        // Load up my code
            active: true,                   // Let’s go!
            oops: false,                    // No mistakes yet
        }
    }

    // Turn raw bytes into instructions I can use
    fn break_it_down(code: &[u8]) -> Vec<MyInstruction> {
        let mut instructions = Vec::new();
        let mut pos = 0;
        while pos < code.len() {
            let opcode = code[pos];
            let (extras, size) = match opcode {
                op if op == MyOpcodes::PushNum as u8 => (code[pos + 1..pos + 5].to_vec(), 5),
                op if op == MyOpcodes::AddEm as u8 => (vec![], 1),
                op if op == MyOpcodes::SubEm as u8 => (vec![], 1),
                op if op == MyOpcodes::SaveIt as u8 => {
                    let key_size = code[pos + 1] as usize;
                    (code[pos + 1..pos + 2 + key_size].to_vec(), 2 + key_size)
                }
                op if op == MyOpcodes::GrabMem as u8 => (code[pos + 1..pos + 3].to_vec(), 3),
                op if op == MyOpcodes::JumpIfNada as u8 => (code[pos + 1..pos + 3].to_vec(), 3),
                op if op == MyOpcodes::JumpAlways as u8 => (code[pos + 1..pos + 3].to_vec(), 3),
                _ => (vec![], 1),
            };
            instructions.push(MyInstruction { code: opcode, extras });
            pos += size;
        }
        instructions
    }

    // Burn some gas, make sure I’ve got enough
    fn burn_gas(&mut self, opcode: u8) -> bool {
        if let Some(cost) = self.gas_prices.get(&opcode) {
            if self.gas_left >= *cost {
                self.gas_left -= *cost;
                return true;
            }
        }
        self.mess_up("Ran out of gas or bad opcode");
        false
    }

    // Oops, something went wrong
    fn mess_up(&mut self, why: &str) {
        println!("Oops: {}", why);
        self.active = false;
        self.oops = true;
    }

    // Do one step of my VM
    fn do_step(&mut self) {
        if !self.active || self.pc >= self.program.len() {
            self.active = false;
            return;
        }

        let opcode = self.program[self.pc].code;
        let extras = self.program[self.pc].extras.clone(); // Copy this so I don’t borrow weirdly

        if !self.burn_gas(opcode) {
            return;
        }

        match opcode {
            op if op == MyOpcodes::Chill as u8 => self.pc += 1,
            op if op == MyOpcodes::PushNum as u8 => {
                let num = i32::from_le_bytes(extras[0..4].try_into().unwrap());
                self.stack.push(num);
                self.pc += 1;
            }
            op if op == MyOpcodes::AddEm as u8 => {
                let num2 = self.stack.pop().unwrap_or(0);
                let num1 = self.stack.pop().unwrap_or(0);
                self.stack.push(num1 + num2);
                self.pc += 1;
            }
            op if op == MyOpcodes::SubEm as u8 => {
                let num2 = self.stack.pop().unwrap_or(0);
                let num1 = self.stack.pop().unwrap_or(0);
                self.stack.push(num1 - num2);
                self.pc += 1;
            }
            op if op == MyOpcodes::SaveIt as u8 => {
                let key_size = extras[0] as usize;
                let key = String::from_utf8(extras[1..1 + key_size].to_vec()).unwrap();
                let value = self.stack.pop().unwrap_or(0);
                self.storage.insert(key, value);
                self.pc += 1;
            }
            op if op == MyOpcodes::GrabMem as u8 => {
                let spot = u16::from_le_bytes(extras[0..2].try_into().unwrap()) as usize;
                let value = i32::from_le_bytes(self.mem[spot..spot + 4].try_into().unwrap());
                self.stack.push(value);
                self.pc += 1;
            }
            op if op == MyOpcodes::JumpIfNada as u8 => {
                let check = self.stack.pop().unwrap_or(0);
                let jump_to = u16::from_le_bytes(extras[0..2].try_into().unwrap()) as usize;
                if check == 0 {
                    self.pc = jump_to;
                } else {
                    self.pc += 1;
                }
            }
            op if op == MyOpcodes::JumpAlways as u8 => {
                let jump_to = u16::from_le_bytes(extras[0..2].try_into().unwrap()) as usize;
                self.pc = jump_to;
            }
            op if op == MyOpcodes::CallOutside as u8 => {
                println!("Calling something outside (just pretending for now)");
                self.pc += 1;
            }
            op if op == MyOpcodes::Stop as u8 => self.active = false,
            _ => self.mess_up("What’s this opcode? I don’t know it!"),
        }
    }

    // Keep going until I stop
    fn keep_going(&mut self) {
        while self.active {
            self.do_step();
        }
    }
}

// My little compiler to turn scripts into bytecode
struct MyCompiler;

impl MyCompiler {
    fn make_code(script: &str) -> Vec<u8> {
        let mut bytes = Vec::new();
        let mut jumps_to_fix = Vec::new();
        let mut labels = HashMap::new();
        let mut pos = 0;

        for (line_num, line) in script.lines().enumerate() {
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            if line.ends_with(':') {
                labels.insert(line[..line.len() - 1].to_string(), pos);
                continue;
            }
            let bits: Vec<&str> = line.split_whitespace().collect();
            match bits[0] {
                "push" => {
                    let num = bits[1].parse::<i32>().unwrap();
                    bytes.push(MyOpcodes::PushNum as u8);
                    bytes.extend_from_slice(&num.to_le_bytes());
                    pos += 5;
                }
                "add" => {
                    bytes.push(MyOpcodes::AddEm as u8);
                    pos += 1;
                }
                "sub" => {
                    bytes.push(MyOpcodes::SubEm as u8);
                    pos += 1;
                }
                "save" => {
                    let key = bits[1];
                    bytes.push(MyOpcodes::SaveIt as u8);
                    bytes.push(key.len() as u8);
                    bytes.extend_from_slice(key.as_bytes());
                    pos += 2 + key.len();
                }
                "jz" => {
                    let label = bits[1];
                    bytes.push(MyOpcodes::JumpIfNada as u8);
                    bytes.extend_from_slice(&[0, 0]);
                    jumps_to_fix.push((pos + 1, label.to_string(), line_num));
                    pos += 3;
                }
                "jump" => {
                    let label = bits[1];
                    bytes.push(MyOpcodes::JumpAlways as u8);
                    bytes.extend_from_slice(&[0, 0]);
                    jumps_to_fix.push((pos + 1, label.to_string(), line_num));
                    pos += 3;
                }
                "stop" => {
                    bytes.push(MyOpcodes::Stop as u8);
                    pos += 1;
                }
                _ => panic!("Hey, I don’t know this command: {} (line {})", bits[0], line_num + 1),
            }
        }

        for (spot, label, line) in jumps_to_fix {
            if let Some(&target) = labels.get(&label) {
                let target_bytes = (target as u16).to_le_bytes();
                bytes[spot] = target_bytes[0];
                bytes[spot + 1] = target_bytes[1];
            } else {
                panic!("Can’t find label '{}' on line {}", label, line + 1);
            }
        }

        bytes
    }

    // Show what my bytecode looks like
    fn show_code(code: &[u8]) -> String {
        let mut output = String::new();
        let mut pos = 0;
        while pos < code.len() {
            let opcode = code[pos];
            output.push_str(&format!("{:04x}: ", pos));
            match opcode {
                op if op == MyOpcodes::PushNum as u8 => {
                    let num = i32::from_le_bytes(code[pos + 1..pos + 5].try_into().unwrap());
                    output.push_str(&format!("push {}\n", num));
                    pos += 5;
                }
                op if op == MyOpcodes::AddEm as u8 => {
                    output.push_str("add\n");
                    pos += 1;
                }
                op if op == MyOpcodes::SubEm as u8 => {
                    output.push_str("sub\n");
                    pos += 1;
                }
                op if op == MyOpcodes::SaveIt as u8 => {
                    let key_size = code[pos + 1] as usize;
                    let key = String::from_utf8(code[pos + 2..pos + 2 + key_size].to_vec()).unwrap();
                    output.push_str(&format!("save {}\n", key));
                    pos += 2 + key_size;
                }
                op if op == MyOpcodes::JumpIfNada as u8 => {
                    let target = u16::from_le_bytes(code[pos + 1..pos + 3].try_into().unwrap());
                    output.push_str(&format!("jz {:04x}\n", target));
                    pos += 3;
                }
                op if op == MyOpcodes::JumpAlways as u8 => {
                    let target = u16::from_le_bytes(code[pos + 1..pos + 3].try_into().unwrap());
                    output.push_str(&format!("jump {:04x}\n", target));
                    pos += 3;
                }
                op if op == MyOpcodes::Stop as u8 => {
                    output.push_str("stop\n");
                    pos += 1;
                }
                _ => {
                    output.push_str(&format!("weird opcode {}\n", opcode));
                    pos += 1;
                }
            }
        }
        output
    }
}

// My blockchain simulator to run stuff together
struct MyBlockchain {
    storage: Mutex<HashMap<String, i32>>,
}

impl MyBlockchain {
    fn start_fresh() -> Self {
        MyBlockchain {
            storage: Mutex::new(HashMap::new()),
        }
    }

    fn run_txs(&self, txs: Vec<MyTx>) {
        let mut groups = Vec::new();
        let mut current = Vec::new();

        for tx in txs {
            let clash = current.iter().any(|prev: &MyTx| {
                prev.writes.iter().any(|w| tx.reads.contains(w) || tx.writes.contains(w)) ||
                prev.reads.iter().any(|r| tx.writes.contains(r))
            });
            if clash && !current.is_empty() {
                groups.push(current);
                current = Vec::new();
            }
            current.push(tx);
        }
        if !current.is_empty() {
            groups.push(current);
        }

        groups.par_iter().for_each(|group| {
            let outcomes: Vec<_> = group.iter().map(|tx| {
                let mut vm = MyBVM::kick_off(tx.code.clone(), 1000);
                vm.storage = self.storage.lock().unwrap().clone();
                vm.keep_going();
                (vm.oops, vm.storage)
            }).collect();

            let mut shared_storage = self.storage.lock().unwrap();
            for (messed_up, vm_storage) in outcomes {
                if !messed_up {
                    for (key, value) in vm_storage.iter() {
                        shared_storage.insert(key.clone(), *value);
                    }
                }
            }
        });
    }
}

fn main() {
    // Test some raw bytecode
    let code = vec![
        MyOpcodes::PushNum as u8, 42, 0, 0, 0,
        MyOpcodes::PushNum as u8, 58, 0, 0, 0,
        MyOpcodes::AddEm as u8,
        MyOpcodes::SaveIt as u8, 6, b'r', b'e', b's', b'u', b'l', b't',
        MyOpcodes::Stop as u8,
    ];
    println!("Here’s my bytecode:\n{}", MyCompiler::show_code(&code));
    let mut vm = MyBVM::kick_off(code, 1000);
    vm.keep_going();
    println!("After running: {:?}", vm.storage);
    println!("Gas left: {}", vm.gas_left);

    // Try a little script I wrote
    let script = "
        push 10       # Start with 10
        push 5        # Then 5
        sub           # 10 - 5
    myloop:
        save count    # Save the top number
        sub           # Subtract 1
        jz alldone    # If it’s 0, we’re done
        jump myloop   # Keep going
    alldone:
        stop          # Finish up
    ";
    let my_code = MyCompiler::make_code(script);
    println!("My script in bytecode:\n{}", MyCompiler::show_code(&my_code));
    let mut vm2 = MyBVM::kick_off(my_code, 1000);
    vm2.keep_going();
    println!("Script result: {:?}", vm2.storage);

    // Test my blockchain sim
    let sim = MyBlockchain::start_fresh();
    let tx1 = MyTx {
        code: MyCompiler::make_code("push 100\nsave balance\nstop"),
        reads: vec![],
        writes: vec!["balance".to_string()],
    };
    let tx2 = MyTx {
        code: MyCompiler::make_code("push 200\nsave balance\nstop"),
        reads: vec![],
        writes: vec!["balance".to_string()],
    };
    let tx3 = MyTx {
        code: MyCompiler::make_code("push 300\nsave other\nstop"),
        reads: vec![],
        writes: vec!["other".to_string()],
    };
    sim.run_txs(vec![tx1, tx2, tx3]);
    println!("Blockchain storage: {:?}", sim.storage.lock().unwrap());
}