from dataclasses import dataclass, field
from pathlib import Path

from autotuner import process
from ui import DataclassUI


@dataclass
class UIProcess(DataclassUI):
    input: Path = field(metadata={
        'filetypes': [('Audio files', '*.wav *.mp3 *.ogg *.flac')]
    })
    midi: Path = field(metadata={
        'filetypes': [('MIDI files', '*.mid')]
    })
    output: Path = field(metadata={
        'filetypes': [('Audio files', '*.wav *.mp3 *.ogg *.flac')],
        'save': True
    })
    pitch: int = 0


if __name__ == '__main__':
    ui_args = UIProcess.get_instance_from_ui(
        title="Can I autotune, not",
        desc="Autotune anything. Remember to EQ stuff afterwards"
    )
    process(ui_args.input,
            ui_args.midi,
            ui_args.pitch,
            ui_args.output)
