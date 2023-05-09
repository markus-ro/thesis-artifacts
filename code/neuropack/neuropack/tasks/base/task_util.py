from os import path
from typing import List


def file_filter(
        file_path: str,
        allowed_extensions: List[str],
        verbose=True) -> bool:
    """Checks a provided path to be:
    - Valid path
    - Valid image

    :param file_path: Path to file
    :type file_path: str
    :param allowed_extensions: Path to image.
    :type allowed_extensions: List[str]
    :param verbose: Print verbose output, defaults to True
    :type verbose: bool, optional
    :return: Is file suitable?
    :rtype: bool
    """
    if "." not in file_path:
        if verbose:
            print(f"File {file_path} does not have an extension.")
        return False

    if file_path.split(".")[-1] not in allowed_extensions:
        if verbose:
            print(f"File {file_path} is not of type {allowed_extensions}.")
        return False

    if not path.isfile(file_path):
        if verbose:
            print(f"File {file_path} does not exist.")
        return False
    return True
