# coding=utf-8

import numpy as np
import matplotlib.pyplot as mpl

class Riding():

    def __init__(self, number, name, candidates, parties, votes):
        self.number = number        
        self.name = name
        self.candidates = np.array(candidates)
        self.parties = np.array(parties)
        self.votes = votes
        
    def results(self):
        '''Prints the riding results by party'''

        for i in range(len(self.parties)):
            print '%s: %s\n' % (self.parties[i], self.votes[i])
    
    def party_result(self, party):
        '''Returns the number of votes for a particular party'''

        w = np.where(self.parties == party)[0]
        if len(w) == 0:
            return 0.0
        else:
            return self.votes[w]
        
################################################


def extract_electiondata():
    ele_results = '/Users/relliotmeyer/gitrepos/election2015AV/EventResults.txt'

    f = open(ele_results, 'r')
    str_data = f.readlines()
    split_data = []
    

    for line in str_data:
        split_data.append(line.split('\t'))

    spl_data = np.array(split_data[2:2034])

    ridingNumbers = spl_data[:,0] 

    unique_ridingNumbers = []
    for num in ridingNumbers:
        if num not in unique_ridingNumbers:
            unique_ridingNumbers.append(num)
    unique_ridingNumbers = np.array(unique_ridingNumbers)

    ridingNames = spl_data[:,1]
    resultType = spl_data[:,3]

    candidateNames = []
    for val in spl_data:
        candidateNames.append(val[7] + ' ' + val[6] + ' ' + val[5])
    candidateNames = np.array(candidateNames)

    candidateParty = spl_data[:,8]
    candidateVotes = spl_data[:,10]
    candidateVotes = candidateVotes.astype(float)
    
    riding_list = []
    
    for num in unique_ridingNumbers:
        ridingrows = np.where(ridingNumbers == num)[0]
        results = resultType[ridingrows]
        if 'validated' in results:
            ridingrows = ridingrows[np.where(results == 'validated')[0]]
        
        #candidates = candidateNames[ridingrows]
        #parties = candidateParty[ridingrows]
        #votes = candidateVotes[ridingrows]

        candidates = []
        parties = []
        votes = []

        for rid in ridingrows:
            candidates.append(candidateNames[rid])
            parties.append(candidateParty[rid])
            votes.append(candidateVotes[rid])
        
        riding_list.append(Riding(num, ridingNames[ridingrows[0]], candidates, parties, votes))

    return riding_list

def instant_runoff(votelist, verbose = False):

    #### 2nd choice preferences from Nanos final election poll ####

    ## Indexing: [Conservative, Liberals, NDP, Green, Bloc]
    con = np.array([0.00, 0.31, 0.12, 0.08, 0.02])
    lib = np.array([0.21, 0.00, 0.49, 0.11, 0.02])
    ndp = np.array([0.10, 0.55, 0.00, 0.17, 0.08])
    gre = np.array([0.10, 0.28, 0.43, 0.00, 0.04])
    blo = np.array([0.13, 0.16, 0.49, 0.07, 0.00])

    choices = np.array([con, lib, ndp, gre, blo])
    partylist = ['Conservative','Liberal', 'NDP-New Democratic Party', 'Green Party', 'Bloc Québécois']
    
    total_votes = np.sum(votelist)
    vote_fraction = votelist / total_votes

    n_iter = 0

    ind_n_nocandidates = np.where(votelist == 0.0)[0]
    n_nocand = len(ind_n_nocandidates)

    for i, val in enumerate(vote_fraction):
        if val >= 0.5:
            return [votelist, partylist[i], n_iter]
        else:
            winner = False
    
    if verbose == True:
        ind_sortedvotelist = np.argsort(votelist)
        fptp_winner = partylist[ind_sortedvotelist[-1]]
            
    party_bool = [1,1,1,1,1]
    
    while winner == False:
        if verbose == True:
            print "Overall vote list: " + str(votelist)
            
        ind_sortedvotelist = np.argsort(votelist)
        bottomparty = ind_sortedvotelist[n_iter]
        bottomvotes = votelist[bottomparty]
        bottom_dist = bottomvotes * choices[bottomparty]
        votelist += bottom_dist
        party_bool[bottomparty] = 0
        votelist *= party_bool

        vote_fraction = votelist / np.sum(votelist)

        if verbose == True:
            print "Sorted party index: " + str(ind_sortedvotelist)
            print "Bottom party index: " + str(bottomparty)
            print "Bottom party votes: " + str(bottomvotes)
            print "Bottom party redistribution: " + str(choices[bottomparty])
            print "Bottom party redistribution votes: " + str(bottom_dist)
            print "Updating vote list: " + str(votelist)
            print "Overall vote fraction: " + str(vote_fraction)
        
        ind_maxfrac = np.argmax(vote_fraction)

        n_iter += 1
        
        if vote_fraction[ind_maxfrac] >= 0.5:
            if verbose == True:
                print "FPTP Winner: " +  fptp_winner
                print "Winning party: "+ partylist[ind_maxfrac]
                print n_iter - n_nocand
                print '\n'
                    
            return [votelist, partylist[ind_maxfrac], n_iter-n_nocand]
        

def alternative_vote(riding_list):

    '''Performs an instant runoff a list of riding objects with the results
    modified according to the 2nd choice preferences defined in the function
    instant_runoff using a alternative vote system.''' 

    partylist = ['Conservative','Liberal', 'NDP-New Democratic Party', 'Green Party', 'Bloc Québécois']

    modified_ridings = []
    
    n_changed = 0
    changed_party = [0,0,0,0,0]
    party_lost = [0,0,0,0,0]
    results = [0,0,0,0,0]
    conchange = []
    libchange = []
    ndpchange = []
    grechange = []
    blochange = []
    n_iterations = []
    
    for riding in riding_list:
        
        print riding.name
        convotes = riding.party_result('Conservative')
        libvotes = riding.party_result('Liberal')
        ndpvotes = riding.party_result('NDP-New Democratic Party')
        grevotes = riding.party_result('Green Party')
        blovotes = riding.party_result('Bloc Québécois')

        votelist = np.array([convotes,libvotes,ndpvotes,grevotes,blovotes])
        ind_max = np.argmax(votelist)
        fptp_winner = partylist[ind_max]


        runoff_result = instant_runoff(np.array(votelist), verbose = True)
        n_iterations.append(runoff_result[2])
        #print runoff_result[1]
        #print fptp_winner
        #print '\n'
        
        if runoff_result[1] != fptp_winner:
            n_changed += 1
            
            if runoff_result[1] == 'Conservative':
                changed_party[0] += 1
                conchange.append(fptp_winner)
            if runoff_result[1] == 'Liberal':
                changed_party[1] += 1
                libchange.append(fptp_winner)
            if runoff_result[1] == 'NDP-New Democratic Party':
                changed_party[2] += 1
                ndpchange.append(fptp_winner)
            if runoff_result[1] == 'Green Party':
                changed_party[3] += 1
                grechange.append(fptp_winner)
            if runoff_result[1] == 'Bloc Québécois':
                changed_party[4] += 1
                blochange.append(fptp_winner)

            if fptp_winner == 'Conservative':
                party_lost[0] += 1
            if fptp_winner == 'Liberal':
                party_lost[1] += 1
            if fptp_winner == 'NDP-New Democratic Party':
                party_lost[2] += 1
            if fptp_winner == 'Green Party':
                party_lost[3] += 1
            if fptp_winner == 'Bloc Québécois':
                party_lost[4] += 1
        
        if runoff_result[1] == 'Conservative':
            results[0] += 1
        if runoff_result[1] == 'Liberal':
            results[1] += 1
        if runoff_result[1] == 'NDP-New Democratic Party':
            results[2] += 1
        if runoff_result[1] == 'Green Party':
            results[3] += 1
        if runoff_result[1] == 'Bloc Québécois':
            results[4] += 1

    print n_iterations.count(0), n_iterations.count(1), n_iterations.count(2), n_iterations.count(3) 
    print n_changed
    print changed_party
    print party_lost
    print results, sum(results)
    
    return results

def plot_results(AV_results):

    mpl.close()
    regular_results = [99, 184, 44, 1,10]
    plot_results = []
        
    x = [1, 1.75, 2.5, 3.25, 4]
    labels = ['CPC','LPC','NDP','GRN','BQ']
    fig, ax = mpl.subplots()
    AV = ax.bar([0.75,1.5,2.25,3,3.75],regular_results, width = 0.25, \
        color=['b','r','#FFA500','g','#07B1FF'], label='FPTP')
    AV = ax.bar(x,AV_results, width = 0.25, \
        color=['#3399ff','r','#FFA500','g','#07B1FF'], alpha = 0.5, linewidth=2, \
        label='IR')

    mpl.xticks(x, labels, rotation=45, size = 15)
    mpl.ylabel('Seats', size = 15)
    mpl.ylim([0,220])
    mpl.title('Election Results: FPTP vs. IR',size = 20)
    mpl.figtext(0.625,0.12,str(regular_results[3]),family='helvetica',weight='bold',size='large')
    mpl.figtext(0.675,0.12,str(AV_results[3]),family='helvetica',weight='bold',size='large')
    mpl.figtext(0.77,0.16,str(regular_results[4]),family='helvetica',weight='bold',size='large')
    mpl.figtext(0.82,0.16,str(AV_results[4]),family='helvetica',weight='bold',size='large')
    
    mpl.legend()
    mpl.show() 
    

if __name__ == '__main__':

    riding_list = extract_electiondata()
    av_results= alternative_vote(riding_list)
    plot_results(av_results)
