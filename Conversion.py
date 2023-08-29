import librosa
import mido

# Load the audio file
audio_file = 'MusicTest/FrankSinatra.wav'
y, sr = librosa.load(audio_file)

# Estimate note onsets and pitches
onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

# Create MIDI messages
output_midi = mido.MidiFile()

# Add a new MIDI track
track = mido.MidiTrack()
output_midi.tracks.append(track)

# Set the tempo in microseconds per beat (500000 microseconds per beat = 120 BPM)
tempo = mido.bpm2tempo(120)
track.append(mido.MetaMessage('set_tempo', tempo=tempo))

# Store active notes
active_notes = set()

# Add note events
for frame in onset_frames:
    new_notes = set()
    for pitch_idx in range(pitches.shape[0]):
        frequency = pitches[pitch_idx, frame]
        if frequency > 0:
            note_number = int(round(librosa.hz_to_midi(frequency)))
            if 0 <= note_number <= 127:
                new_notes.add(note_number)

    # Find notes that need to be turned off
    notes_to_turn_off = active_notes - new_notes

    # Turn off notes that are no longer active
    for note_number in notes_to_turn_off:
        note_off = mido.Message('note_off', note=note_number, velocity=64, time=0)
        track.append(note_off)
        active_notes.remove(note_number)

    # Turn on new notes and add them to active_notes
    for note_number in new_notes:
        if note_number not in active_notes:
            note_on = mido.Message('note_on', note=note_number, velocity=64, time=0)
            track.append(note_on)
            active_notes.add(note_number)

    # Calculate the time_advance
    frame_duration_ms = 0.01
    time_advance = int(sr * frame_duration_ms)

    for note_number in active_notes:
        note_off = mido.Message('note_off', note=note_number, velocity=64, time=time_advance)
        track.append(note_off)

# Save the MIDI file
output_midi.save('Frank.mid')