# blockchain.py
# Manages transaction processing and storage with dynamic keys

import copy
from multiprocessing import Pool
import logging
from typing import List, Dict

from transaction import Transaction, Receipt
from vm import BVM

logger = logging.getLogger(__name__)

class Blockchain:
    def __init__(self):
        self.global_storage: Dict[bytes, int] = {}

    def run_batch(self, transactions: List[Transaction]) -> Receipt:
        """Execute a batch of transactions."""
        logger.info(f"Processing batch of {len(transactions)} transactions")
        local_storage = copy.deepcopy(self.global_storage)
        batch_logs = []
        total_gas = 0
        success = True

        for i, tx in enumerate(transactions):
            logger.info(f"Transaction {i + 1}: Bytecode={tx.bytecode.hex()}")
            vm = BVM(tx.bytecode, gas_limit=1000000, call_data=tx.call_data,
                     read_keys=tx.read_keys, write_keys=tx.write_keys)
            vm.storage = copy.deepcopy(local_storage)
            receipt = vm.execute()
            total_gas += receipt.gas_used
            batch_logs.extend(receipt.logs)
            if receipt.success:
                local_storage.update(receipt.storage)
                logger.info(f"Transaction {i + 1} succeeded")
            else:
                success = False
                logger.warning(f"Transaction {i + 1} failed")
        return Receipt(success, total_gas, batch_logs, local_storage)

    def process_transactions(self, transactions: List[Transaction]) -> List[Receipt]:
        """Process transactions in parallel batches."""
        logger.info("Starting transaction processing")
        batches = []
        current_batch = []

        for tx in transactions:
            conflicts = any(
                any(w in tx.read_keys or w in tx.write_keys for w in prev.write_keys) or
                any(r in tx.write_keys for r in prev.read_keys)
                for prev in current_batch
            )
            if conflicts and current_batch:
                batches.append(current_batch)
                current_batch = []
            current_batch.append(tx)
        if current_batch:
            batches.append(current_batch)

        logger.info(f"Created {len(batches)} batches")
        with Pool() as pool:
            receipts = pool.map(self.run_batch, batches)

        for i, receipt in enumerate(receipts):
            if receipt.success:
                self.global_storage.update(receipt.storage)
                logger.info(f"Merged batch {i + 1}: {receipt.storage}")
            else:
                logger.warning(f"Batch {i + 1} failed")
        return receipts