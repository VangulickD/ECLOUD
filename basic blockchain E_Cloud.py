# blockchain based on http://ecomunsing.com/build-your-own-blockchain
# test peer to peer energy exchange type "E-Cloud" with 1 generator (george) and 3 customers (anne,bob,carla)
# shares for each customer are fixed (e.g. a=50%, b = 30%, c =20%)

# IMPORTANT NOTICE; (see note Improvement for further development)
    # 1)For the sake of simplicity, the transactions are not signed 
    # 2) This is a local blockchain. Transaction and block need to be broadcasted for a real case
    # 3) This blockchain is not time related/synchronised
    # 4) The voting system to determine which node is the miner is not yet implemented.

##-------------------------------------------------------------------
# Helper function to create Hash = block header
import hashlib, json, sys


def hashMe(msg=""):
    # For convenience, this is a helper function that wraps our hashing algorithm
    if type(msg)!=str:
        msg = json.dumps(msg,sort_keys=True)  # If we don't sort keys, we can't guarantee repeatability!
        
    if sys.version_info.major == 2:
        return unicode(hashlib.sha256(msg).hexdigest(),'utf-8')
    else:
        return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()
##-------------------------------------------------------------------
# create 30 random transactions to share energy produced by george
# Improvement: add signature to the transaction + ID + time stamp
import random
from datetime import datetime
random.seed(0)
#random.seed(datetime.now()) # optional random function for generate new seed (for demonstration purpose)
def makeTransaction(maxValue=10):
    # This will create valid transactions in the range of (1,maxValue)
    
    amount    = random.randint(1,maxValue)
    georgeProd = -amount
    anneReceive = round(0.5 * amount,2)
    bobReceive = round(0.3 * amount,2)
    carlaReceive = round(amount - anneReceive - bobReceive,2)

    # By construction, this will always return transactions that respect the conservation of tokens.
    # However, note that we have not done anything to check whether these overdraft an account
    return {u'George':georgeProd,u'Anne':anneReceive,u'Bob':bobReceive, u'Carla':carlaReceive}
    
txnBuffer = [makeTransaction() for i in range(30)]
##---------------------------------------------------------------------
# creation of the ledger (state) for each participant
def updateState(txn, state):
    # Inputs: txn, state: dictionaries keyed with account names, holding numeric values for transfer amount (txn) or account balance (state)
    # Returns: Updated state, with additional users added to state if necessary
    # NOTE: This does not not validate the transaction- just updates the state!
    
    # If the transaction is valid, then update the state
    state = state.copy() # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state
##---------------------------------------------------------------------
# Check of the validity of the transaction
# Improvement:
    #  1) The check of the signature of the transaction would be integrated here 
    #  2) There is no control of the traceability of the token (no merkel root algo)
def isValidTxn(txn,state):
    # Assume that the transaction is a dictionary keyed by account names

    # Check that the sum of the deposits (generated energy) and withdrawals (share to each customer) is 0
    if round(sum(txn.values()),2)<0:
        print('sum tx value =',sum(txn.values())," is not = 0 -> tx validation error #1 (value <0)")
        return False
    if round(sum(txn.values()),2)>0:
        print('sum tx value =',sum(txn.values())," is not = 0 -> tx validation error #2 (value >0)")
        return False    
    # Check that the transaction does not cause an overdraft (is used to ensure that George is not cheating (produced energy > its capability) and will be used for voting token)
    for key in txn.keys():
        if key in state.keys(): 
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            print("overdraft account of",key,"by", acctBalance + txn[key],"tx validation error #3")
            return False
    return True
        #---------------------------------------------------------------------
# remove '#' to test this validity check
#state = {u'George':100,u'Anne':100,'Bob':100, u'Carla':100}
#g=int(-100)
#a=int(0.5*g)
#b=int(0.3*g)
#c=(g-a-b)
     # Basic transaction- this works great!
#print(isValidTxn({u'George': g, u'Anne': a, u'Bob':b, u'Carla':c},state)) 
    # But we can't create or destroy tokens!
#print(isValidTxn({u'George': -g, u'Anne': a, u'Bob':b, u'Carla':c},state))  
#print(isValidTxn({u'George': g, u'Anne': -a, u'Bob':b, u'Carla':c},state))
    # We also can't overdraft our account.
#print(isValidTxn({u'George':- 150, u'Anne': 100, u'Bob':20, u'Carla':30},state))
    # Creating new users is valid
#print(isValidTxn({u'George': -6, u'Guillaume': 6},state))  
        #---------------------------------------------------------------------
##---------------------------------------------------------------------
# creation of the genesis block
state = {u'George':1000, u'Anne':0, u'Bob':0,u'Carla':0}  # Define the initial state (please note the the initial state for George can be interpretated as the maximum energy that George can produce during this simulation)
genesisBlockTxns = [state]
genesisBlockHeader ={u'blockNumber':0, u'parentHash':None, u'timestamp':None, u'Mined by':None, u'Version':"beta"}
genesisBlockContents = {u'txnCount':1,u'txns':genesisBlockTxns, u'Ledger':state}
genesisHash = hashMe( genesisBlockContents )
genesisBlock = {u'blockheader': genesisBlockHeader, u'hash':genesisHash,u'contents':genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

chain = [genesisBlock]
##---------------------------------------------------------------------
# Building the Blockchain: From Transactions to blocks
#Improvement
        # There is only one miner
        # This will be changed when introducing voting system
def makeBlock(txns,chain):
    parentBlock = chain[-1]
    parentHash  = parentBlock[u'hash']
    blockNumber = parentBlock[u'blockheader'][u'blockNumber'] + 1
    txnCount    = len(txns)
    blockheader ={u'blockNumber':blockNumber, u'parentHash':parentHash,u'timestamp':None, u'Mined by':None, u'Version':"beta"}
    blockContents = {u'txnCount':len(txns),u'txns':txns,u'Ledger':state}
    blockHash = hashMe( blockContents )
    block = {u'blockheader': blockheader, u'hash':blockHash,u'contents':blockContents}
    
    return block
blockSizeLimit = 5  # Arbitrary number of transactions per block- 
               #  this will be changed when introducing time synchronisation

while len(txnBuffer) > 0:
    bufferStartSize = len(txnBuffer)
    
    # Gather a set of valid transactions for inclusion
    txnList = []
    while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
        newTxn = txnBuffer.pop()
        validTxn = isValidTxn(newTxn,state) # This will return False if txn is invalid
        
        if validTxn:           # If we got a valid state, not 'False'
           txnList.append(newTxn)
           state = updateState(newTxn,state)
        else:
            print("ignored transaction")
            sys.stdout.flush()
            continue  # This was an invalid transaction; ignore it and move on
        
    # Make a block
    myBlock = makeBlock(txnList,chain)
    chain.append(myBlock) 
##---------------------------------------------------------------------
# Checking Chain Validity: be sure that the chain has not been corrupted
# To do that we need 2 helpers
        # helper 1: check that each block is still untouched
        # helper 2: check if the block is valid (see bellow for further details)
#---------------------------------------------------------------------
    # Helper 1
def checkBlockHash(block):
    # Raise an exception if the hash does not match the block contents
    expectedHash = hashMe( block['contents'] )
    if block['hash']!=expectedHash:
        raise Exception('Block Check error #1: Hash does not match contents of block %s'%
                        block['contents']['blockNumber'])
    return
    #---------------------------------------------------------------------
    # Helper 2
def checkBlockValidity(block,parent,state):    
    # We want to check the following conditions:
    # - Each of the transactions are valid updates to the system state
    # - Block hash is valid for the block contents
    # - Block number increments the parent block number by 1
    # - Accurately references the parent block's hash
    parentNumber = parent['blockheader']['blockNumber']
    parentHash   = parent['hash']
    blockNumber  = block['blockheader']['blockNumber']
    
    # Check transaction validity; throw an error if an invalid transaction was found.
    for txn in block['contents']['txns']:
        if isValidTxn(txn,state):
            state = updateState(txn,state)
        else:
            raise Exception('Block Check error #2:Invalid transaction in block %s: %s'%(blockNumber,txn))

    checkBlockHash(block) # Check hash integrity; raises error if inaccurate

    if blockNumber!=(parentNumber+1):
        raise Exception('Block Check error #3: Parent block number does not match %s'%blockNumber, 'possible broken chain')

    if block['blockheader']['parentHash'] != parentHash:
        raise Exception('Block Check error #3: Parent hash not accurate at block %s'%blockNumber)
    return state
    #---------------------------------------------------------------------
    # Full chain validity check
def checkChain(chain):
    # Work through the chain from the genesis block (which gets special treatment), 
    #  checking that all transactions are internally valid,
    #    that the transactions do not cause an overdraft,
    #    and that the blocks are linked by their hashes.
    # This returns the state as a dictionary of accounts and balances,
    #   or returns False if an error was detected

    
    # Data input processing: Make sure that our chain is a list of dicts
    if type(chain)==str:
        try:
            chain = json.loads(chain)
            assert( type(chain)==list)
        except:  # This is a catch-all, admittedly crude
            return False
    elif type(chain)!=list:
        return False
    
    state = {}
    # Prime the pump by checking the genesis block
    # We want to check the following conditions:
    # - Each of the transactions are valid updates to the system state
    # - Block hash is valid for the block contents

    for txn in chain[0]['contents']['txns']:
        state = updateState(txn,state)
    checkBlockHash(chain[0])
    parent = chain[0]
    
    # Checking subsequent blocks: These additionally need to check
    #    - the reference to the parent block's hash
    #    - the validity of the block number
    for block in chain[1:]:
        state = checkBlockValidity(block,parent,state)
        parent = block
    print("The chain as been completely checked and is valid")
    return state

##---------------------------------------------------------------------
# final Result

Bl_lenght = len(chain)
E_Prod = state['George']
#print (state)
checkChain(chain)
print ("The blockchain is currently ",Bl_lenght,"blocks long")
print("So far, energy produced by George =", 1000-E_Prod," Kwh")
import copy
import csv

backup = copy.copy(chain)
csvfile = "D:\Documents\PHD\Bitcoin\Prg Py Hawkcoin\Hawk Coin\HawkLedger.csv"
#with open(csvfile, "w") as output:
#    writer = csv.writer(output, lineterminator='\n')
#    writer.writerows(backup)
#import pandas as pd

#(pd.DataFrame.from_dict(data=backup, orient='index').to_csv(csvfile, header=False))

print(chain)


