import os
from hedera import (
	Hbar,
	PrivateKey,
	AccountCreateTransaction,
	Client
)


client = Client.for_testnet()
client.setOperator('0.0.6886802','12de03c83b7eb630c082ccf1a0c58d671b1c5aed4448b1e71ad931e964a4ab20')

def create_hedera_account():
	new_Private_key = PrivateKey.generate()
	new_Public_key = new_Private_key.getPublicKey()



	transaction = (
		AccountCreateTransaction()
			.setKey(new_Public_key)
			.execte(client)
		)



	receipt = transaction.getRecipt(client)
	account_id = receipt.account_id

	return str(receipt)

create_hedera_account()
print()