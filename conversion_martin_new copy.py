import librosa
import mido

INPUT = "./MusicTest/Music_Audio.wav"
OUTPUT = "./results/test.mid"
ABS_TRESHOLD = 10
TRESHOLD = 0.5

data, sr = librosa.load(INPUT)
data = librosa.to_mono(data)
data = librosa.effects.trim(data)[0]
tempo = int(librosa.feature.tempo(y=data)[0])
tempo = 120
print("Tempo is : ", tempo)
# This indicate the number of frames to take into account to
# analyse 1 beat
framePerBeat = int(1 / (tempo / 60) * sr)


midiOut = mido.MidiFile(ticks_per_beat=10)

framePerTick = int(1 / (tempo * midiOut.ticks_per_beat / 60) * sr)


track = mido.MidiTrack()
track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))




nbrOfBeat = int((len(data) - (len(data) % framePerBeat)) / framePerBeat)

nbrOfTick = int((len(data) - (len(data) % framePerTick)) / framePerTick)

print(nbrOfBeat, nbrOfTick)

maxAmp = []

print("Song got", nbrOfBeat, " beats")

activeNotes = []

lastEventTick = 0

for t in range(0, nbrOfTick):
    # Current data should cover a beat in the song
    currentData = data[t*framePerTick:(t + 1) * framePerTick - 1]
    pitches, magnitudes = librosa.piptrack(y=currentData, sr=sr)
    notes = []
    maxMag = magnitudes.max()
    maxAmp.append(maxMag)
    for i in range(0, len(pitches)):
        for j in range(0, len(pitches[i])):
            if(pitches[i][j] != 0.0):
                if(magnitudes[i][j] < ABS_TRESHOLD or magnitudes[i][j] < maxMag * TRESHOLD):
                    continue
                midiNote = round(librosa.hz_to_midi(pitches[i][j]))
                if notes.count(midiNote) == 0:
                    notes.append(midiNote)
    # Here we have all the notes in the time frame taken

    treatedNotes = []
    for n in notes:
        # This is here to keep track of what needs to be removed from active notes
        treatedNotes.append(n)
        if activeNotes.count(n) == 0:
            # We need to activate the note !
            activeNotes.append(n)
            currentTick = t
            tickDelta = currentTick - lastEventTick
            track.append(mido.Message("note_on", note=n, time=tickDelta))
            lastEventTick = currentTick
    for n in activeNotes:
        if treatedNotes.count(n) == 0:
            # This means that the note was not active anymore
            activeNotes.remove(n)
            currentTick = t
            tickDelta = currentTick - lastEventTick
            track.append(mido.Message("note_off", note=n, time=tickDelta))
            lastEventTick = currentTick

midiOut.tracks.append(track)
midiOut.save(OUTPUT)
print(maxAmp)