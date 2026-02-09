from io import BytesIO

import numpy
import sys
import wave

import numpy as np


def read(path: BytesIO) -> tuple[np.ndarray, int]:
    with wave.open(path, 'rb') as file:
        sr = file.getframerate()
        bytes = file.getsampwidth()
        channels = file.getnchannels()
        data = file.readframes(file.getnframes())

    assert bytes in [1, 2, 3, 4]
    bits = bytes * 8
    scaler = 2 ** (bits - 1) - 1

    data = numpy.frombuffer(data, dtype=numpy.uint8).reshape(-1, bytes)
    data = numpy.asarray([
        int.from_bytes(frame, signed=(bits != 8), byteorder=sys.byteorder)
        for frame in data])
    data = data.astype(float).reshape(-1, channels)

    data -= 128 if bits == 8 else 0
    data = (data + 0.5) / (scaler + 0.5)
    data = data.clip(-1, +1)

    return data.flatten() if channels == 1 else data, sr


def write(path: BytesIO, data: np.ndarray, sr: int, bits: int=32) -> None:
    data = numpy.asarray(data)
    assert data.dtype in [float, complex]
    assert data.ndim in [1, 2]
    assert data.size > 0

    if numpy.iscomplex(data).any():
        assert data.ndim == 1
        data = numpy.stack((numpy.real(data), numpy.imag(data)))

    if data.ndim == 2:
        if data.shape[0] == 2:
            channels = data.shape[0]
            data = data.ravel('F')
        else:
            channels = data.shape[1]
            data = data.ravel('C')
    else:
        channels = 1

    assert bits in [8, 16, 24, 32]
    bytes = bits // 8
    scaler = 2 ** (bits - 1) - 1

    data = data.clip(-1, +1)
    data = (data * (scaler + 0.5)) - 0.5
    data += 128 if bits == 8 else 0

    data = b''.join([
        int(frame).to_bytes(length=bytes, signed=(bits != 8), byteorder=sys.byteorder)
        for frame in data])

    with wave.open(path, 'wb') as file:
        file.setframerate(sr)
        file.setsampwidth(bytes)
        file.setnchannels(channels)
        file.writeframes(data)
