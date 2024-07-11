import json
import asyncio
import time
from threading import Thread
from web3 import Web3

# подключение к контракту в первом блокчейне
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  
contract_address = Web3.to_checksum_address('0x5fbdb2315678afecb367f032d93f642f64180aa3')

with open('MShop.json') as fp:
    contract_abi = json.loads(fp.read())

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# подлкючение к контракту во втором блокчейне 
w3_2 = Web3(Web3.HTTPProvider('http://127.0.0.1:8546'))
contract_2 = w3_2.eth.contract(address=contract_address, abi=contract_abi)

# подлкючение к контракту в третьем блокчейне 
w3_3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8547'))
contract_3 = w3_3.eth.contract(address=contract_address, abi=contract_abi)

#################################################

event_amount = None
event_chain_id = None
event_address = None

def handle_event(event):
    global event_amount, event_chain_id, event_address
    print()
    print(f"Событие: {event.event}")
    print(f"Данные: {event.args}")
    print()
    event_amount = event.args['_amount']
    event_chain_id = event.args['_chainId']
    event_address = event.args['_to']

def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)

def main():
    #обработка событий о переводе токенов на другой блокчейн
    event_filter = contract.events.OtherBlockchainTransfer.create_filter(fromBlock='latest')
    worker = Thread(target=log_loop, args=(event_filter, 2), daemon=True)
    worker.start()

    # Адреса и приватный ключ
    sender_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
    private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'
    recipient_address = Web3.to_checksum_address('0x5fbdb2315678afecb367f032d93f642f64180aa3')

    # Функция для вывода баланса
    def print_balances():
        sender_balance = w3.eth.get_balance(sender_address)
        recipient_balance = w3.eth.get_balance(recipient_address)
        print(f'Баланс отправителя: {w3.from_wei(sender_balance, "ether")} ETH')
        print(f'Баланс получателя: {w3.from_wei(recipient_balance, "ether")} ETH')

    #покупка токенов в первом блокчейне
    nonce = w3.eth.get_transaction_count(sender_address)

    transaction = contract.functions.buy().build_transaction({
        'nonce': nonce,
        'value': w3.to_wei(5, 'ether'),
        'gas': 30000000,
        'gasPrice': w3.to_wei('50', 'gwei'),
    })

    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    #Вывод балансов до транзакции
    print('Баланс до транзакции:')
    print_balances()

    # Отправка транзакции  
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    # Ожидание подтверждения транзакции tx_receipt =
    w3.eth.wait_for_transaction_receipt(tx_hash)
    time.sleep(4)
 
    # Вывод балансов после транзакции
    print()
    print('Баланс после транзакции:')
    print_balances()
    print()
    print()

###############################################
    # перевод токенов на второй блокчейн 
    nonce = w3.eth.get_transaction_count(sender_address)

    transaction = contract.functions.transferToBlockchain('0x70997970C51812dc3A010C7d01b50e0d17dc79C8', 4000000000000000000, 2).build_transaction({
        'nonce': nonce,
        'gas': 30000000,
        'gasPrice': w3.to_wei('50', 'gwei'),
    })

    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)
    # Отправка транзакции
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    # Ожидание подтверждения транзакции
    w3.eth.wait_for_transaction_receipt(tx_hash)
    time.sleep(4)

    token_balance = contract.functions.myTokenBalance().call({'from': sender_address})
    print(f'Баланс токенов: {token_balance}')
    print()

##########################################
    # на балансах второго и третьего блокчейна нет денег, поэтому нужно пополнить, чтобы потом продать токены
        # Адреса и приватный ключ
    sa = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'
    pk = '0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a'
    akk = Web3.to_checksum_address('0x5fbdb2315678afecb367f032d93f642f64180aa3')

    amount_in_ether = 10
    nonce = w3_2.eth.get_transaction_count(sa)
    transaction = {
        'nonce': nonce,
        'to': akk,
        'value': w3_2.to_wei(amount_in_ether, 'ether'),
        'gas': 30000000,
        'gasPrice': w3_2.to_wei('50', 'gwei'),
    }
    signed_transaction = w3_2.eth.account.sign_transaction(transaction, pk)

    tx_hash = w3_2.eth.send_raw_transaction(signed_transaction.rawTransaction)
    w3_2.eth.wait_for_transaction_receipt(tx_hash)
    print('баланс второго контракта пополнен')
    print()

    # пополнение третьего
    nonce = w3_3.eth.get_transaction_count(sa)
    transaction = {
        'nonce': nonce,
        'to': akk,
        'value': w3_3.to_wei(amount_in_ether, 'ether'),
        'gas': 30000000,
        'gasPrice': w3_3.to_wei('50', 'gwei'),
    }
    signed_transaction = w3_3.eth.account.sign_transaction(transaction, pk)

    tx_hash = w3_3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    w3_3.eth.wait_for_transaction_receipt(tx_hash)
    print('баланс третьего контракта пополнен')
    print()


##########################################
    # получение токенов 

    if event_chain_id == 2:
        nonce = w3_2.eth.get_transaction_count(event_address)

        transaction = contract_2.functions.recieveFromBlockchain(event_address, event_amount).build_transaction({
            'nonce': nonce,
            'gas': 30000000,
            'gasPrice': w3_2.to_wei('50', 'gwei'),
        })

        signed_transaction = w3_2.eth.account.sign_transaction(transaction, private_key)
        # Отправка транзакции
        tx_hash = w3_2.eth.send_raw_transaction(signed_transaction.rawTransaction)
        # Ожидание подтверждения транзакции
        w3_2.eth.wait_for_transaction_receipt(tx_hash)
        print('токены зачислены')

        token_balance = contract_2.functions.myTokenBalance().call({'from': event_address})
        print(f'Баланс токенов 2 блокчейн: {token_balance}')
        print()
    elif event_chain_id == 3:
        nonce = w3_3.eth.get_transaction_count(event_address)

        transaction = contract_3.functions.recieveFromBlockchain(event_address, event_amount).build_transaction({
            'nonce': nonce,
            'gas': 30000000,
            'gasPrice': w3_3.to_wei('50', 'gwei'),
        })

        signed_transaction = w3_3.eth.account.sign_transaction(transaction, private_key)
        # Отправка транзакции
        tx_hash = w3_3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        # Ожидание подтверждения транзакции
        w3_3.eth.wait_for_transaction_receipt(tx_hash)
        print('токены зачислены')

        token_balance = contract_3.functions.myTokenBalance().call({'from': event_address})
        print(f'Баланс токенов 3 блокчейн: {token_balance}')
        print()

###########################################
    # продажа токенов 

    if event_chain_id == 2:
        nonce = w3_2.eth.get_transaction_count(event_address)

        transaction = contract_2.functions.sell(event_amount).build_transaction({
            'nonce': nonce,
            'gas': 30000000,
            'gasPrice': w3_2.to_wei('50', 'gwei'),
        })

        signed_transaction = w3_2.eth.account.sign_transaction(transaction, private_key)
        # Отправка транзакции
        tx_hash = w3_2.eth.send_raw_transaction(signed_transaction.rawTransaction)
        # Ожидание подтверждения транзакции
        w3_2.eth.wait_for_transaction_receipt(tx_hash)
        print('токены проданы')
        token_balance = contract_2.functions.myTokenBalance().call({'from': event_address})
        print(f'Баланс токенов 2 блокчейн: {token_balance}')
        print()

        final_balance = w3_2.eth.get_balance(event_address)
        print(f'Итоговый баланс: {w3_2.from_wei(final_balance, "ether")} ETH')
        print()
    elif event_chain_id == 3:
        nonce = w3_3.eth.get_transaction_count(event_address)

        transaction = contract_3.functions.sell(event_amount).build_transaction({
            'nonce': nonce,
            'gas': 30000000,
            'gasPrice': w3_3.to_wei('50', 'gwei'),
        })

        signed_transaction = w3_3.eth.account.sign_transaction(transaction, private_key)
        # Отправка транзакции
        tx_hash = w3_3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        # Ожидание подтверждения транзакции
        w3_3.eth.wait_for_transaction_receipt(tx_hash)
        print('токены проданы')
        token_balance = contract_3.functions.myTokenBalance().call({'from': event_address})
        print(f'Баланс токенов 3 блокчейн: {token_balance}')
        print()

        final_balance = w3_3.eth.get_balance(event_address)
        print(f'Итоговый баланс: {w3_3.from_wei(final_balance, "ether")} ETH')
        print()


if __name__ == '__main__':
    main()