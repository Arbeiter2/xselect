import os
import errno

UNIX_PIPE_NAME = '/var/tmp/pipe.bin'

class UnixPipe:
    def create_fifo(self):
        try:
            os.mkfifo(UNIX_PIPE_NAME)
        except OSError as oe: 
            if oe.errno != errno.EEXIST:
                raise
        print("FIFO created")          

    def open_writer(self):
        try:
            self.write_handle = os.open(UNIX_PIPE_NAME, os.O_RDWR)
            return self.write_handle
        except OSError as exc:
            if exc.errno == errno.ENXIO:
                self.write_handle = None
            else:
                raise


    def close(self):
        if self.write_handle:
            os.close(self.write_handle)
        if self.read_handle:
            os.close(self.read_handle)


    def write(self, payload):
        if self.write_handle is None:
            self.open_writer()
        try:
            count = os.write(self.write_handle, payload)
            os.write(self.write_handle, '\n'.encode())
        except OSError as exc:
            if exc.errno == errno.EPIPE:
                pass
            else:
                raise
        print(f"Wrote {payload} to pipe ({count} bytes)")


    def open_reader(self):
        self.read_handle = os.open(UNIX_PIPE_NAME, os.O_RDONLY)
        self.file = os.fdopen(self.read_handle)
        return self.read_handle


    def read(self, buffer_size: int = 65536):
        if self.read_handle is None:
            self.open_reader()
        try:
            #resp = os.read(self.read_handle, buffer_size)
            resp = self.file.readline()
        except OSError as exc:
            if exc.errno == errno.EAGAIN or exc.errno == errno.EWOULDBLOCK:
                resp = None
            else:
                raise
        return resp

    def __init__(self, server: bool = True):
        self.read_handle = self.file = None
        self.write_handle = None
        if not server:
            return
        self.create_fifo()

    def __del__(self):
        self.close()
