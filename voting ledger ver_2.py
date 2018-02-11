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
# creation of the genesis block
import collections
chain=[]
state = {u'George':1000, u'Anne':0, u'Bob':0,u'Carla':0}
Gen_ballot = {u'George':100, u'Anne':100, u'Bob':100,u'Carla':100}  # Define the initial ballot 
Gen_Reputation ={u'George':1, u'Anne':0, u'Bob':0,u'Carla':0}
Gen_AgeBlock = {u'George':1, u'Anne':0, u'Bob':0,u'Carla':0}

genesisBlockTxns = []
genesisVoting =[]

genesisBlockHeader ={u'blockNumber':0, u'parentHash':None, u'timestamp':None, u'Mined by':'George', u'Next Miner':'George',u'Version':"beta"}

genesisBlockContents = {u'txnCount':0,u'txns':genesisBlockTxns, u'Ledger':state, u'Voting':genesisVoting,u'Ballot':Gen_ballot, u'Last mined block':Gen_AgeBlock,u'count blocks mined':Gen_Reputation}

genesisHash = hashMe( genesisBlockContents )

genesisBlock = {u'blockheader': genesisBlockHeader, u'hash':genesisHash,u'contents':genesisBlockContents}

genesisBlockStr = json.dumps(genesisBlock, sort_keys =True)

chain = [collections.OrderedDict(sorted(genesisBlock.items()))]


##-------------------------------------------------------------------
# create random voting transactions to influence the choice of the miner
#Improvement: add signature to the transaction + ID + time stamp

def makeVote():
    import random
    from datetime import datetime
    random.seed(datetime.now()) # optional random function for generate new seed (for demonstration purpose)
    vote ={}
    # This will create valid voting transactions. 
    # the random number is the % of the voting token in the ledger that participant send to the previous miner.
    # the previous miner may not vote.
    Block = len(chain)-1
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    ballot =chain[Block] [u'contents'] [u'Ballot']
    for key in ballot :
        if key ==miner:
            vote[key]=0

        else:
            vtktoken    = random.randint(1,100)
            vote[key]=round(-(vtktoken /100) *ballot[key],2)
    vote[miner]+=-sum(vote.values())
    return vote

    
# By construction, this will always return transactions that respect the conservation of tokens.
    # However, note that we have not done anything to check whether these overdraft an account

# vtnBuffer = [makeVote()]
# print(vtnBuffer)
#print(sum(vote.values()))
##---------------------------------------------------------------------
# Check of the validity of the Vote
# Improvement:
    #  1) The check of the signature of the transaction would be integrated here 
    #  2) There is no control of the traceability of the token (no merkel root algo)
def isValidVtn(vtn,ballot):
    # Assume that the transaction is a dictionary keyed by account names

    # Check that the sum of the deposits (voting token received by previous miner) and withdrawals (voting token send by candidate miner) is 0
    if round(sum(vtn.values()),2)<0:
        print('sum vtn value =',sum(vtn.values())," is not = 0 -> vote validation error #1 (value <0)")
        return False
    if round(sum(vtn.values()),2)>0:
        print('sum vtn value =',sum(vtn.values())," is not = 0 -> vote validation error #2 (value >0)")
        return False    
    # Check that the transaction does not cause an overdraft (is used to ensure that George is not cheating (produced energy > its capability) and will be used for voting token)
    for key in vtn.keys():
        if key in ballot.keys(): 
            acctBallot = ballot[key]
        else:
            acctBallot = 0
        if round(acctBallot + vtn[key],5) < 0:
            print("overdraft voting capability of",key,"by", acctBallot + vtn[key],"vote validation error #3")
            return False
    return True
# remove '#' to test this validity check
#ballot = {u'George':100,u'Anne':100,'Bob':100, u'Carla':100}

     # Basic transaction- this works great!
#print(isValidVtn({u'George': -100, u'Anne': 40, u'Bob':25, u'Carla':35},ballot)) 
    # But we can't create or destroy tokens!
#print(isValidTxn({u'George': -120, u'Anne': 40, u'Bob':25, u'Carla':35},ballot))  
#print(isValidTxn({u'George': -100, u'Anne': 75, u'Bob':5, u'Carla':2},ballot))
    # We also can't overdraft our account.
#print(isValidTxn({u'George':- 150, u'Anne': 100, u'Bob':20, u'Carla':30},ballot))
    # Creating new users is valid
#print(isValidVtn({u'George': -6, u'Guillaume': 6},ballot))  
##---------------------------------------------------------------------
# miner selection (see paper PSCC2018)
# This is a 3 steps process.
    # Step 1 = determine the wealth of each candidate miner
    # Step 2 = randomize
    # Step 3 = select the winner
#---------------------------------------------------------------------
# Step 1
# Note: for the sake of training, ballot, last mined block, and sum of mined block are integrate in the block

# Step 1.1 : gathering and validate voting token
def Candidate():
    ActualBlock = len(chain)-1
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    ballot =chain[ActualBlock] [u'contents'] [u'Ballot']
    Candidate={}
    newvtn=makeVote()
    vtnList = []
    validvtn =isValidVtn(newvtn,ballot)# This will return False if txn is invalid
    if validvtn:           # If we got a valid vote, not 'False'
        vtnList.append(newvtn)
        #print (vtnList)
    else:
        print("ignored transaction")
        sys.stdout.flush() # This was an invalid transaction; ignore it and move on

    Candidate=vtnList[0] #needed to transform a list (is not a dict)
    return Candidate
# Step 1.2.1 : taking the amount of voting token (and excluding the actual miner from the list)
def CandidateVote(Candidate):
    ActualBlock = len(chain)-1
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    ballot =chain[ActualBlock] [u'contents'] [u'Ballot']
    CandVote ={}
    for key in Candidate :
        if key ==miner:
            CandVote[key]=0
        else:
            CandVote[key]=-(Candidate[key])
    return CandVote
#Step 1.2.2 : multipying vote by alpha
def Candidate_E(CandVote):
    alpha = .6
    E={}
    for key in CandVote:
        E[key] =CandVote[key]*alpha
    return E
# Step 1.3 : Determine Age of last block mined by candidates
def CandidateAgeBlock(Candidate):
    beta = .8
    CandAge={}
    ActualBlock = len(chain)-1
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    ExAgeBlock = (chain[ActualBlock] [u'contents'] [u'Last mined block'])
    for key in Candidate:
        if key ==miner:
            CandAge[key]=0
        else:
            CandAge[key]=(ActualBlock -ExAgeBlock[key]+1)*beta
    return CandAge
# Step 1.4 : Determine Reputation of candidates
def CandidateReputation(Candidate):
    gamma =0.3
    CandReput ={}
    ActualBlock = len(chain)-1
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    ballot =chain[ActualBlock] [u'contents'] [u'Ballot']
    ExCountBlock = (chain[ActualBlock] [u'contents'] [u'count blocks mined'])
    for key in Candidate:
        if key ==miner:
            CandReput[key]=0  
        else:
            CandReput[key]=ExCountBlock[key]*gamma
    return CandReput 
# step 1.6: computing Wealth for each participant
def CandidateWealth(Candidate, Candidate_Vote, Candidate_Age,Candidate_Reput):
    CandWealth ={}
    ActualBlock = len(chain)-1
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    ballot =chain[ActualBlock] [u'contents'] [u'Ballot'] 
    for key in Candidate:
        if key ==miner:
            CandWealth[key]=0  
        else:
            CandWealth[key]=Candidate_Vote[key]+Candidate_Age[key]+Candidate_Reput[key]
    return CandWealth
# Step 2: generate random
# Improvement To create random number secret (pip install django-secrets) is prefered as random function
def CandidateUk(Candidate):
    import random
    CandUk={}
    from datetime import datetime
    random.seed(datetime.now()) # optional random function for generate new seed (for demonstration purpose)
    for key in Candidate:
        CandUk[key] =random.random()
    return(CandUk)
# Step 3: determine winner for next block
def Winner(Candidate, Candidate_Wealth, Candidate_Uk):
    ActualBlock = len(chain)-1
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    CandScore={}
    for key in Candidate:
        if key==miner:
            CandScore[key]=0
        else:
            CandScore[key]=Candidate_Wealth[key]/Candidate_Uk[key]
    v=list(CandScore.values())
    k=list(CandScore.keys())
    Winner = k[v.index(max(v))]
    return Winner   
##---------------------------------------------------------------------
# Settlement of the voting process
# There are 3 steps
#   step 1: updating the ballot
#   step 2: updating age of block
#   step 3: updating reputation
# All the voting token are send to the winner by updating the ballot

#Step 1: Updating Ballot
def updateBallot(Candidate,Winner):
# Returns: Updated ballotbox, 
    # NOTE: This does not not validate the transaction- just updates the ballot!
    ActualBlock = len(chain)-1
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    ballot =chain[ActualBlock] [u'contents'] [u'Ballot']
    ballot = ballot.copy() # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
    TotalBet =Candidate[miner]
    for key in Candidate:
        if key ==Winner:
            ballot[key]+= TotalBet+Candidate[key]
        elif key == miner:
            ballot[key]=ballot[key]
        else:
            ballot[key] += Candidate[key]
    return ballot
    
#Step 2: Updating Age of block for the winner    
def updateAgeblock(Candidate, Winner):
    ActualBlock = len(chain)-1
    AgeBlock={}
    miner = chain[-1] [u'blockheader'] [ u'Next Miner']
    ExAgeBlock = (chain[ActualBlock] [u'contents'] [u'Last mined block'])
    for key in Candidate:
        if key ==Winner:
            AgeBlock[key]= len(chain)+1
        else:
            AgeBlock[key] =ExAgeBlock[key]
    return AgeBlock
#Step 3: Updating reputation for the winner 
def updateReputation(Candidate, Winner):
    ActualBlock = len(chain)-1
    Reputation={}
    ExCountBlock = (chain[ActualBlock] [u'contents'] [u'count blocks mined'])
    for key in Candidate:
        if key ==Winner:
            Reputation[key]= ExCountBlock[key]+1
        else:
             Reputation[key]= ExCountBlock[key]
    return Reputation    

def makeBlock(Candidate, vote,Winner, ballot, Reputation, Age):
    import collections
    parentBlock = chain[-1]
    parentHash  = parentBlock[u'hash']
    #previousBlockNumber = len(chain) -2
    blockNumber = len(chain)
    mined = chain[-1] [u'blockheader'] [u'Next Miner']

    BlockHeader ={u'blockNumber':blockNumber, u'parentHash':parentHash, u'timestamp':None, u'Mined by':mined, u'Next Miner':Winner,u'Version':"beta"}
    
    BlockContents = {u'txnCount':0,u'txns':genesisBlockTxns, u'Ledger':state, u'Voting':vote,u'Ballot':ballot, u'Last mined block':Age,u'count blocks mined':Reputation}
    
    blockHash = hashMe( BlockContents )
    block = {u'blockheader': BlockHeader, u'hash':blockHash,u'contents':BlockContents}
    return collections.OrderedDict(sorted(block.items()))
def full_Voting_Process():
    Proven_candidate=Candidate()
    #print(Proven_candidate)
    CandVote =CandidateVote(Proven_candidate)
    #print(CandVote)
    Cand_E = Candidate_E(CandVote)
    CandAgeBlock = CandidateAgeBlock(Proven_candidate)
    #print (CandAgeBlock)
    CandReput = CandidateReputation(Proven_candidate)
    #print (CandReput)
    CandWealth=CandidateWealth(Proven_candidate,Cand_E,CandAgeBlock,CandReput)
    #print (CandWealth)
    CandUk =CandidateUk(Proven_candidate)
    #print (CandUk)
    New_Miner =Winner(Proven_candidate,CandWealth,CandUk)
    #print(New_Miner)
    New_Ballot = updateBallot(Proven_candidate,New_Miner)
    #print (New_Ballot)
    New_Age_Block = updateAgeblock(Proven_candidate,New_Miner)
    #print (New_Age_Block)
    New_Reputation = updateReputation(Proven_candidate,New_Miner)
    #print (New_Reputation)
    New_Block =makeBlock(Proven_candidate,CandVote,New_Miner,New_Ballot,New_Reputation,New_Age_Block)
    #print (New_Block)
    return New_Block
a=1000 # for testing = # of simulation of the voting process

for i in range(a):
    voteDemo=full_Voting_Process()
    chain.append(voteDemo)
#Report to analyse the voting process
x=0
for x in range(1,a+1):
    Draft_Report={}
    Ordered_Report={}
    import collections
    import csv
    csvfile ="D:\Documents\PHD\Bitcoin\Prg Py Hawkcoin\extract_csv.csv"
    Block_number=chain[x] [u'blockheader'][u'blockNumber']
    Ballot_Anne=chain[x][u'contents'] [u'Ballot'][u'Anne']
    Ballot_Bob=chain[x][u'contents'] [u'Ballot'][u'Bob']
    Ballot_Carla=chain[x][u'contents'] [u'Ballot'][u'Carla']
    Ballot_George=chain[x][u'contents'] [u'Ballot'][u'George']
    Vote_Anne=chain[x][u'contents'] [u'Voting'][u'Anne']
    Vote_Bob=chain[x][u'contents'] [u'Voting'][u'Bob']
    Vote_Carla=chain[x][u'contents'] [u'Voting'][u'Carla']
    Vote_George=chain[x][u'contents'] [u'Voting'][u'George']    
    Win=chain[x] [u'blockheader'][u'Next Miner']
    Mine =chain[x] [u'blockheader'][u'Mined by']
    Draft_Report = {'#':Block_number,'Ballot Anne':Ballot_Anne,'Ballot Bob':Ballot_Bob,'Ballot Carla':Ballot_Carla,'Ballot George':Ballot_George,'Voting Anne':Vote_Anne,'Voting Bob':Vote_Bob,'Voting Carla':Vote_Carla,'Voting George':Vote_George,'Winner':Win, 'Mined By':Mine}
    Ordered_Report=collections.OrderedDict(sorted(Draft_Report.items()))

    with open(csvfile,'a') as f: 
        w = csv.DictWriter(f, Ordered_Report.keys())
        w.writeheader()
        w.writerow(Ordered_Report)


