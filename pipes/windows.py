import win32pipe, win32file, pywintypes
import json

PIPE_NAME = r'\\.\pipe\dwll'

class WindowsPipe:
    def open_existing(self):
        try:
            self.write_handle = win32file.CreateFile(
                    self.pipe_name,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0, None, win32file.OPEN_EXISTING, 0, None
                )
            return self.write_handle
        except pywintypes.error as e:
            print(e)
            raise ValueError(e.args[2])
                

    def open_writer(self):
        try:
            self.write_handle = win32pipe.CreateNamedPipe(
                self.pipe_name,
                win32pipe.PIPE_ACCESS_DUPLEX, 
                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                1, 65536, 65536, 0, None)
            print(f"Named Pipe {self.pipe_name}")
            win32pipe.ConnectNamedPipe(self.write_handle, None)
            print("Client is conencted.")
        except pywintypes.error as e:
            if e.args[0] != 231:   # ERROR_FILE_NOT_FOUND
                raise ValueError(e.args[2])
        return self.write_handle


    def close(self):
        win32file.FlushFileBuffers(self.pipe_handle)
        # Disconnect the named pipe
        win32pipe.DisconnectNamedPipe(self.pipe_handle)
        # CLose the named pipe
        win32file.CloseHandle(self.pipe_handle)


    def write(self, payload):
        if self.write_handle is None:
            self.open_writer()
        err, bytes_written=win32file.WriteFile(
            self.write_handle, 
            json.dumps(payload).encode()
        )
        print(f"Wrote {payload} to pipe ({bytes_written} bytes)")


    def open_reader(self):
        try:
            self.read_handle = win32file.CreateFile(
                self.pipe_name, win32file.GENERIC_READ | win32file.GENERIC_WRITE, 
                0, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, None)
            # Set the read or blocking mode of the named pipe
            res = win32pipe.SetNamedPipeHandleState(
                      self.read_handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
            if res == 0:
                raise ValueError(f"SetNamedPipeHandleState Return Code: {res}")   # if function fails, the return value will be zero
            return self.read_handle
        except pywintypes.error as e:
            print(e.args)
            if e.args[0] == 2:   # ERROR_FILE_NOT_FOUND
                raise ValueError("No Named Pipe")
            raise


    def read(self, buffer_size: int = 65536):
        if self.read_handle is None:
            self.open_reader()
        try:
            resp = win32file.ReadFile(self.read_handle, buffer_size)
        except pywintypes.error as e:
            if e.args[0] == 2:   # ERROR_FILE_NOT_FOUND
                raise ValueError("No Named Pipe")
            elif e.args[0] == 109:   # ERROR_BROKEN_PIPE
                raise ValueError("Named Pipe is broken")
        return resp

    def __init__(self, server: bool = True, pipe_name: str = PIPE_NAME):
        self.pipe_name = pipe_name
        self.read_handle = None
        self.write_handle = None
        if not server:
            return
        try:
            self.open_existing()
            win32pipe.ConnectNamedPipe(self.write_handle, None)
            print("Successfully opened existing pipe")
        except ValueError:
            try:
                self.open_writer()
            except ValueError as e:
                raise e
        print("Pipe opened")
