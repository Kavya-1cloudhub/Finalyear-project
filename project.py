pip install PyCryptodome


from Crypto.PublicKey import RSA
from Crypto import Random
import hashlib as hasher
import datetime
import json
import getpass
import os
class Transaction:
    def __init__(self, drug_name, batch_number, manufacturing_date, expiration_date, supplier_puk, receiver_puk, amount=0, temperature=None, storage_info=None, timestamp=None):
        self.drug_name = drug_name
        self.batch_number = batch_number
        self.manufacturing_date = manufacturing_date
        self.expiration_date = expiration_date
        self.supplier_puk = supplier_puk
        self.receiver_puk = receiver_puk
        self.timestamp = timestamp or datetime.datetime.now()
        self.amount = amount
        self.temperature = temperature  # Temperature information
        self.storage_info = storage_info  # Storage information
class Block:
    def __init__(self, previous_hash):
        self.supply_data = []
        self.previous_hash = previous_hash
        self.timestamp = datetime.datetime.now()
        self.proof_of_work = 0
        self.hash = self.calculate_hash()
    def calculate_hash(self):
        sha = hasher.sha256()
        sha.update(str(self.timestamp).encode('utf-8') +
                   str(self.previous_hash).encode('utf-8') +
                   str(self.supply_data).encode('utf-8') +
                   str(self.proof_of_work).encode('utf-8'))
        return sha.hexdigest()
def create_genesis_block():
    return Block("0")
supply_blockchain = [create_genesis_block()]
manufacturers_list = []
other_users_list = []
utxo_dict = {}
def generate_pharmaceutical_company_keys(number):
    for _ in range(int(number)):
        key = RSA.generate(1024, Random.new().read)
        manufacturers_list.append(key.publickey().exportKey("PEM").decode('utf-8'))
        utxo_dict[key.publickey().exportKey("PEM").decode('utf-8')] = []  # Initialize UTXO for each manufacturer
    print('\nThe pharmaceutical company keys have been generated.')
def generate_other_keys(number):
    for _ in range(int(number)):
        key = RSA.generate(1024, Random.new().read)
        other_users_list.append(key.publickey().exportKey("PEM").decode('utf-8'))
        utxo_dict[key.publickey().exportKey("PEM").decode('utf-8')] = []  # Initialize UTXO for each stakeholder
    print('\nThe stakeholder keys have been generated.')
def view_blockchain():
    for count, block in enumerate(supply_blockchain):
        print('\nFor block #{}:'.format(count))
        for transaction in block.supply_data:
            print('Drug: {}, Batch: {}, Timestamp: {}, Temperature: {}, Storage Info: {}'.format(
                transaction.drug_name, transaction.batch_number,
                transaction.timestamp, transaction.temperature, transaction.storage_info))
        if count > 0 and str(supply_blockchain[count - 1].hash) == str(block.previous_hash):
            print('The hash values have been verified.')
        print('PoW: {}, Hash: {}'.format(block.proof_of_work, block.hash))
    print('------------------------------------------------------------------------------------------------------------------------')
    print('\n\n')
def make_transaction(drug_name, batch_number, receiver_index, amount, temperature=None, storage_info=None):
    if len(manufacturers_list) == 0 or len(other_users_list) == 0:
        print('Please generate keys for pharmaceutical companies and stakeholders first.')
        return
    supplier_index = 0  # Assuming the first pharmaceutical company is the supplier
    supplier_key = manufacturers_list[supplier_index]
    receiver_key = other_users_list[receiver_index]
    new_transaction = Transaction(drug_name, batch_number, datetime.datetime.now(),
                                  datetime.datetime.now() + datetime.timedelta(days=365),
                                  supplier_key, receiver_key,
                                  amount, temperature, storage_info)
    supply_blockchain[-1].supply_data.append(new_transaction)
    utxo_dict[supplier_key].append(new_transaction)
    utxo_dict[receiver_key].append(new_transaction)
    print('\nTransaction added successfully.')
def view_UTXO():
    print('\nUTXO Array:')
    for key, utxo_list in utxo_dict.items():
        print('Public Key: {}'.format(key))
        for utxo in utxo_list:
            print('    Drug: {}, Batch: {}, Amount: ${}, Temperature: {}, Storage Info: {}'.format(
                utxo.drug_name, utxo.batch_number, utxo.amount, utxo.temperature, utxo.storage_info))
        print('----------------------------------------')
def mine_block():
    # Placeholder for mining logic
    new_block = Block(supply_blockchain[-1].hash)
    supply_blockchain.append(new_block)
    print("\nBlock mined successfully.")
def verify_blockchain():
    for i in range(1, len(supply_blockchain)):
        current_block = supply_blockchain[i]
        previous_block = supply_blockchain[i - 1]
        # Verify the hash of the current block
        if current_block.calculate_hash() != current_block.hash:
            print("\nBlockchain verification failed: Hash mismatch in block #{}.".format(i))
            return
        # Verify that the previous hash matches the hash of the previous block
        if current_block.previous_hash != previous_block.hash:
            print("\nBlockchain verification failed: Previous hash mismatch in block #{}.".format(i))
            return
    print("\nBlockchain verified successfully.")
def track_item(batch_number):
    not_found_flag = True
    for block in supply_blockchain[1:]:
        for transaction in block.supply_data:
            if batch_number == transaction.batch_number:
                if not_found_flag:
                    print('\nThe drug (Batch #{}) has been found, and the tracking details are: '.format(batch_number))
                    not_found_flag = False
                supplier_found = False
                receiver_found = False
                for index, supplier_key in enumerate(manufacturers_list):
                    if transaction.supplier_puk == supplier_key:
                        supplier_found = True
                        break
                for index, receiver_key in enumerate(other_users_list):
                    if transaction.receiver_puk == receiver_key:
                        receiver_found = True
                        break
                print('Supplier: {}, Receiver: {}, Timestamp: {}'.format(
                    'Pharmaceutical Company #{}'.format(index + 1) if supplier_found else 'Stakeholder #{}'.format(
                        index + 1),
                    'Pharmaceutical Company #{}'.format(index + 1) if receiver_found else 'Stakeholder #{}'.format(
                        index + 1),
                    transaction.timestamp))
    if not_found_flag:
        print('\nThe drug batch number was not found in the blockchain.')
def view_transaction_history():
    print('\nTransaction History:')
    for index, block in enumerate(supply_blockchain[1:]):
        for transaction in block.supply_data:
            print('{}. Drug: {}, Batch: {}, Amount: ${}, Sender: {}, Receiver: {}, Timestamp: {}'.format(
                index + 1, transaction.drug_name, transaction.batch_number, transaction.amount,
                transaction.supplier_puk, transaction.receiver_puk, transaction.timestamp))
def transfer_ownership(batch_number, current_owner_index, new_owner_index):
    for block in supply_blockchain[1:]:
        for transaction in block.supply_data:
            if batch_number == transaction.batch_number:
                current_owner_key = manufacturers_list[current_owner_index] if current_owner_index == 0 else other_users_list[current_owner_index]
                new_owner_key = manufacturers_list[new_owner_index] if new_owner_index == 0 else other_users_list[new_owner_index]
                if transaction.receiver_puk == current_owner_key:
                    transaction.receiver_puk = new_owner_key
                    print('\nOwnership transferred successfully.')
                    return
    print('\nThe drug batch number was not found in the blockchain.')
def view_stakeholder_balance(stakeholder_index):
    print('\nStakeholder #{} Balance:'.format(stakeholder_index + 1))
    stakeholder_key = other_users_list[stakeholder_index]
    if stakeholder_key in utxo_dict:
        balance = sum(utxo.amount for utxo in utxo_dict[stakeholder_key])
        print('Total Balance: ${:.2f}'.format(balance))
    else:
        print('Total Balance: $0.00 (No UTXO available)')
def view_blockchain_statistics():
    print('\nBlockchain Statistics:')
    print('Number of Blocks:', len(supply_blockchain) - 1)
    print('Number of Transactions:', sum(len(block.supply_data) for block in supply_blockchain[1:]))
    total_amount = sum(transaction.amount for block in supply_blockchain[1:] for transaction in block.supply_data)
    print('Total Amount Transferred: ${:.2f}'.format(total_amount))
class ExpiryDateCheckContract:
    def __init__(self, expiry_date_threshold):
        self.expiry_date_threshold = expiry_date_threshold
    def execute(self, transaction):
        # Check if the drug is not expired based on the provided threshold
        current_date = datetime.datetime.now()
        expiry_date = transaction.manufacturing_date + datetime.timedelta(days=365)
        condition = expiry_date > current_date > self.expiry_date_threshold
        return condition
from json import JSONEncoder
class DateTimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, Transaction):
            return o._dict_
        return super().default(o)
class CrossBorderTransactionContract:
    def __init__(self, country_restrictions):
        self.country_restrictions = country_restrictions
    def execute(self, transaction):
        # Check if the transaction involves cross-border movement
        supplier_country = get_country_from_key(transaction.supplier_puk)
        receiver_country = get_country_from_key(transaction.receiver_puk)
        if supplier_country in self.country_restrictions and receiver_country in self.country_restrictions:
            # Both supplier and receiver are subject to cross-border restrictions
            return False
        else:
            # Either supplier or receiver is not subject to cross-border restrictions
            return True
def get_country_from_key(public_key):
    # This is a placeholder function to extract country information from the public key.
    # In a real-world scenario, you might have a more sophisticated method to determine the country.
    return "CountryX"
# Generating keys for pharmaceutical companies and stakeholders
number_pharmaceutical_companies = int(input('\nEnter the number of pharmaceutical companies: '))
generate_pharmaceutical_company_keys(number_pharmaceutical_companies)
number_other_users = int(input('\nEnter the number of stakeholders: '))
generate_other_keys(number_other_users)
# Inserting a genesis block into the blockchain
supply_blockchain.append(create_genesis_block())
print('\n\nWelcome to the drug supply blockchain.')
# Menu-driven program for the supply blockchain
while True:
    print('\nThe following options are available to the user:')
    print('1. View the blockchain.')
    print('2. Enter a drug transaction.')
    print('3. View the UTXO array.')
    print('4. Mine a block.')
    print('5. Verify the blockchain.')
    print('6. Generate RSA keys.')
    print('7. Track a drug batch.')
    print('8. View transaction history.')
    print('9. Transfer ownership.')
    print('10. View stakeholder balance.')
    print('11. View blockchain statistics.')
    print('12. Interactive Smart Contract.')
    print('13. User Authentication and Authorization.')
    print('14. Exit.')
    
    choice = int(input('Enter your choice: '))
    
    if choice == 1:
        view_blockchain()
    elif choice == 2:
        drug_name = input('Enter the drug name: ')
        batch_number = input('Enter the batch number: ')
        receiver_index = int(input('Enter the stakeholder index (starting from 0): '))
        amount = float(input('Enter the transaction amount: '))
        temperature = float(input('Enter the temperature: '))
        storage_info = input('Enter the storage information: ')
        make_transaction(drug_name, batch_number, receiver_index, amount, temperature, storage_info)
    elif choice == 3:
        view_UTXO()
    elif choice == 4:
        mine_block()
    elif choice == 5:
        verify_blockchain()
    elif choice == 6:
        number_pharmaceutical_companies = int(input('Enter the number of pharmaceutical companies: '))
        generate_pharmaceutical_company_keys(number_pharmaceutical_companies)
        number_other_users = int(input('Enter the number of stakeholders: '))
        generate_other_keys(number_other_users)
    elif choice == 7:
        batch_number = input('Enter the drug batch number: ')
        track_item(batch_number)
    elif choice == 8:
        view_transaction_history()
    elif choice == 9:
        batch_number = input('Enter the drug batch number: ')
        current_owner_index = int(input('Enter the current owner index (starting from 0): '))
        new_owner_index = int(input('Enter the new owner index (starting from 0): '))
        transfer_ownership(batch_number, current_owner_index, new_owner_index)
    elif choice == 10:
        stakeholder_index = int(input('Enter the stakeholder index: '))
        view_stakeholder_balance(stakeholder_index)
    elif choice == 11:
        view_blockchain_statistics()
    elif choice == 12:
      expiry_date_threshold = datetime.datetime.now()  # Set a threshold for demo purposes
      expiry_contract = ExpiryDateCheckContract(expiry_date_threshold)  # Create an instance of the contract
      cross_border_contract = CrossBorderTransactionContract(["CountryA", "CountryB"])  # Specify countries with cross-border restrictions
      drug_manufacturing_date = datetime.datetime.strptime(input('Enter the manufacturing date (YYYY-MM-DD): '), '%Y-%m-%d')
      drug_transaction = Transaction('DemoDrug', 'DemoBatch', drug_manufacturing_date, datetime.datetime.now(),
                                manufacturers_list[0], other_users_list[0])
      expiry_contract_result = expiry_contract.execute(drug_transaction)  # Use the correct contract instance
      cross_border_contract_result = cross_border_contract.execute(drug_transaction)
      print('Expiry Contract Execution Result:', 'Contract condition satisfied.' if expiry_contract_result else 'Contract failed.')
      print('Cross Border Contract Execution Result:', 'Contract condition satisfied.' if cross_border_contract_result else 'Contract failed.')
    elif choice == 13:
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")
        # Simplified check for authentication
        if username == "admin" and password == "password":
            print("Authentication successful. You have access to enhanced features.")
            # Simplified check for authorization
            if username == "admin":
                # Additional functionality for authorized user goes here
                print("You have admin privileges.")
            else:
                print("You do not have admin privileges.")
        else:
            print("Authentication failed. Access denied.")
    elif choice == 14:
        print('Goodbye!')
        break
    else:
        print('This is an invalid option.')
