READ.ME
*******
List and explanation of the files:
----------------------------------
	basic blockchain E_Cloud.py
 		+ this is the basic blockchain to test the logic to build a complete chaine in Python.
		+ test peer to peer energy exchange type "E-Cloud" with 1 generator (george) and 3 customers (anne,bob,carla)
		+ shares for each customer are fixed (e.g. a=50%, b = 30%, c =20%)
	
	voting ledger ver_2.py
		+ separate BlockChain to test voting process based on paper PSCC (no integration of the transaction): 1000 blocks are created (see line 307)
		+ each agent is candidate for every steps
		+ initial balot 100 units / candidates
		+ initial rules : purely ramdomized based on ledger + no creation of new voting token
		+ a special dict is created to facilitate the analyse of the process. This dict is exported to a csv file
		+ /!\ create an empty extract_csv.csv
		+ /!\ need to change line 319 to indicate your path to this csv file

	analyse typical voting process.xlsx
		+ this file is an analyse of the voting process using voting ledger ver_2

	test scheduling task.py
		+ this is a working file to test different way to schedul task. (ie apscheduler)
		+ when it will be ready,it will be integrated in basic blockchain.py to generate block at given time period (= proxy of virtual meters ledger)

	generate private and publickey.py
		+ this is a working file to test differentway to sign transaction (txn) and to verify the signature
		+ when it will be ready, it will be integrated in basic blockchain.py to signed transaction (= proxy of cryptometers)

To do list (status: February 11Th 2018):
------------------------------
	1) create voting token : OK DONE
	2) create consensus model and decision about miner (see PSCC article): 
		2.1) get info from the voting ledger about reputation and age of last block : 
			OK DONE
		2.2) create standard rules to vote (e.g. George keep 20 % of the voting token when creating a kWh,find rules for anne, bob and carla) 
			OK DONE BUT DIFFERENT STRATEGIES NEED TO BE TESTED
		2.3) generate random number 'u' (/!\ use secrets libraty to generate secure random numbers for managing secrets): 
			To be Checked
		2.4) create specific txn "mining winner" + set rules to pay the miner (e.g. waiting 6 blocks to defreeze the voting token) + penality rules if miner failed
	3) (new point) Integrate transaction blockchain and voting blockchain
	4) create block on a synchronise manner (e.g. each 15 seconds as a proxy for 1/4h exchange ledger)
	5) for each transaction add Txn_Id and signature (mimic cryptometer)
	6) deploy solution on decentralized way
	


Explanation about block structure
---------------------------------

The blocks are built as a dictionaty in Python.
After the genesis block, each block has the same structure: 

	Blockheader = generalities about the block. 
		Please note that some fileds are already foreseen for further development:
			mined by: will be used with the voting system
			timestamp: to build the virtual meter ledger based on market period
			version: coud be integrated in block verification in the future
	Contents = # transaction in the bloc + ledger + details of transaction
		Please note that a second ledger and a second type of transaction will be implemented with the voting system

see example:
{'blockheader': 
	{'Version': 'beta',
 	'Mined by': None, 
	'blockNumber' : 2, 
	'parentHash': '1a7cb1a48dedc85d3b3768e7619620bf127e99bc30b6888b42c37497cac05f70', 
	'timestamp': None},
 	'hash': '92560a107026646014bf69295cd5bd6c337365b8f189f381f0214f4287e580a3', 
'contents': 
	{'txnCount': 5,
	'Ledger': {'Carla': 10.6, 'George': 947, 'Bob': 15.9, 'Anne': 26.5}, 
	'txns': 
		[{'Carla': 0.4, 'George': -2, 'Bob': 0.6, 'Anne': 1.0}, 
		{'Carla': 0.4, 'George': -2, 'Bob': 0.6, 'Anne': 1.0},
		{'Carla': 1.0, 'George': -5, 'Bob': 1.5, 'Anne': 2.5}, 
		{'Carla': 0.6, 'George': -3, 'Bob': 0.9, 'Anne': 1.5}, 
		{'Carla': 2.0, 'George': -10, 'Bob': 3.0, 'Anne': 5.0}]}},