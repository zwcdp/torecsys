from . import _CtrModule
from ..layers import FactorizationMachineLayer
from torecsys.utils.logging.decorator import jit_experimental
from functools import partial
import torch
import torch.nn as nn
from typing import Dict


class FactorizationMachineModule(_CtrModule):
    r"""FactoizationMachine is a module of Factorization Machine which calculate interactions 
    between fields by the following equation:
    :math:`\^{y}(x) := b_{0} + \sum_{i=1}^{n} w_{i} x_{i} + \sum_{i=1}^{n} \sum_{j=1+1}^{n} <v_{i},v_{j}> x_{i} x_{j}` .

    :Reference:

    #. `Steffen Rendle, 2010. Factorization Machine <https://www.csie.ntu.edu.tw/~b97053/paper/Rendle2010FM.pdf>`_.

    """
    @jit_experimental
    def __init__(self, 
                 embed_size    : int,
                 num_fields    : int,
                 dropout_p     : float = 0.0):
        r"""initialize Factorization Machine Module
        
        Args:
            embed_size (int): embedding size
            num_fields (int): number of fields in inputs
            dropout_p (float, optional): dropout probability after factorization machine. Defaults to 0.1.
        """
        super(FactorizationMachineModule, self).__init__()
        
        # initialize bias variable
        self.bias = nn.Parameter(torch.zeros(1))
        nn.init.uniform_(self.bias.data)
        
        self.fm = FactorizationMachineLayer(dropout_p)
    
    def forward(self, feat_inputs: torch.Tensor, emb_inputs: torch.Tensor) -> torch.Tensor:
        r"""feed forward of Factorization Machine Model 
        
        Args:
            feat_inputs (T), shape = (B, N, 1): first order outputs, i.e. outputs from nn.Embedding(V, 1)
            emb_inputs (T), shape = (B, N, E): second order outputs of one-hot encoding, i.e. outputs from nn.Embedding(V, E)
        
        Returns:
            torch.Tensor, shape = (B, 1 OR output size), dtype = torch.float: outputs of Factorization Machine
        """

        # feat_inputs'shape = (B, N, 1) and reshape to (B, N)
        fm_first = feat_inputs.squeeze()

        # pass to fm layer where its returns' shape = (B, E)
        fm_second = self.fm(emb_inputs).squeeze()
            
        # sum bias, fm_first, fm_second and get fm outputs with shape = (B, 1)
        outputs = fm_second + fm_first + bias

        return outputs