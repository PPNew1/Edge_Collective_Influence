import copy
import math
from igraph import *
from SumRule_Reorder import *


def cal_CI(g,l):
    deg=g.degree
    CI = {}
    layer_l = {}
    ball_l ={}
    for v in g.vs:
        k_sum=0
        it = g.bfsiter(v, advanced=True)
        layer_l_v = []
        ball=[]
        for u, d, _ in it:
            if d > l+1:
                break
            if d>0 and d <=l+1:
                ball.append(u['id'])
            if d == l:
                layer_l_v.append(u['id'])
                k_sum+=deg(u)-1
            
        layer_l[v['id']] = layer_l_v
        ball_l[v['id']] = ball
        CI[v['id']] = (deg(v)-1)*k_sum
    return CI,layer_l,ball_l


def update_CI(g,CI_res,remove_nodes_ids,layers_l,ball_l,l):
    deg=g.degree
    for remove_nodes_id in remove_nodes_ids:
        layers_l.pop(remove_nodes_id)
        ball_l.pop(remove_nodes_id)
        CI_res.pop(remove_nodes_id)
        
    for v_id,ball_l_v in ball_l.items():
        for remove_nodes_id in remove_nodes_ids:
            if remove_nodes_id in ball_l_v:
                v=g.vs.find(id=v_id)
                it = g.bfsiter(v, advanced=True)
                layer_l_v = []
                ball=[]
                k_sum=0
                for u, d, _ in it:
                    if d > l+1:
                        break
                    if d>0 and d <=l+1:
                        ball.append(u['id'])
                    if d == l:
                        layer_l_v.append(u['id'])
                        k_sum+=deg(u)-1
                    
                layers_l[v['id']] = layer_l_v
                ball_l[v['id']] = ball
                    
                CI_res[v['id']] = (deg(v)-1)*k_sum
                break


def ECI(g, p=0.01, l=1, remove_p=-1):
    """
    Args:
        g (_type_): igraph.Graph
        p (float, optional): Dismantling Target pN. Defaults to 0.01.
        l (int, optional): Radius of the Ball. Defaults to 3.

    Returns:
        _type_: cost:remove_link_p  res:gcc_p
    """
    
    
    g_copy = copy.deepcopy(g)
    lg = g.linegraph()
    
    lg.vs['id']=range(lg.vcount())
    g_copy.es['id']=range(g_copy.ecount())
    
    N=g_copy.vcount()
    M = g_copy.ecount()
    
    #Number of edges removed in a single step.
    if remove_p==-1:
        remove_num_per=1
    else:
        remove_num_per=math.ceil(M*remove_p)
    
    gcc_p = []
    remove_link_p = []
    
    gcc = get_gcc_size(g_copy)
    gcc_i = get_gcc_size(g_copy)
    threshold = gcc*p
    gcc_p.append(gcc_i/gcc)
    remove_link_p.append(0)

    CI_res,layers_l,ball_l=cal_CI(lg,l)
    
    remove_order = []
    times_count = 0
    
    while gcc_i > threshold:
        v_list=[v for v,_ in 
                sorted(CI_res.items(),
                       key=lambda x:x[1],reverse=True)[:remove_num_per]]
        for remove_node_id in v_list:
            remove_node = lg.vs.find(id=remove_node_id)
            remove_edge= g_copy.es.find(id=remove_node_id)
            remove_order.append(remove_edge.tuple)
            #Remove nodes in the line graph, remove edges in the original graph.
            lg.delete_vertices(remove_node)
            g_copy.delete_edges(remove_edge)
            times_count += 1
        #update ball,layers
        update_CI(lg,CI_res,v_list,layers_l,ball_l,l)
        #Save the result at each step.
        gcc_i = max(g_copy.components().sizes())
        gcc_p.append(gcc_i/gcc)
        M_i = g_copy.ecount()
        remove_link_p.append((M-M_i)/M) 
    
    return remove_link_p, gcc_p, remove_order, g_copy


def get_gcc_size(g: Graph):
    return max(g.components().sizes())


def cal_gcc_remove_p(g,remove_order):
    g_copy=copy.deepcopy(g)
    M=g_copy.ecount()
    M_i=g_copy.ecount()
    gcc=get_gcc_size(g_copy)
    gcc_i=get_gcc_size(g_copy)
    gcc_p=[gcc_i/gcc]
    remove_p=[(M-M_i)/M]
    for e in remove_order:
        g_copy.delete_edges([e])
        gcc_i = get_gcc_size(g_copy)
        gcc_p.append(gcc_i/gcc)
        
        M_i = g_copy.ecount()
        remove_p.append((M-M_i)/M)
        
    return remove_p,gcc_p


def IECIR(g,k=100, p=0.01, l=1,remove_p=-1):
    
    lg = g.linegraph()
    g_copy = copy.deepcopy(g)
    final_g= copy.deepcopy(g)
    
    lg.vs['id']=range(lg.vcount())
    g_copy.es['id']=range(g_copy.ecount())
    final_g.es['id']=range(final_g.ecount())

    M = g_copy.ecount()
    
    #Number of edges removed in a single step.
    if remove_p==-1:
        remove_num_per=1
    else:
        remove_num_per=math.ceil(M*remove_p)
    
    # ECI、IECI，IECIR
    gcc_p_0 = []
    gcc_p_1 = []
    
    remove_link_p_0 = []
    remove_link_p_1 = []
    
    gcc = get_gcc_size(g_copy)
    gcc_i = get_gcc_size(g_copy)
    if p==-1:
        threshold = 1
    else:
        threshold = gcc*p
    gcc_p_0.append(gcc_i/gcc)
    gcc_p_1.append(gcc_i/gcc)

    remove_link_p_0.append(0)
    remove_link_p_1.append(0)

    CI_res,layers_l,ball_l=cal_CI(lg,l)

    remove_edges_0 = []
    times_count = 0
    while gcc_i > threshold:
        #The edges that need to be removed.
        v_list=[v for v,_ in 
                sorted(CI_res.items(),
                       key=lambda x:x[1],reverse=True)[:remove_num_per]]
        for remove_node_id in v_list:
            remove_node = lg.vs.find(id=remove_node_id)
            remove_edge= g_copy.es.find(id=remove_node_id)
            #Save the removed edges.
            remove_edges_0.append(remove_edge.tuple)
            #Remove nodes in the line graph, remove edges in the original graph.
            lg.delete_vertices(remove_node)
            g_copy.delete_edges(remove_edge)
            times_count += 1
        #update ball,layers
        update_CI(lg,CI_res,v_list,layers_l,ball_l,l)    
        #Save the result at each step.
        gcc_i = max(g_copy.components().sizes())
        gcc_p_0.append(gcc_i/gcc)
        M_i = g_copy.ecount()
        remove_link_p_0.append((M-M_i)/M)    
        

    # print(f'g-copy Components-Number:{len(g_copy.components())},Remove-Number:{len(remove_edges_0)}')

    # logger.info(f'ECI END. Then Run Reinsertion and Reorder.')
    if k==-1:
        k=len(g_copy.components())
    cluster_id,clusters = get_cluster_info(g_copy)

    reinsert_rule(g, g_copy, cluster_id, k, threshold)
    final_remove_edges = get_and_remove_edges(g, cluster_id)

    #Adjust the order of edges in final_remove_edges
    for i in range(len(final_remove_edges)):
        e = final_remove_edges[i]
        if e[0] > e[1]:
            final_remove_edges[i] = (e[1], e[0])

    # IECI: after reinsertion, remove edges based on ECI order.
    remove_edges_1 = []
    for e in remove_edges_0:
        if e in final_remove_edges:
            remove_edges_1.append(e)
            final_g.delete_edges([e])
            gcc_i = get_gcc_size(final_g)
            gcc_p_1.append(gcc_i/gcc)
            M_i = final_g.ecount()
            remove_link_p_1.append((M-M_i)/M)
    
    remove_link_p_2,gcc_p_2=cal_gcc_remove_p(g,final_remove_edges)

    ECI_res = (remove_link_p_0, gcc_p_0, remove_edges_0)
    IECI_res = (remove_link_p_1, gcc_p_1, remove_edges_1)
    IECIR_res = (remove_link_p_2,gcc_p_2,final_remove_edges)
    
    return ECI_res, IECI_res, IECIR_res