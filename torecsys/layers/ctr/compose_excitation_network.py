from torecsys.utils.decorator import jit_experimental, no_jit_experimental_by_namedtensor
import torch
import torch.nn as nn


class ComposeExcitationNetworkLayer(nn.Module):
    r"""Layer class of Compose Excitation Network used in FAT-Deep :title:`Junlin Zhang et al, 2019`[1], which 
    is to compose field aware embedded tensors by 1D Convalution with a :math:`1 * 1` kernel feature-wisely from 
    a :math:`k * n` tensor of field i into a :math:`k * 1` tensor, then, concatenate the tensors and forward to 
    a fully-connect layers to calculate attention weights, finally, inputs' tensor are multiplied by attention 
    weights, and return outputs tensor with shape = (B, N * N, E).

    :Reference:

    #. `Junlin Zhang et al, 2019. FAT-DeepFFM: Field Attentive Deep Field-aware Factorization Machine <https://arxiv.org/abs/1905.06336>`_.

    """
    @no_jit_experimental_by_namedtensor
    def __init__(self, 
                 num_fields : int,
                 reduction  : int = 1):
        r"""Initialize ComposeExcitationNetworkLayer
        
        Args:
            num_fields (int): Number of inputs' fields. 
            reduction (int, optional): Size of reduction in fully-connect layer. 
                Defaults to 1.
        
        Attributes:
            pooling (torch.nn.Module): Adaptive average pooling layer to compose tensors.
            fc (torch.nn.Sequential): Sequential of linear and activation to calculate weights of 
                attention, which the linear layers are: 
                :math:`[Linear(N^2, \frac{N^2}{reduction}), Linear(\frac{N^2}{reduction}, N^2)]`. 
        """
        # refer to parent class
        super(ComposeExcitationNetworkLayer, self).__init__()

        # initialize 1d pooling layer to compose the embedding vectors
        self.pooling = nn.AdaptiveAvgPool1d(1)
        
        # initialize fully-connect layers to calculate attention
        self.fc = nn.Sequential(
            nn.Linear(num_fields ** 2, num_fields ** 2 // reduction),
            nn.ReLU(),
            nn.Linear(num_fields ** 2 // reduction, num_fields ** 2),
            nn.ReLU()
        )

    def forward(self, field_emb_inputs: torch.Tensor) -> torch.Tensor:
        r"""Forward calculation of ComposeExcitationNetworkLayer
        
        Args:
            field_emb_inputs (T), shape = (B, N * N, E), dtype = torch.long: Field aware embedded features tensors.
        
        Returns:
            T, shape = (B, N * N, E), dtype = torch.long: Output of ComposeExcitationNetworkLayer.
        """
        # pooling with inputs' shape = (B, N * N, E) to output's shape = (B, N * N, 1)
        pooled_inputs = self.pooling(field_emb_inputs.rename(None))
        pooled_inputs.names = ("B", "N", "E")

        # squeeze pooled_inputs into shape = (B, N * N)
        ## pooled_inputs = pooled_inputs.squeeze()
        pooled_inputs = pooled_inputs.flatten(["N", "E"], "N")

        # output's shape of attn_w = (B, N * N)
        attn_w = self.fc(pooled_inputs.rename(None))
        attn_w.names = ("B", "N")

        # unsqueeze to (B, N * N, 1) and expand as x's shape = (B, N * N, E)
        ## attn_w = attn_w.unsqueeze(-1)
        attn_w = attn_w.unflatten("N", (("N", attn_w.size("N")), ("E", 1)))
        ## outputs = field_emb_inputs * attn_w.expand_as(field_emb_inputs)
        outputs = field_emb_inputs * attn_w

        return outputs
