# Reverso-Anki 

Utility to save your favorites from reverso-context to a simple txt file for later use in anki

---

## Notes ⚠️

- When parsing all favorites, the program will remove each entry from the favorites list one by one for complete collection, since without premium you don't have access to more than 50 entries, please keep this in mind
- Currently only macOS is supported, other OS will be on the list in the future
- Repository is under development so expect bugs


---

## Getting started
```
git clone https://github.com/ya1p/reverso-anki
pip3 install -r requirements.txt
playwright install
```
After installation, configure the config.json
```
{
    "browser": "webkit",
    "headless_browser": false, 
    "html_folder_path": "favorites_htmls",
    "deleted_folder_path": "favorites_deleted", // after re-collecting favorites htmls of old favorites will be moved to this folder
    "output_cards_file": "output.txt", //  final txt file
    "voice_output_folder": "voices", //  where the audio will be stored only if generate_voices is true
    "generate_voices": false, //if the true will generate audio for the proposals
    "voice_name": null,
    "language_code": "en", // the language from which you translated to your native language, i.e. target language
    "rate": 160, // reading speed
    "audio_format": "mp3"
}
```
Now just run these two files, the first time you run get_htmls.py you will need to log in
```
python3 get_htmls.py
python3 main.py
```
