from enum import Enum
from typing import List, Union

from ..container import EEGContainer, EventContainer
from .filters import *


class ComponentType(Enum):
    Desired = 1
    Undesired = 2


class PreprocessingPipeline():
    def __init__(self, *filters: List[FilterBase]) -> None:
        """Preprocessing pipeline for containers. Applies a list of filters to the containers.

        :param filters: List of filters to apply to the containers. Defaults to empty list.
        :type filters: List[FilterBase]
        """
        self.filters = list(filters)

    def add_filter(self, filter: FilterBase):
        """Add a filter to the pipeline. Filters are applied in the order they are added.

        :param filter: Filter to add to the pipeline.
        :type filter: FilterBase
        """
        self.filters.append(filter)

    def apply(self,
              container: Union[EventContainer,
                               List[EventContainer],
                               EEGContainer,
                               List[EEGContainer]]):
        """Apply the pipeline to a container or a list of containers. The pipeline is applied in the order the filters were added.

        :param container: Event or list of containers to apply the pipeline to.
        :type container: Union[EventContainer, List[EventContainer], EEGContainer, List[EEGContainer]]
        """
        if not isinstance(container, list):
            container = [container]
        for co in container:
            for filter in self.filters:
                filter.apply(co)

    def __str__(self) -> str:
        _sub = ", ".join([str(x) for x in self.filters])
        return f"PreprocessingPipeline({_sub})"
