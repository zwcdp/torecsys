from torecsys.utils.decorator import jit_experimental, no_jit_experimental_by_namedtensor
import torch
import torch.nn as nn

class CrossNetworkLayer(nn.Module):
    r"""Layer class of Cross Network used in Deep & Cross Network :title:`Ruoxi Wang et al, 2017`[1], 
    to calculate cross-feature interaction element-wise by the following equation: for i-th layer, 
    math:`x_{i} = x_{0} * (w_{i} * x_{i-1} + b_{i}) + x_{0}`

    :Reference:

    #. `Ruoxi Wang et al, 2017. Deep & Cross Network for Ad Click Predictions <https://arxiv.org/abs/1708.05123>`_.

    """
    @no_jit_experimental_by_namedtensor
    def __init__(self, 
                 num_layers  : int,
                 embed_size  : int = None,
                 num_fields  : int = None,
                 inputs_size : int = None):
        r"""Initialize CrossNetworkLayer
        
        Args:
            num_layers (int): Number of layers of Cross Network
            embed_size (int, optional): Size of embedding tensor. 
                Required with num_fields. 
                Defaults to None.
            num_fields (int, optional): Number of inputs' fields. 
                Required with embed_size together. 
                Defaults to None.
            inputs_size (int, optional): Size of inputs. 
                Required when embed_size and num_fields are None. 
                Defaults to None.
        
        Attributes:
            inputs_size (int): Size of inputs, or Product of embed_size and num_fields.
            model (torch.nn.ModuleList): Module List of Cross Network Layers.
        
        Raises:
            ValueError: when embed_size or num_fields is missing if using embed_size and num_field pairs, or when inputs_size is missing if using inputs_size
        """
        # refer to parent class
        super(CrossNetworkLayer, self).__init__()

        # set inputs_size to N * E when using embed_size and num_fields
        if inputs_size is None and embed_size is not None and num_fields is not None:
            inputs_size = embed_size * num_fields
        # else, set inputs_size to inputs_size
        elif inputs_size is not None and (embed_size is None or num_fields is None):
            inputs_size = inputs_size
        else:
            raise ValueError("Only allowed:\n    1. embed_size and num_fields is not None, and inputs_size is None\n    2. inputs_size is not None, and embed_size or num_fields is None")

        # bind inputs_size to inputs_size
        self.inputs_size = inputs_size

        # initialize module list for Cross Network
        self.model = nn.ModuleList()

        # add modules to module list of Cross Network
        for _ in range(num_layers):
            self.model.append(nn.Linear(inputs_size, inputs_size))
    
    def forward(self, emb_inputs: torch.Tensor) -> torch.Tensor:
        """Forward calculation of CrossNetworkLayer
        
        Args:
            emb_inputs (T), shape = (B, N, E), dtype = torch.float: Embedded features tensors.
        
        Returns:
            T, shape = (B, N * E), dtype = torch.float: Output of CrossNetworkLayer
        """
        # reshape inputs from (B, N, E) to (B, N * E)
        ## emb_inputs = emb_inputs.view(-1, self.inputs_size)
        emb_inputs = emb_inputs.flatten(["N", "E"], "E")

        # copy emb_inputs to outputs for residual
        outputs = emb_inputs.detach().requires_grad_()

        # forward calculation of bilinear and add residual
        for layer in self.model:
            # shape = (B, N * E)
            outputs = emb_inputs * layer(outputs) + emb_inputs
        
        # rename tensor names
        outputs.names = ("B", "O")

        # unsqueeze outputs to (B, 1, O)
        ## outputs = outputs.unsqueeze(1)

        return outputs
