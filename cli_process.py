import argparse
from pathlib import Path

from autotuner import process


def main() -> None:
    parser = argparse.ArgumentParser(description='Read the README for more information.')

    parser.add_argument('input', type=str, help='Input audio path (wav, mp3, ogg, flac)')
    parser.add_argument('midi', type=str, help='MIDI string')
    parser.add_argument('output', type=str, help='Output audio to this path (wav, mp3, ogg, flac)')
    parser.add_argument('pitch', type=int, help='Base pitch')

    args = parser.parse_args()

    process(Path(args.input), Path(args.midi), int(args.pitch), Path(args.output))


if __name__ == '__main__':
    main()
