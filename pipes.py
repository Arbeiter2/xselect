import msvcrt
import os

# No idea what is going on here but if it works, it works.
from ctypes import windll, byref, wintypes, GetLastError, POINTER
from ctypes.wintypes import HANDLE, DWORD, BOOL

# ???
LPDWORD = POINTER(DWORD)
PIPE_NOWAIT = wintypes.DWORD(0x00000001)
ERROR_NO_DATA = 232


class AdvancedFD:
    """
    A wrapper for a file descriptor so that we can call:
        `<AdvancedFD>.read(number_of_bytes)` and
        `<AdvancedFD>.write(data_as_bytes)`

    It also makes the `read_fd` non blocking. When reading from a non-blocking
    pipe with no data it returns b"".

    Methods:
        write(data: bytes) -> None
        read(number_of_bytes: int) -> bytes
        rawfd() -> int
        close() -> None
    """
    def __init__(self, fd: int):
        self.fd = fd
        self.closed = False

    def __del__(self) -> None:
        """
        When this object is garbage collected close the fd
        """
        self.close()

    def close(self) -> None:
        """
        Closes the file descriptor.
        Note: it cannot be reopened and might raise an error if it is
        being used. You don't have to call this function. It is automatically
        called when this object is being garbage collected.
        """
        self.closed = True

    def write(self, data: bytes) -> None:
        """
        Writes a string of bytes to the file descriptor.
        Note: Must be bytes.
        """
        os.write(self.fd, data)

    def read(self, x: int) -> bytes:
        """
        Reads `x` bytes from the file descriptor.
        Note: `x` must be an int
              Returns the bytes. Use `<bytes>.decode()` to convert it to a str
        """
        try:
            return os.read(self.fd, x)
        except KeyboardInterrupt:
            raise OSError("Terminated by user")
        except OSError as error:
            err_code = GetLastError()
            # If the error code is `ERROR_NO_DATA`
            if err_code == ERROR_NO_DATA:
                # Return an empty string of bytes
                return b""
            else:
                # Otherwise raise the error
                website = ("https://docs.microsoft.com/en-us/windows/win32/"
                           "debug/system-error-codes--0-499-")
                raise OSError(f"An exception occured. Error code: {err_code} Look up"
                               " the error code here: {website}")

    def config_non_blocking(self) -> bool:
        """
        Makes the file descriptor non blocking.
        Returns `True` if sucessfull, otherwise returns `False`
        """

        # Please note that this is kindly plagiarised from:
        # https://stackoverflow.com/a/34504971/11106801
        SetNamedPipeHandleState = windll.kernel32.SetNamedPipeHandleState
        SetNamedPipeHandleState.argtypes = [HANDLE, LPDWORD, LPDWORD, LPDWORD]
        SetNamedPipeHandleState.restype = BOOL
        handle = msvcrt.get_osfhandle(self.fd)
        res = windll.kernel32.SetNamedPipeHandleState(handle,
                                                      byref(PIPE_NOWAIT), None,
                                                      None)
        return not (res == 0)

    def rawfd(self) -> int:
        """
        Returns the raw fd as an int.
        """
        return self.fd


class NonBlockingPipe:
    """
    Creates 2 file descriptors and wrapps them in the `AdvancedFD` class
    so that we can call:
        `<AdvancedFD>.read(number_of_bytes)` and
        `<AdvancedFD>.write(data_as_bytes)`

    It also makes the `read_fd` non blocking. When reading from a non-blocking
    pipe with no data it returns b"".

    Methods:
        write(data: bytes) -> None
        read(number_of_bytes: int) -> bytes
        rawfds() -> (int, int)
        close() -> None
    """
    def __init__(self, non_blocking: bool = False):
        self.read_fd, self.write_fd = self.create_pipes()
        if non_blocking:
            self.read_fd.config_non_blocking()

    def __del__(self) -> None:
        """
        When this object is garbage collected close the fds
        """
        self.close()

    def close(self) -> None:
        """
        Note: it cannot be reopened and might raise an error if it is
        being used. You don't have to call this function. It is automatically
        called when this object is being garbage collected.
        """
        self.read_fd.close()
        self.write_fd.close()

    def create_pipes(self) -> (AdvancedFD, AdvancedFD):
        """
        Creates 2 file descriptors and wrapps them in the `Pipe` class so
        that we can call:
            `<Pipe>.read(number_of_bytes)` and
            `<Pipe>.write(data_as_bytes)`
        """
        read_fd, write_fd = os.pipe()
        return AdvancedFD(read_fd), AdvancedFD(write_fd)

    def write(self, data: bytes) -> None:
        """
        Writes a string of bytes to the file descriptor.
        Note: Must be bytes.
        """
        self.write_fd.write(data)

    def read(self, number_of_bytes: int) -> bytes:
        """
        Reads `x` bytes from the file descriptor.
        Note: `x` must be an int
              Returns the bytes. Use `<bytes>.decode()` to convert it to a str
        """
        return self.read_fd.read(number_of_bytes)

    def rawfds(self) -> (int, int):
        """
        Returns the raw file descriptors as ints in the form:
            (read_fd, write_fd)
        """
        return self.read_fd.rawfd(), self.write_fd.rawfd()


if __name__  == "__main__":
    # Create the nonblocking pipe
    pipe = NonBlockingPipe()

    pipe.write(b"xxx")
    print(pipe.read(1024)) # Check if it can still read properly

    pipe.write(b"yyy")
    print(pipe.read(1024)) # Read all of the data in the pipe
    print(pipe.read(1024)) # Check if it is non blocking
