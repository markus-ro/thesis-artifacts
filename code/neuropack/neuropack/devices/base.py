from abc import ABC, abstractmethod
from ctypes import c_double, c_short
from dataclasses import dataclass
from multiprocessing import Pipe, Process, Value
from typing import List

from numpy.typing import NDArray


@dataclass
class BCISignal:
    timestamp: float
    signals: List[float]


class DeviceBase(ABC):
    __slots__ = "removal_time_stamp", "sample_rate", "channel_names"

    @abstractmethod
    def start_stream():
        """Start data stream of device. Must be called before being able to fetch any data.
        """
        pass

    @abstractmethod
    def stop_stream():
        """Stop data stream of device. Prevents any further data from being fetched."""
        pass

    @abstractmethod
    def connect(self, timeout: int = 20, raise_exception: bool = True):
        """Tries to connect to device. If no connection could be established, an exception is raised. If raise_exception is set to False, the function returns False instead. This function is blocking and will wait for the connection to be established. The timeout parameter can be used to limit the waiting time.

        :param timeout: Timeout for connection, defaults to 20
        :type timeout: int, optional
        :param raise_exception: Raise exception when no connection could be created, defaults to True
        :type raise_exception: bool, optional
        """
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnects from device. After calling this no more data can be fetched.
        """
        pass

    @abstractmethod
    def fetch_data(self) -> BCISignal:
        """Fetches data from device.

        :return: Data from device as BCISignal object containing timestamp and signal values as list of floats (one value per channel) in the same order as channel_names.
        :rtype: BCISignal
        """
        pass

    @abstractmethod
    def has_data(self) -> bool:
        """Checks if data is available. This function is non-blocking. It returns True if data is available, False otherwise. If data is available, fetch_data() can be called without blocking.

        :return: True if data is available, False otherwise
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_worn(self) -> bool:
        """Checks if device is worn. This function is non-blocking. It returns True if device is worn, False otherwise.

        :return: True if device is worn, False otherwise
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Checks if device is connected. This function is non-blocking. It returns True if device is connected, False otherwise. If device is not connected, no data can be fetched.

        :return: True if device is connected, False otherwise
        :rtype: bool
        """
        pass
