from queue import Queue
from threading import Thread
from time import sleep, time

from brainflow import BrainFlowError
from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams

from .base import BCISignal, DeviceBase


class BrainFlowDevice(DeviceBase):
    __slots__ = "board_id", "board", "_channels", "_average_window", "_streaming", "_gather_thread", "_timestamp_channel", "_msg_queue", "_on_head", "_connected", "_board", "_params", "_signal_avg"
    window_size = 32

    @classmethod
    def CreateMuse2Device(cls):
        id = BoardIds.MUSE_2_BOARD
        params = BrainFlowInputParams()
        return cls(id, params)

    @classmethod
    def CreateMuse2BLEDDevice(cls, com_port: str = "COM4"):
        id = BoardIds.MUSE_2_BLED_BOARD
        params = BrainFlowInputParams()
        params.serial_port = com_port
        return cls(id, params)

    def __init__(self, board_id: BoardIds, params: BrainFlowInputParams):
        """Creates a new BrainFlowDevice. This is a wrapper around the BrainFlow library. This class is not thread safe. It is not recommended to use it in a multi-threaded environment. For more info how to populate the parameters see the BrainFlow docs. https://brainflow.readthedocs.io/en/stable/

        :param board_id: Board id of the device to connect to (see BrainFlow docs for more info).
        :type board_id: BoardIds
        :param params: Parameters for the device (see BrainFlow docs for more info).
        :type params: BrainFlowInputParams
        """
        super().__init__()
        self.board = None
        self.removal_time_stamp = 0
        self._average_window = []
        self.board_id = board_id
        self._channels = BoardShim.get_eeg_channels(
            self.board_id.value)

        # Get infos from lib
        desc = BoardShim.get_board_descr(self.board_id)
        self._timestamp_channel = desc["timestamp_channel"]
        self.channel_names = desc["eeg_names"].split(",")
        self.sample_rate = desc["sampling_rate"]

        # Init
        self._streaming = False
        self._gather_thread = None
        self._msg_queue = Queue()
        self._on_head = True
        self._connected = False
        self._params = params
        self._signal_avg = 0

    def start_stream(self):
        """Start data stream of device. Must be called before being able to fetch any data.
        """
        if self.board:
            self._streaming = True

    def stop_stream(self):
        """Stops data stream of device. After calling this no more data can be fetched.
        """
        if self.board:
            self._streaming = False
            self._msg_queue = Queue()

    def connect(self, timeout: int = 20, raise_exception: bool = True) -> bool:
        """Tries to connect to Muse device via Bluetooth.

        :param timeout: Timeout for connection, defaults to 20
        :type timeout: int, optional
        :param raise_exception: Raise exception when no connection could be created, defaults to True
        :type raise_exception: bool, optional
        :raises Exception: Device connection not possible
        :return: True if connection was successful, False otherwise
        :rtype: bool
        """
        # Disconnect if already connected
        self.disconnect()
        self._params.timeout = timeout
        self.board = BoardShim(self.board_id, self._params)

        # Try to connect
        try:
            self.board.prepare_session()
            self.board.start_stream()
        except BrainFlowError as e:
            if raise_exception:
                raise e
            return False

        # Start data gathering thread
        self._connected = True
        self._gather_thread = Thread(target=self._fetch_data)
        self._gather_thread.start()
        return True

    def disconnect(self):
        """Disconnect device from hardware.
        """
        # Return if not connected
        if not self._connected:
            return
        self._connected = False

        # Wait for thread to finish
        if self._gather_thread.is_alive():
            self._gather_thread.join()

        # Disconnect
        if self.board:
            self.stop_stream()
            self.board.stop_stream()
            self.board.release_all_sessions()
        del self.board
        self.board = None

    def __thread_disconnect(self):
        """Safely disconnect from gather thread.
        """
        if not self._connected:
            return
        self._connected = False
        if self.board:
            self.stop_stream()
            self.board.stop_stream()
            self.board.release_all_sessions()
        del self.board
        self.board = None

    def fetch_data(self) -> BCISignal:
        """Fetch data from device. Blocking if no data is present.

        :return: Fetched data from Muse.
        :rtype: BCISignal
        """
        if self._streaming:
            return self._msg_queue.get()
        raise Exception("Device is not streaming.")

    def is_worn(self) -> bool:
        """Checks if device is currently worn.

        :return: Is device currently on a head?
        :rtype: bool
        """
        return self._on_head and self._gather_thread.is_alive()

    def is_connected(self) -> bool:
        """Checks if device is connected to hardware. This does not indicate if the device is streaming. For that use is_streaming.

        :return: True if device is connected to hardware, False otherwise.
        :rtype: bool
        """
        return self._connected and self._gather_thread.is_alive()

    def has_data(self) -> bool:
        """Indicates if new data can be fetched. Should be called before calling fetch_data
        to circumvent possible exceptions.

        :return: Is data in buffer?
        :rtype: bool
        """
        return not self._msg_queue.empty()

    def _fetch_data(self):
        """Fetch data from Brainflow API and transform it for further processing.
        """
        last_timestamp = time()
        while self._connected:
            sleep(0.001)
            # Check if there is a sample to fetch
            sample_count = self.board.get_board_data_count()
            if sample_count == 0:
                # No new samples, check how long ago was last sample
                if time() - last_timestamp > 1:
                    self.__thread_disconnect()
                    break

                # Wait for at least 32 new samples being generated
                sleep(32 / self.sample_rate)
                continue

            # Fetch data
            try:
                sample = self.board.get_board_data(sample_count)
            except BaseException:
                self.disconnect()
                break

            # Check for empty sample
            if sample.shape[1] == 0:
                sleep(0.001)
                continue

            dim = sample.shape[1]
            for i in range(dim):
                timestamp = sample[self._timestamp_channel][i]
                signals = [sample[x][i] for x in self._channels]

                # Only need to check for the last samples in window size if
                # device is still on head
                if i > dim - self.window_size:
                    self._check_device_on_head(signals)

                # Save time stamp of last sample
                if i == dim - 1:
                    last_timestamp = timestamp

                if self._streaming:
                    self._msg_queue.put(BCISignal(timestamp, signals))

    def _check_device_on_head(self, sample: list):
        """Use window mechanism to check if device was taken of head
        during recording.

        :param sample: sample data points
        :type sample: list
        """
        max_sign = max([abs(x) for x in sample]) / self.window_size
        self._average_window.append(max_sign)
        self._signal_avg += max_sign

        if len(self._average_window) > self.window_size:
            self._signal_avg -= self._average_window.pop(0)

        if self._signal_avg > 700:
            if self._on_head:
                self._on_head = False
                self.removal_time_stamp = time()
        elif not self._on_head:
            self._on_head = True

    def __del__(self):
        self.disconnect
