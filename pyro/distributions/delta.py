import torch
from torch.autograd import Variable

from pyro.distributions.distribution import Distribution


class Delta(Distribution):
    """
    Delta Distribution - probability of 1 at `v`
    """

    def _sanitize_input(self, v):
        if v is not None:
            # stateless distribution
            return v
        elif self.v is not None:
            # stateful distribution
            return self.v
        else:
            raise ValueError("Parameter(s) were None")

    def __init__(self, v=None, batch_size=1, *args, **kwargs):
        """
        Params:
          `v` - value
        """
        self.v = v
        if v is not None:
            if v.dim() == 1 and batch_size > 1:
                self.v = v.expand(v, 0)
        super(Delta, self).__init__(*args, **kwargs)

    def sample(self, v=None, *args, **kwargs):
        _v = self._sanitize_input(v)
        if isinstance(_v, Variable):
            return _v
        return Variable(_v)

    def batch_log_pdf(self, x, v=None, batch_size=1, *args, **kwargs):
        _v = self._sanitize_input(v)
        if x.dim == 1:
            x = x.expand(batch_size, 0)
        return (torch.eq(x, _v.expand_as(x)) - 1).float() * 999999

    def log_pdf(self, x, v=None, *args, **kwargs):
        _v = self._sanitize_input(v)
        if torch.equal(x.data, _v.data.expand_as(x.data)):
            return Variable(torch.zeros(1))
        return Variable(torch.Tensor([-float("inf")]))

    def support(self, v=None, *args, **kwargs):
        _v = self._sanitize_input(v)
        # univariate case
        return (Variable(_v.data.index(i)) for i in range(_v.size(0)))