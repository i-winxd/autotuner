import argparse
from pathlib import Path

from autotuner import process


def main() -> None:
    import multiprocessing
    multiprocessing.freeze_support()
    parser = argparse.ArgumentParser(description='Autotuner. Input audio is at a constant pitch. Input MIDI has a track named target, where the input audio is tuned to. Read the README for more information.')

    parser.add_argument('input', type=str, help='Input audio path (wav, mp3, ogg, flac)')
    parser.add_argument('midi', type=str, help='Path to input MIDI')
    parser.add_argument('output', type=str, help='Output audio to this path (wav, mp3, ogg, flac)')
    parser.add_argument('pitch', type=int, help='Base pitch of input audio (NEGATIVE of pitch offset - what you hear 0=C5,1=C#5,2=D5,3=D#5,4=E,5=F,6=F#)')
    parser.add_argument('--track', default="target", type=str, help="Name of the track to analyze (default: target)")

    args = parser.parse_args()
    process(Path(args.input), Path(args.midi), int(args.pitch), Path(args.output), str(args.track))


if __name__ == '__main__':
    main()
