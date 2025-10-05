# Audio Files Directory

Ten folder przechowuje wygenerowane pliki audio dla scenariuszy snów.

## Struktura plików:
- `dream_tts_[timestamp].mp3` - Pliki TTS z polskim tekstem pomagającym w świadomym śnieniu
- `dream_sound_[timestamp].mp3` - Pliki z ambient/relaksacyjną muzyką dopasowaną do scenariusza

## Automatyczne czyszczenie:
Pliki są automatycznie generowane przez API i mogą być usuwane po pewnym czasie.

## Docker Volume:
Ten folder jest zamontowany jako volume w Docker kontenerze w `/app/audio_files`

## Uwagi:
- Pliki są ignorowane przez Git (zobacz .gitignore)
- Upewnij się że aplikacja ma uprawnienia do zapisu w tym folderze