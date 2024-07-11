import json
import asyncio
import time
from threading import Thread
from web3 import Web3

class Contract:
    def __init__(self, provider: str):
        self.w3 = Web3(Web3.HTTPProvider(provider))
        self.contract_address = Web3.to_checksum_address('0x5fbdb2315678afecb367f032d93f642f64180aa3')
        with open('MShop.json') as fp:
            contract_abi = json.loads(fp.read())
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=contract_abi)
    
    def buyTockens(self, amount: int, sender_address: str, private_key: str):
        nonce = self.w3.eth.get_transaction_count(sender_address)

        transaction = self.contract.functions.buy().build_transaction({
        'nonce': nonce,
        'value': self.w3.to_wei(amount, 'ether'),
        'gas': 30000000,
        'gasPrice': self.w3.to_wei('50', 'gwei'),
        })

        signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key)  
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def printBalances(self, sender_address: str):
        token_balance = self.contract.functions.myTokenBalance().call({'from': sender_address})
        print()
        print(f'Баланс токенов: {token_balance}')
        print()
        sender_balance = self.w3.eth.get_balance(sender_address)
        print(f'Баланс эфиров: {self.w3.from_wei(sender_balance, "ether")} ETH')
        print()
    
    def transactTokens(self, amount: int, recipient_address: str, private_key: str):
            #зачисление токенов
        nonce = self.w3.eth.get_transaction_count(recipient_address)
        transaction = self.contract.functions.recieveFromBlockchain(recipient_address, amount).build_transaction({
            'nonce': nonce,
            'gas': 30000000,
            'gasPrice': self.w3.to_wei('50', 'gwei'),
        })
        signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

            #продажа токенов
        nonce = self.w3.eth.get_transaction_count(recipient_address)
        transaction = self.contract.functions.sell(amount).build_transaction({
            'nonce': nonce,
            'gas': 30000000,
            'gasPrice': self.w3.to_wei('50', 'gwei'),
        })
        signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)






    #контракты 
firstContract = Contract('http://127.0.0.1:8545')
secondContract = Contract('http://127.0.0.1:8546')
thirdContract = Contract('http://127.0.0.1:8547')   

def handle_event(event):
    print(f"Событие: {event.event}")
    print(f"Данные: {event.args}")
    event_amount = event.args['_amount']
    event_chain_id = event.args['_chainId']
    event_address = event.args['_to']

    if event_chain_id == 1:
        firstContract.transactTokens(event_amount, event_address, '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d')
        firstContract.printBalances(event_address)
    elif event_chain_id == 2:
        secondContract.transactTokens(event_amount, event_address, '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d')
        secondContract.printBalances(event_address)
    elif event_chain_id == 3:
        thirdContract.transactTokens(event_amount, event_address, '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d')
        thirdContract.printBalances(event_address)



def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)

def main():
        #события
    event_filter = firstContract.contract.events.OtherBlockchainTransfer.create_filter(fromBlock='latest')
    worker = Thread(target=log_loop, args=(event_filter, 2), daemon=True)
    worker.start()

    event_filter_2 = secondContract.contract.events.OtherBlockchainTransfer.create_filter(fromBlock='latest')
    worker_2 = Thread(target=log_loop, args=(event_filter_2, 2), daemon=True)
    worker_2.start()

    event_filter_3 = thirdContract.contract.events.OtherBlockchainTransfer.create_filter(fromBlock='latest')
    worker_3 = Thread(target=log_loop, args=(event_filter_3, 2), daemon=True)
    worker_3.start()

        #пополняем баланс на контрактах 
    sender_address = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'
    private_key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    firstContract.buyTockens(100, sender_address, private_key)
    secondContract.buyTockens(100, sender_address, private_key)
    thirdContract.buyTockens(100, sender_address, private_key)

        #чтобы программа не останавливалась
    while True:
        time.sleep(1)

    
  

if __name__ == '__main__':
    main()



        

