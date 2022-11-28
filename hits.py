import networkx as nx
import json

def main():
    G = nx.Graph()
    f = open('httpswww.basketball-reference.com#pages.json')
    data = json.load(f)
    websites = data.keys()
    for site in websites:
        G.add_node(site)
    for node in G.nodes:
        adj_sites = data.get(node)
        for x in adj_sites:
            if x in G.nodes:
                G.add_edge(node,x)
    print(G)
    pr = nx.hits(G)
    print(pr)
    with open("hits_scores.json", "w") as outfile:
        json.dump(pr, outfile)

if __name__ == '__main__':
	main()
