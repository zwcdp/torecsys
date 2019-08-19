from torecsys.utils.decorator import jit_experimental
import torch
import torch.nn as nn


class FactorizationMachineLayer(nn.Module):
    r"""FactorizationMachineLayer is a layer used in Factorization Machine to calculate low 
    dimension cross-features interactions.
    
    :Reference:
    
    #. `Steffen Rendle, 2010. Factorization Machine <https://www.csie.ntu.edu.tw/~b97053/paper/Rendle2010FM.pdf>`_.
    
    """
    @jit_experimental
    def __init__(self, 
                 dropout_p: float = 0.0):
        r"""initialize factorization machine layer module
        
        Args:
            dropout_p (float, optional): dropout probability after factorization machine. Defaults to 0.0.
        """
        super(FactorizationMachineLayer, self).__init__()
        self.dropout = nn.Dropout(dropout_p)
        
    def forward(self, emb_inputs: torch.Tensor) -> torch.Tensor:
        r"""feed-forward calculation of factorization machine layer
        
        Args:
            emb_inputs (T), shape = (B, N, E), dtype = torch.float: features matrices of inputs
        
        Returns:
            T, shape = (B, 1, O), dtype = torch.float: output of factorization machine layer
        """
        # squared sum embedding where output shape = (B, E)
        squared_sum_embs = (emb_inputs.sum(dim=1)) ** 2
        
        # sum squared embedding where output shape = (B, E)
        sum_squared_embs = (emb_inputs ** 2).sum(dim=1)
        
        # calculate output of fm
        outputs = 0.5 * (squared_sum_embs - sum_squared_embs)
        outputs = self.dropout(outputs)
        return outputs.unsqueeze(1)
        