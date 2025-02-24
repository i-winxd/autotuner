import re

import numpy as np
from stftpitchshift import StftPitchShift


def _semicent(value):
    return value.startswith('+') or value.startswith('-') or (
            value.startswith('0') and '.' not in value)


def _number(value: str) -> int:
    return int(value[:-1]) * 1024 if value.lower().endswith('k') else int(value)


def _semitone(value):
    return pow(2, float(re.match('([+,-]?\\d+){1}([+,-]\\d+){0,1}', value)[1]) / 12)


def _cent(value):
    return pow(2, float(re.match('([+,-]?\\d+){1}([+,-]\\d+){0,1}', value)[2] or 0) / 1200)


class _PitchProcessor:
    def __init__(self) -> None:
        timbre = "1.0"
        quefrency = 1.5
        rms = False

        self.quefrency = float(quefrency) * 1e-3
        self.timbre = 4.0
        self.distortion = _semitone(timbre) * _cent(timbre) if _semicent(timbre) else float(timbre)
        self.normalization = rms

        window = "1024"
        overlap = "32"
        self.framesize = list(_number(framesize) for framesize in window.split(','))
        self.hopsize = self.framesize[-1] // int(overlap)

    def process_audio_batch(self, audio: np.ndarray, samplerate: int, pitch: int) -> np.ndarray:
        x = audio

        pitchc = str(pitch) if pitch < 0 else "+" + str(pitch)

        factors = list(
            set(_semitone(factor) * _cent(factor) if _semicent(factor) else float(factor) for factor in pitchc.split(',')))

        channels = x.shape[-1] if x.ndim > 1 else 1
        x = x[:, None] if channels == 1 else x
        pitchshifter = StftPitchShift(self.framesize, self.hopsize, samplerate)
        y = np.stack([
            pitchshifter.shiftpitch(x[:, channel], factors, self.quefrency, self.distortion, self.normalization)
            for channel in range(channels)
        ], axis=-1)
        return y


def process_audio(audio: np.ndarray, samplerate: int, pitch: int) -> np.ndarray:
    return _PitchProcessor().process_audio_batch(audio, samplerate, pitch)
