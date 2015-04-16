import networkx as nx
from copy import deepcopy
import Queue

'''
Authors: Bala Bathula, Max Zhang, Kostas
Email: bgsquare@gmail.com
'''

import csv
import math

nodes_file=csv.reader(open('./inputs/nodes.csv','rb'));
links_file=csv.reader(open('./inputs/links.csv','rb'));



G_network=nx.Graph()
tmp=0
for row in nodes_file:
    if (tmp>0):
        G_network.add_node(row[0])
    tmp=+1


tmp=0
for row in links_file:
    if (tmp>0): # Ignores the first line in the file
        G_network.add_edge(row[0],row[1]);
        G_network[row[0]][row[1]]['weight']=float(row[2]);
    tmp+=1;



# Yen's algorithm for K-shortest paths in an edge-weighted graph G (undirected
# or directed)

# Cost/weight of path p in graph G
def pweight(G,p):
    w = 0;
    for i in range(len(p)-1): w += G[p[i]][p[i+1]]['weight'];
    return w

# Copy edge (a,z) of G, remove it, and return the copy.
# This can become expensive!
def cprm(G,a,z):
    ec = deepcopy(G[a][z]);
    G.remove_edge(a,z);
    return (a,z,ec)

# Copy node n of G, remove it, and return the copy.
# This can become expensive!
def cprmnode(G,n):
    ec = deepcopy(G[n]);
    G.remove_node(n);
    return (n,ec)

# K shortest paths in G from 'source' to 'target'
def yen(G,source,target,K):
    # First shortest path from the source to the target
    (c,p) = nx.single_source_dijkstra(G,source,target);
    A = [p[target]];  A_cost = [c[target]];
    B = Queue.PriorityQueue();
    
    for k in range(1,K):
        
        for i in range(len(A[k-1])-1):
            # Spur node ranges over the (k-1)-shortest path minus its last node:
            sn = A[k-1][i];
            # Root path: from the source to the spur node of the (k-1)-shortest path
            rp = A[k-1][:i];
            # We store the removed edges
            removed_edges = [];  removed_root_edges = [];  removed_root_nodes=[];
            # Remove the root paths
            for j in range(len(rp)-1):
            
                extra_edges = [];
                extra_edges = G.edges(rp[j]);
                        
                for eg in extra_edges:
                    
                    src=eg[0];
                    tgt=eg[1];
                    
                    
                    removed_root_edges.append(cprm(G,src,tgt));
                    
            
               
                removed_root_nodes.append(cprmnode(G,rp[j]));
                
                #G.remove_node(rp[j])
                
                
                
                
                
            if len(rp) > 0 and sn != target:
                
                extra_edges = [];
                extra_edges = G.edges(rp[len(rp)-1])  ;            
                
                for eg in extra_edges:
                    src=eg[0];
                    tgt=eg[1];
                    removed_root_edges.append(cprm(G,src,tgt));
 
                removed_root_nodes.append(cprmnode(G,rp[len(rp)-1]));
                
                
            # Remove the edges that are part of the already-found k-shortest paths
            # which share the same extended root path
            erp = A[k-1][:i+1];  # extended root path
            for p in A:
                if erp == p[:i+1] and G.has_edge(p[i],p[i+1]):
                    removed_edges.append(cprm(G,p[i],p[i+1]));
            # The spur path
            DONE = 0
            try:
                (csp,sp) = nx.single_source_dijkstra(G,sn,target)
                sp = sp[target];  csp = csp[target];
            except:
                # there is no spur path if sn is not connected to the target
                sp = [];  csp = None; DONE = 1;
                #return (A, A_cost)
            if len(sp) > 0:
                # The potential k-th shortest path (the root path may be empty)
                pk = rp + sp;
                
                for nd in removed_root_nodes: G.add_node(*nd);
                
                for re in removed_root_edges: G.add_edge(*re);
                cpk = pweight(G,pk);
                # Add the potential k-shortest path to the heap
                B.put((cpk,pk));
            # Add back the edges that were removed
            if len(sp) == 0: 
                for nd in removed_root_nodes: G.add_node(*nd);
                for re in removed_root_edges: G.add_edge(*re);
            for re in removed_edges: G.add_edge(*re);
            for nd in removed_root_nodes: G.add_node(*nd);

        if B.empty():
            print 'There are only', k, 'shortest paths for this pair';
            break;
        # The shortest path in B that is not already in A is the new k-th shortest path
        while not B.empty():
            cost, path = B.get();
            if path not in A:
                A.append(path);
                A_cost.append(cost);
                break;
   
    return (A, A_cost)

    
   

src='Ann_Arbor';
tgt='Seattle';
k=10;


k_path, path_costs=yen(G_network,src,tgt,k);

k_shortest_paths_file=open('%d_SPs_btw_%s_%s.csv' %(k,src,tgt),'w');
k_shortest_paths_file.write('Source,Target,kth-path,Distance,,,SHORTEST PATH,,,,,\n');
k_shortest_paths_file.write('%s,%s,' %(src,tgt));

for i in enumerate(k_path):
    if (i[0]==0):
        k_shortest_paths_file.write('%d,%f,,,' %(i[0]+1,path_costs[i[0]]));
    else:
        k_shortest_paths_file.write(',,%d,%f,,,' %(i[0]+1,path_costs[i[0]]));
    for j in range(len(i[1])):
        k_shortest_paths_file.write('%s,' %(i[1][j]))
    
    k_shortest_paths_file.write('\n');
