import torch
import itertools
import functools
from torch.autograd import Variable
from pyro.distributions.distribution import Distribution


class Bernoulli(Distribution):
    """
    Multi-variate bernoulli
    """

    def _sanitize_input(self, ps):
        if ps is not None:
            # stateless distribution
            return ps
        elif self.ps is not None:
            # stateful distribution
            return self.ps
        else:
            raise ValueError("Parameter(s) were None")

    def __init__(self, ps=None, batch_size=1, *args, **kwargs):
        """
        Params:
          ps = tensor of probabilities
        """
        self.ps = ps
        if ps is not None:
            if ps.dim() == 1:
                self.ps = ps.expand(batch_size, ps.size(0))
        super(Bernoulli, self).__init__(*args, **kwargs)

    def sample(self, ps=None, *args, **kwargs):
        """
        Reparameterized Bernoulli sampler.
        """
        _ps = self._sanitize_input(ps)
        return torch.bernoulli(_ps)

    def log_pdf(self, x, ps=None, batch_size=1, *args, **kwargs):
        """
        Bernoulli log-likelihood
        """
        _ps = self._sanitize_input(ps)
        x_1 = x - 1
        ps_1 = _ps - 1
        xmul = torch.mul(x, _ps)
        xmul_1 = torch.mul(x_1, ps_1)
        logsum = torch.log(torch.add(xmul, xmul_1))
        return torch.sum(logsum)

    def batch_log_pdf(self, x, ps=None, batch_size=1, *args, **kwargs):
        _ps = self._sanitize_input(ps)
        if x.dim() == 1 and _ps.dim() == 1 and batch_size == 1:
            return self.log_pdf(x)
        elif x.dim() == 1:
            x = x.expand(batch_size, x.size(0))
        if _ps.size() != x.size():
            _ps = _ps.expand_as(x)
        x_1 = x - 1
        ps_1 = _ps - 1
        xmul = torch.mul(x, _ps)
        xmul_1 = torch.mul(x_1, ps_1)
        logsum = torch.log(torch.add(xmul, xmul_1))
        return torch.sum(logsum, 1)

    def support(self, ps=None, *args, **kwargs):
        _ps = self._sanitize_input(ps)
        if _ps.dim() == 1:
            return iter([Variable(torch.ones(1)), Variable(torch.zeros(1))])
        size = functools.reduce(lambda x, y: x * y, _ps.size())
        return (Variable(torch.Tensor(list(x)).view_as(_ps))
                for x in itertools.product(torch.Tensor([0, 1]), repeat=size))