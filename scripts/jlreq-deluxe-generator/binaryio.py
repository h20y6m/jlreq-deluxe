import io
import logging
import os

logger = logging.getLogger(__name__)


class BinaryReader:
    def __init__(self, file):
        # Check if we were passed a file-like object
        if isinstance(file, os.PathLike):
            file = os.fspath(file)
        if isinstance(file, str):
            # No, it's a filename
            self._filePassed = 0
            self.filename = file
            self.fp = io.open(file, "rb")
        else:
            self._filePassed = 1
            self.fp = file
            self.filename = getattr(file, "name", None)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        result = ["<%s.%s" % (self.__class__.__module__, self.__class__.__qualname__)]
        if self.fp is not None:
            if self._filePassed:
                result.append(" file=%r" % self.fp)
            elif self.filename is not None:
                result.append(" filename=%r" % self.filename)
        else:
            result.append(" [closed]")
        result.append(">")
        return "".join(result)

    def __del__(self):
        """Call the "close()" method in case the user forgot."""
        self.close()

    def close(self):
        """Close the file."""
        if self.fp is None:
            return

        fp = self.fp
        self.fp = None
        fp.close()

    def read_all(self):
        return self.fp.read()

    def read_exact(self, n):
        b = self.fp.read(n)
        if len(b) != n:
            raise EOFError()
        return b

    def read_bytes(self, n):
        return self.read_exact(n)

    def read_u(self, n):
        v = 0
        for b in self.read_exact(n):
            v = (v << 8) | b
        return v

    def read_u8(self):
        return self.read_u(1)

    def read_u16(self):
        return self.read_u(2)

    def read_u24(self):
        return self.read_u(3)

    def read_u32(self):
        return self.read_u(4)

    def read_i(self, n):
        v = self.read_u(n)
        m = 1 << (n * 8)
        if v >= (m >> 1):
            v -= m
        return v

    def read_i8(self):
        return self.read_i(1)

    def read_i16(self):
        return self.read_i(2)

    def read_i24(self):
        return self.read_i(3)

    def read_i32(self):
        return self.read_i(4)

    def read_f4d20(self):
        return self.read_u24() * 0.00000095367431640625

    def read_f12d20(self):
        return self.read_i32() * 0.00000095367431640625


class BinaryWriter:
    def __init__(self, file):
        self.size = 0
        # Check if we were passed a file-like object
        if isinstance(file, os.PathLike):
            file = os.fspath(file)
        if isinstance(file, str):
            # No, it's a filename
            self._filePassed = 0
            self.filename = file
            self.fp = io.open(file, "wb")
        else:
            self._filePassed = 1
            self.fp = file
            self.filename = getattr(file, "name", None)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        result = ["<%s.%s" % (self.__class__.__module__, self.__class__.__qualname__)]
        if self.fp is not None:
            if self._filePassed:
                result.append(" file=%r" % self.fp)
            elif self.filename is not None:
                result.append(" filename=%r" % self.filename)
        else:
            result.append(" [closed]")
        result.append(">")
        return "".join(result)

    def __del__(self):
        """Call the "close()" method in case the user forgot."""
        self.close()

    def close(self):
        """Close the file."""
        if self.fp is None:
            return

        fp = self.fp
        self.fp = None
        fp.close()

    def write_bytes(self, b):
        self.size += len(b)
        self.fp.write(b)

    def write_u(self, n, v):
        self.write_bytes(bytes([(v >> (8 * (n - i - 1))) & 0xFF for i in range(n)]))

    def write_u8(self, v):
        self.write_u(1, v)

    def write_u16(self, v):
        self.write_u(2, v)

    def write_u24(self, v):
        self.write_u(3, v)

    def write_u32(self, v):
        self.write_u(4, v)

    def write_i(self, n, v):
        m = (1 << (n * 8)) - 1
        self.write_u(n, v & m)

    def write_i8(self, v):
        self.write_i(1, v)

    def write_i16(self, v):
        self.write_i(2, v)

    def write_i24(self, v):
        self.write_i(3, v)

    def write_i32(self, v):
        self.write_i(4, v)

    def write_f12d20(self, v):
        v = int(round(v * 1048576))
        self.write_i32(v)
