import librosa
import mido
from mido import MidiFile, MidiTrack, Message
import numpy as np

def convert_wav_to_midi(input_filename, output_filename, bpm):
    # Load the WAV file with the original sampling rate
    y, sr = librosa.load(input_filename, sr=None)

    # Estimate pitches using the Constant-Q chromagram
    chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)

    # Find the most dominant pitch in each frame
    dominant_pitches = np.argmax(chromagram, axis=0)
    midi_notes = dominant_pitches + 21  # Shift pitches to MIDI note numbers (A0 is MIDI note 21)

    # Estimate dynamics: MIDI velocity and note duration based on average RMS
    rms = librosa.feature.rms(y=y)[0]
    avg_rms = np.mean(rms)
    velocity = int(127 * avg_rms)  # Scale the average RMS to MIDI velocity range (0-127)
    note_duration = 0.5 * (avg_rms / np.max(rms))  # Adjust note duration based on dynamics

    # Create MIDI messages with the calculated velocity and note duration
    midi_messages = []
    for note in midi_notes:
        note_on = Message('note_on', note=note, velocity=velocity, time=0)
        note_off = Message('note_off', note=note, velocity=0, time=int(bpm * note_duration * 60))
        midi_messages.extend([note_on, note_off])

    # Create and save the MIDI file
    output_midi = MidiFile()
    track = MidiTrack()
    output_midi.tracks.append(track)
    for msg in midi_messages:
        track.append(msg)
    output_midi.save(output_filename)

if __name__ == "__main__":
    input_filename = 'MusicTest/FrankSinatra.wav'
    output_filename = 'output.mid'
    bpm = 120
    convert_wav_to_midi(input_filename, output_filename, bpm)
