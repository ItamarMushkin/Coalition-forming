import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt
plt.style.use('fivethirtyeight')


def add_size_to_name(name, party_seats):
    return name+' ({})'.format(party_seats[name])


def add_sizes_to_partners(possible_partners_dict, party_seats):
    possible_partners_with_sizes = {add_size_to_name(k, party_seats): {add_size_to_name(_v, party_seats) for _v in v} 
                                    for k, v in possible_partners_dict.items()}
    return possible_partners_with_sizes


def plot_cooperation_network(possible_partners_dict, party_seats):
    g = nx.Graph(add_sizes_to_partners(possible_partners_dict, party_seats))
    node_size = [v * 30 for v in party_seats.values]
    plt.figure(figsize=(12, 8))
    nx.draw_networkx(g, node_size=node_size)


def create_coalitions(possible_partners_dict, party_seats, only_maximal=False, only_valid=False):
    graph = nx.Graph(possible_partners_dict)
    parties = party_seats.index
    cliques = nx.find_cliques(graph) if only_maximal else nx.enumerate_all_cliques(graph)

    coalitions = pd.DataFrame(data=[{'members': set(coalition),
                                     'value': sum(party_seats[party] for party in coalition)}
                                    for coalition in cliques])

    coalitions = coalitions[coalitions['value'] > 60] if only_valid else coalitions
    coalitions = coalitions.sort_values(by='value', ascending=False).reset_index(drop=True)

    if not coalitions.empty:
        coalitions['necessary_parties'] = coalitions.apply(
            lambda coalition: {p for p in parties
                               if party_seats[coalition['members'].difference({p})].sum() < 61}, axis=1)
        coalitions['necessary_are_sufficient'] = coalitions.apply(
            lambda coalition: party_seats[coalition['necessary_parties']].sum() > 60, axis=1)
        
    else:
        coalitions['necessary_parties'] = None        

    return coalitions


def plot_possible_coalitions(possible_partners_dict, coalitions_df, party_seats):

    n_cols = 1
    n_rows = (coalitions_df.shape[0]-1) // n_cols + 1
    plt.subplots(n_rows, n_cols, figsize=(12, 8*n_rows))

    g = nx.Graph(add_sizes_to_partners(possible_partners_dict, party_seats))
    
    pos = nx.fruchterman_reingold_layout(g, dim=2, k=None, pos=None, fixed=None,
                                         iterations=5000, weight='weight', scale=1.0, center=None)
    
    for idx, coalition in coalitions_df.iterrows():
        plt.subplot(n_rows, n_cols, idx+1)
        nx.draw_networkx(g,
                         node_color=['green' if p.split(' (')[0] in coalition['necessary_parties'] 
                                     else 'yellow' if (p.split(' (')[0] in coalition['members']
                                                       and not coalition['necessary_are_sufficient'])
                                     else 'orange' if (p.split(' (')[0] in coalition['members']
                                                       and coalition['necessary_are_sufficient'])
                                     else 'red' for p in g.nodes()],
                         pos=pos,
                         node_size=[30 * v for v in party_seats.values]
                         )
