# Edge Collective Influence and Dual Competitive Percolation
These codes implement the ECI, IECI and IECIR network dismantling algorithm and DCP and IDCP percolation models proposed in 

> Peng, P., Fan, T., Ren, X. L., & Lü, L. (2023). Unveiling Explosive Vulnerability of Networks through Edge Collective Behavior. arXiv preprint arXiv:2310.06407.
> <https://arxiv.org/abs/2310.06407>

Please refer to the paper for details of the algorithms and the models.


## Code details

ECI, IECI, and IECIR algorithms are implemented in file `EdgeCollectiveInfluence.py` and `SumRule_Reorder.py`.

DCP and IDCP percolation models are implementes in file `DualCompetitivePercolation.py`.

`Example.ipynb` shows how to use our algorithm.

The above code can all run in a Python 3.10.6 environment.

Package Requirements:
> igraph 0.11.2
> 
> numpy 1.23.2
