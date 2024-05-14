import streamlit as st
from dataclasses import dataclass, field
import datetime
import pandas as pd
import hashlib
from typing import List

# Define a data class to store transaction details. This will be the content of each block.
@dataclass
class Record:
    sender: str
    receiver: str
    amount: float
    timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Automatically generate timestamp

# Define a data class for the blocks in the blockchain.
@dataclass
class Block:
    record: Record
    creator_id: int
    prev_hash: str = "0"  # Hash of the previous block; default is "0" for the genesis block
    timestamp: str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # UTC timestamp of the block creation
    nonce: int = 0  # Nonce used in the proof of work

    # Method to compute the hash of the block using SHA-256.
    def hash_block(self) -> str:
        sha = hashlib.sha256()
        # Create a string by concatenating all the block information, used for hashing.
        components = (str(self.record) + str(self.creator_id) + self.timestamp + self.prev_hash + str(self.nonce)).encode()
        sha.update(components)
        return sha.hexdigest()

# Blockchain class managing the chain of blocks and blockchain operations.
@dataclass
class PyChain:
    chain: List[Block] = field(default_factory=list)  # List of blocks
    difficulty: int = 4  # Difficulty level of the proof of work required to add a block

    # Perform the proof of work; modifies the nonce until the hash meets the difficulty criteria.
    def proof_of_work(self, block: Block) -> Block:
        calculated_hash = block.hash_block()
        num_of_zeros = "0" * self.difficulty  # Difficulty criteria: Hash must start with this many zeros
        while not calculated_hash.startswith(num_of_zeros):
            block.nonce += 1  # Increment nonce to change the hash
            calculated_hash = block.hash_block()
        return block

    # Add a block to the chain after performing proof of work
    def add_block(self, candidate_block: Block) -> None:
        block = self.proof_of_work(candidate_block)
        self.chain.append(block)

    # Validate the integrity of the blockchain; each block's previous hash must match the hash of the preceding block
    def is_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.prev_hash != previous.hash_block():
                return False
        return True

# Initialize or retrieve the PyChain instance from Streamlit's session state
def get_pychain():
    if 'pychain' not in st.session_state:
        genesis_block = Block(record=Record(sender="Genesis", receiver="Genesis", amount=0), creator_id=0)
        st.session_state.pychain = PyChain(chain=[genesis_block])
    return st.session_state.pychain

pychain = get_pychain()

st.title("PyChain Ledger")

# Streamlit form to accept new transactions
with st.form("Add Block Form"):
    sender = st.text_input("Sender")
    receiver = st.text_input("Receiver")
    amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
    submitted = st.form_submit_button("Add Block")
    if submitted:
        new_record = Record(sender, receiver, amount)
        prev_block_hash = pychain.chain[-1].hash_block()
        new_block = Block(record=new_record, creator_id=42, prev_hash=prev_block_hash)
        pychain.add_block(new_block)
        st.success("Block added to the chain successfully!")

# Button to validate the entire blockchain
if st.button("Validate Chain"):
    if pychain.is_valid():
        st.success("The blockchain is valid.")
    else:
        st.error("The blockchain is not valid.")

# Display details of each block in the blockchain
st.header("Complete PyChain Ledger")
for idx, block in enumerate(pychain.chain):
    block_info = f"""
    Block: {idx}
    Sender: {block.record.sender}
    Receiver: {block.record.receiver}
    Amount: {block.record.amount}
    Timestamp: {block.record.timestamp}
    Hash: {block.hash_block()}
    Previous Hash: {block.prev_hash}
    """
    st.text_area(f"Block {idx} Details", value=block_info, height=250)
