# AUTOTUNER

This repository is for reference only. I may not be able to provide 101 support.

Kerovee/Pitcher but not in FL Studio and it *might* sound better?

No pitch detection **so input audio must be at a constant pitch.** Otherwise, this is a
full-on autotuner with formant preservation. In Newtone, select all and CTRL+CLICK piano
note to tune all to a single pitch.

**This program has a UI, but there's a command-line version of this offered.**

Program parameters:

- Input audio is your input audio
- The input midi is the notes you want to tune it to, where all the notes must be in the track "target" (case-sensitive). In FL Studio, there is 1 track per MIDI out, the track name is what you actually named the MIDI out track.
- Pitch is the base pitch of your input audio. This is an offset, and it should be the pitch you are hearing, **distance
  from 60**
  - 60 is C5, 61 is C#5, and so on
  - if your input signal is C#5 set it to 1. B4, set it to -1.
- Output is where this program will export the tuned audio

Polyphonic note sequences (harmonies) are fine; rests means NO sound will play for the duration of the rest so remember to legato your notes!

## Installation

Get Python (3.10-3.12, idk if 3.13 breaks), pip install everything in `requirements.txt`.


Then:

### UI

Run `ui_process.py`

### CLI

```
usage: cli_process.py [-h] input midi output pitch

Read the README for more information.

positional arguments:
  input       Input audio path (wav, mp3, ogg, flac)
  midi        MIDI string
  output      Output audio to this path (wav, mp3, ogg, flac)
  pitch       Base pitch

options:
  -h, --help  show this help message and exit
```

## Performance

Depends. Usually performs better if Kerovee sucks, otherwise does worse. Never better than doing it yourself entirely in Newtone.
