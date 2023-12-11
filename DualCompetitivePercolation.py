from igraph import Graph
import random 
import itertools as it
import copy


def nei_degree(v,g):
    res=0
    for nei in g.neighbors(v):
        res+=g.degree(nei)
        res+=g.degree(v)
    return res


# Dual Competitive Percolation
def DCP(n,m):
    gcc=[]
    g=Graph(n)
    add_order=[]
    while g.ecount()<m:
        g_components=g.components()
        components_list=list(g_components)
        gcc.append(max(g_components.sizes())/n)
        components_list.sort(key=len)
        if len(components_list)>=2:
            v_1=min(components_list[0],key=g.degree)
            v_2=min(components_list[1],key=g.degree)

        else:
            min_nd=min(components_list[0],key=lambda x:nei_degree(x,g))
            sorted_d=sorted(components_list[0],key=lambda x:nei_degree(x,g))
            min_nd_set=[]
            for i in components_list[0]:
                if nei_degree(i,g)==min_nd:
                    min_nd_set.append(i)
            if len(min_nd_set)<=1:
                min_nd_set=sorted_d[:10]
            sample_set=[(min_nd_set[i],min_nd_set[j]) for i in range(len(min_nd_set)) for j in range(i)]
            v_1,v_2=random.sample(sample_set,1)[0]
            cnt=0
            while g.are_connected(v_1, v_2):
                cnt+=1
                if cnt>2:
                    min_nd_set=sorted_d[:10]
                    sample_set=[(min_nd_set[i],min_nd_set[j]) for i in range(len(min_nd_set)) for j in range(i)]
                v_1,v_2=random.sample(sample_set,1)[0]
        g.add_edges([(v_1,v_2)])
        add_order.append((v_1,v_2))
    return gcc,g,add_order
    

def c_m(c_dict):
    return {i:c for i,c in c_dict.items() if len(c)>2}


def update_1(c_dict,c_candidate,e_candidate,id_1,id_2,c_1,c_2,v_1,v_2):
    
    if id_1>id_2:
        id_1,id_2=id_2,id_1
        
    new_c=c_1+c_2
    c_dict[id_1]=new_c
    c_dict.pop(id_2,-1)
    if len(new_c)>2:
        prod_c=list(it.product(c_1,c_2))
        prod_c.remove((v_1,v_2))
        if id_1 in e_candidate:
            if id_2 in e_candidate:
                added_c=prod_c+e_candidate[id_2]
            else:
                added_c=prod_c
            e_candidate[id_1].extend(added_c)
        else:
            if id_2 in e_candidate:
                added_c=prod_c+e_candidate[id_2]
            else:
                added_c=prod_c
            e_candidate[id_1]=added_c
        c_candidate[id_1]=new_c
        e_candidate.pop(id_2,-1)
        c_candidate.pop(id_2,-1)



# Improved Dual Competitive Percolation
def IDCP(n,m,p,m_s):
    gcc=[]
    g=Graph(n)
    add_order=[]
    g_components=g.components()
    
    c_dict={i:c for i,c in enumerate(g_components)}
    c_candidate=c_m(c_dict)
    e_candidate={}
    first=True
    
    extra_e_n=int((n-1)*(1/p-1))
    extra_e_n_tot=int(m*(1-p))
    
    added_e_n=0
    removed_e=[]
    
    while g.ecount()<m:
        
        M=g.ecount()
        
        g_components=g.components()
        gcc.append(max(g_components.sizes())/n)
        
        if len(c_dict)>=2:
            if len(c_candidate)==0:
                min_c_size=0
            else:
                min_c_size=len(min(c_dict.values(),key=len))
            if min_c_size==m_s and added_e_n!=extra_e_n:
                
                id_c,es=random.choice(list(e_candidate.items()))
                v_1,v_2=random.choice(es)
                e_candidate[id_c].remove((v_1,v_2))
                if len(e_candidate[id_c])==0:
                    e_candidate.pop(id_c,-1)
                    c_candidate.pop(id_c,-1)
                added_e_n+=1
                
                if added_e_n==extra_e_n:
                    copy_e=copy.deepcopy(e_candidate)
                    copy_c=copy.deepcopy(c_candidate)
                    
            else:
                (id_1,c_1),(id_2,c_2)=sorted(c_dict.items(),key=lambda x:len(x[1]))[:2]
                v_1=min(c_1,key=g.degree)
                v_2=min(c_2,key=g.degree)
                update_1(c_dict,c_candidate,e_candidate,id_1,id_2,c_1,c_2,v_1,v_2)

        elif added_e_n!=extra_e_n_tot:
            id_c,es=random.choice(list(copy_e.items()))
            v_1,v_2=random.choice(es)
            copy_e[id_c].remove((v_1,v_2))
            removed_e.append((v_1,v_2))
            if len(copy_e[id_c])==0:
                copy_e.pop(id_c,-1)
                copy_c.pop(id_c,-1)
            added_e_n+=1
        
        else:
            if first:
                [(id_c,es)]=e_candidate.items()
                es_tot=len(es)
                es_n=m-M+len(removed_e)
                e_can_id=random.sample(range(es_tot),es_n)
                first=False
                idx=0
            v_1,v_2=es[e_can_id[idx]]
            idx+=1
            while (v_1,v_2) in removed_e:
                v_1,v_2=es[e_can_id[idx]]
                idx+=1
        g.add_edges([(v_1,v_2)])
        add_order.append((v_1,v_2))
    return gcc,g,add_order