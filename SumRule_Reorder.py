import copy
from math import inf
import random
import numpy as np


def get_cluster_info(g):
    cluster_id = {}
    clusters={}
    for id, c in enumerate(g.components()):
        for v in c:
            if id in clusters:
                clusters[id].append(v)
            else:
                clusters[id]=[v]
            cluster_id[v] = id
    return cluster_id,clusters


def compute_cluster_adj_res(g, g_removed, cluster_id):
    n = g.vcount()
    id_num = max(cluster_id.values())+1
    adj = np.zeros((id_num,id_num),dtype=int)
    adj_r=np.zeros((id_num,id_num),dtype=int)
    for v in range(n):
        for u in g.neighbors(v):
            adj[cluster_id[v]][cluster_id[u]] += 1
        for w in g_removed.neighbors(v):
            adj_r[cluster_id[v]][cluster_id[w]] += 1
    for i in range(id_num):
        adj[i][i]/=2
        adj_r[i][i]/=2
    return adj-adj_r


def compute_cluster_adj(g, cluster_id):
    n = g.vcount()
    id_num = max(cluster_id.values())+1
    cluster_adj = np.zeros((id_num,id_num),dtype=int)
    for v in range(n):
        for u in g.neighbors(v):
            cluster_adj[cluster_id[v]][cluster_id[u]] += 1
    for i in range(id_num):
        cluster_adj[i][i]=0
    return cluster_adj


def reinsert_rule(g, g_removed, cluster_id, k, threshold):
    total_relation = 1
    while total_relation > 0:
        #The weighted adjacency matrix of the connected component.
        cluster_adj = compute_cluster_adj_res(g,g_removed, cluster_id)  

        relations = []
        # compute cluster_size
        cluster_size = [0]*(max(cluster_id.values())+1)
        for i in range(len(cluster_id)):
            cluster_size[cluster_id[i]] += 1

        #  disconnect clusters larger than the threshold.
        total_relation = 0
        for i in range(len(cluster_adj)):
            for j in range(i+1, len(cluster_adj)):
                if cluster_adj[i][j] != 0:
                    if cluster_size[i]+cluster_size[j] > threshold:
                        cluster_adj[i][j] = 0
                        cluster_adj[j][i] = 0
                    else:
                        total_relation += 1
                        relations.append((i, j))

        # print(f'\r Total relations:{total_relation}',end='')
        # sample relations
        if total_relation < k:
            k_relations = list(range(total_relation))
        else:
            k_relations = random.sample(range(total_relation),k)

        # find the relation with minimal value
        # print('     Reduced links :')
        indictor = -1
        min_value, temp_value = inf, inf
        for i in k_relations:
            v = relations[i][0]
            u = relations[i][1]
            nn_i=(cluster_size[v]+cluster_size[u])
            temp_value = (nn_i*(nn_i-1))/(cluster_adj[v][u])
            if temp_value < min_value:
                min_value = temp_value
                indictor = i
            if temp_value == min_value:
                v_ind=relations[indictor][0]
                u_ind=relations[indictor][1]
                size_i=cluster_size[v]+cluster_size[u]
                size_ind=cluster_size[v_ind]+cluster_size[u_ind]
                if  size_i<size_ind:
                    indictor=i

        # merge the two clusters
        if indictor != -1:
            cluster_id1 = relations[indictor][0]
            cluster_id2 = relations[indictor][1]
            cluster_id_temp = copy.deepcopy(cluster_id)
            for i in range(len(cluster_id)):
                if cluster_id_temp[i] == cluster_id2:
                    cluster_id[i] = cluster_id1
                elif cluster_id_temp[i] > cluster_id2:
                    cluster_id[i] = cluster_id_temp[i]-1

        total_relation -= 1


def get_and_remove_edges(g, cluster_id):
    remove_edges = []

    cluster_adj = compute_cluster_adj(g, cluster_id)

    max_id = max(cluster_id.values())+1
    cluster_size = [0]*max_id
    for i in range(len(cluster_id)):
        cluster_size[cluster_id[i]] += 1

    cluster_removed_flag = [False]*max_id

    total_relation = 1
    while total_relation:
        target_cluster = -1
        min_val, temp_val = inf, inf
        for i in range(max_id):
            edges = sum(cluster_adj[i])
            if edges == 0:
                continue
            temp_val = edges/cluster_size[i]
            if min_val > temp_val:
                min_val = temp_val
                target_cluster = i
        if target_cluster != -1:
            for i in range(len(cluster_adj[target_cluster])):
                cluster_adj[target_cluster][i] = 0
                cluster_adj[i][target_cluster] = 0

        for i in range(len(cluster_id)):
            if cluster_id[i] == target_cluster:
                for j in g.neighbors(i):
                    if cluster_id[i] != cluster_id[j] and not cluster_removed_flag[cluster_id[j]]:
                        remove_edges.append((i, j))

        cluster_removed_flag[target_cluster] = True

        total_relation = sum([sum(cluster_adj_row)
                             for cluster_adj_row in cluster_adj])

    # print(f'Dismantling edge set after reinsertion:{len(remove_edges)}')

    return remove_edges
