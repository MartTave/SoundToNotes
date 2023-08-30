import librosa
import mido

# Charger le fichier audio
fichier_audio = 'MusicTest/c5.mp3'
y, sr = librosa.load(fichier_audio)
y = librosa.to_mono(y)

# Estimer les débuts de notes et les hauteurs de notes
onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units="time")
pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.5)
# Créer des messages MIDI
sortie_midi = mido.MidiFile()

# Ajouter une nouvelle piste MIDI
piste = mido.MidiTrack()
sortie_midi.tracks.append(piste)

# Définir le tempo en microsecondes par temps (500000 microsecondes par temps = 120 BPM)
tempo = mido.bpm2tempo(120)
piste.append(mido.MetaMessage('set_tempo', tempo=tempo))


# Stocker les notes actives
notes_actives = set()

# Ajouter les événements de notes
for frame in onset_frames:
    nouvelles_notes = set()
    for indice_hauteur in range(pitches.shape[0]):
        frequence = pitches[indice_hauteur, frame]
        if frequence > 0:
            numero_note = int(round(librosa.hz_to_midi(frequence)))
            nouvelles_notes.add(numero_note)

    # Trouver les notes à enlever
    notes_a_eteindre = notes_actives - nouvelles_notes

    # enlever les notes qui ne sont plus actives
    for numero_note in notes_a_eteindre:
        #note_off = mido.Message('note_off', note=numero_note, velocity=64, time=0)
        #piste.append(note_off)
        notes_actives.remove(numero_note)

    # ajouter les nouvelles notes et les ajouter à notes_actives
    for numero_note in nouvelles_notes:
        if numero_note not in notes_actives:
            print(numero_note)
            note_on = mido.Message('note_on', note=numero_note, velocity=64, time=0)
            piste.append(note_on)
            notes_actives.add(numero_note)

    # Calculer l'avance_temporelle
    duree_trame_ms = 0.01
    avance_temporelle = int(sr * duree_trame_ms)

    for numero_note in notes_actives:
        note_off = mido.Message('note_off', note=numero_note, velocity=64, time=0)
        piste.append(note_off)

# Enregistrer le fichier MIDI
sortie_midi.save('./c5.mid')
