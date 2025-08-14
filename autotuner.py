# the pydub version of this, which has to be a lot more stable
import io
import math
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path
from typing import Optional

import mido
from pydub import AudioSegment

from audio_batch_processor import process_audio
from midi_processing import midi_to_representation, MidiRepresentation, Track, TempoChange
from stft_io import read, write


def beat_to_s(beat: float, tcs: list[TempoChange]) -> float:
    tcs = sorted(tcs, key=lambda s: s.beat)
    bpm = 120.0  # current bpm
    cur_time = 0.0  # time since the last tempo change
    last_tc = 0.0  # beat of the last tempo change

    # 120 -> 120 @ 0, cur_time = 0
    # 120 -> 240 @ 1, cur_time = 0.5, last_tc = 1, bpm = 120
    # @ 3, 0.5 + 0.25 * (2) = 0.5 + 0.5 = 1
    for tc in tcs:
        if tc.beat < beat:
            last_tc = tc.beat
            cur_time += (60 / bpm) * (tc.beat - last_tc)
            bpm = tc.new_bpm
        else:
            break
    return cur_time + (60 / bpm) * (beat - last_tc)


@dataclass
class ASG:
    b: int
    e: int
    pitch_delta: int


@dataclass
class ASGW:
    asg: ASG
    sound: AudioSegment


def apply_pitch(asg_w_list: list[ASGW]) -> list[ASGW]:
    # return [shift_pitch(asgw) for asgw in asg_w_list]
    print("Mapping")
    with Pool() as pool:
        f_as = pool.map(shift_pitch, asg_w_list)
    return f_as


def shift_pitch(asgw: ASGW) -> ASGW:
    buffer = io.BytesIO()
    asgw.sound.export(buffer, format="wav")
    buffer.seek(0)
    x, samplerate = read(buffer)
    y = process_audio(x, samplerate, asgw.asg.pitch_delta)

    output_buffer = io.BytesIO()
    write(output_buffer, y, samplerate)
    output_buffer.seek(0)
    return ASGW(asgw.asg, AudioSegment.from_file(output_buffer, format="wav"))


# TG_TRACK = "target"


def poly_slicer(midi_data: MidiRepresentation, pitch_offset: int, target_track: str) -> list[ASG]:
    midi_rep = midi_data
    first_valid_track: Optional[Track] = next((item for item in midi_rep.tracks.values() if item.track_name == target_track), None)
    if first_valid_track is None:
        raise ValueError(f"No track named {target_track}")

    track_notes = sorted(first_valid_track.notes, key=lambda n: n.beat)
    audio_segments: list[ASG] = []
    for note in track_notes:
        start_ms = round(beat_to_s(note.beat, midi_rep.bpm_changes) * 1000)
        end_ms = round(beat_to_s(note.beat + note.duration, midi_rep.bpm_changes) * 1000)
        audio_segments.append(ASG(max(start_ms, 0),
                                  end_ms + 40,
                                  note.note - 60 - pitch_offset))
    return audio_segments


def process_internal(sound: AudioSegment, midi_data: MidiRepresentation, pitch_offset: int, target_track: str) -> AudioSegment:
    # obtain the track named "target"
    first_valid_track = next((item for item in midi_data.tracks.values() if item.track_name == "target"), None)
    if first_valid_track is None:
        print("No track named target")
        return None

    audio_segments = poly_slicer(midi_data, pitch_offset, target_track)
    length_in_ms = math.floor(sound.duration_seconds * 1000)
    asg_w_list: list[ASGW] = [ASGW(seg, sound[seg.b:seg.e]) for seg in audio_segments]
    pitches_applied = apply_pitch(asg_w_list)

    new_canvas = AudioSegment.silent(length_in_ms + 1000)
    for seg in pitches_applied:
        new_canvas = new_canvas.overlay(seg.sound, position=seg.asg.b, loop=False)
    return new_canvas


def process(audio: Path, midi_file: Path, pitch: int, export_path: Path, target_track: str = "target") -> None:
    format_of = audio.suffix.removeprefix(".")
    af_formats = {"wav", "mp3", "ogg", "flac"}
    if format_of not in af_formats:
        raise ValueError(f"Audio format ({format_of}) not in wav, mp3, ogg, flac")
    exp_format = export_path.suffix.removeprefix(".")
    if exp_format not in af_formats:
        export_path = export_path.with_suffix(".wav")
    sound = AudioSegment.from_file(audio, format=format_of)
    midi_data = midi_to_representation(mido.MidiFile(midi_file.__str__()))
    ad = process_internal(sound, midi_data, pitch, target_track)
    ad.export(export_path.__str__(), format=exp_format)
