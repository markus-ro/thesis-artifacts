from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from ...container import EEGContainer, EventContainer


@dataclass
class BenchmarkContainer():
    ident: str
    template_epochs: List[EventContainer]
    authentication_epochs: List[EventContainer]

    def num_template_epochs(self):
        return len(self.template_epochs)

    def num_authentication_epochs(self):
        return len(self.authentication_epochs)

    def avg_snr(self, channel_names: List[str] = None):
        return np.mean([x.avg_snr(channel_names=channel_names) for x in self.authentication_epochs] +
                       [x.avg_snr(channel_names=channel_names) for x in self.template_epochs])

    def avg_snr_template(self, channel_names: List[str] = None):
        return np.mean([x.avg_snr(channel_names=channel_names) for x in self.template_epochs]), np.std(
            [x.avg_snr(channel_names=channel_names) for x in self.template_epochs])

    def avg_snr_auth(self, channel_names: List[str] = None):
        return np.mean([x.avg_snr(channel_names=channel_names) for x in self.authentication_epochs]), np.std(
            [x.avg_snr(channel_names=channel_names) for x in self.authentication_epochs])

    def __str__(self):
        return f"Ident: {self.ident}, Template Epochs: {self.num_template_epochs()}, Authentication Epochs: {self.num_authentication_epochs()}"

    def __len__(self):
        return self.num_template_epochs() + self.num_authentication_epochs()
