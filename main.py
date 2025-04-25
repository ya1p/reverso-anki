import os
import json
from bs4 import BeautifulSoup
from reverso_anki import make_voices

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def process_html_file(file_path, with_voices, language_code):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    new_cards = []
    words = soup.find_all("app-favourite-item-new")

    def find_word_index(word):
        for i, card in enumerate(new_cards):
            if str(word) == card["word"]:
                return i
        return -1

    for row in words:
        word = row.find('a')
        word_translation = row.find('div', attrs={"class": ["favourite-item-new__translate", "favourite-item-new__translate_expanded"]})
        sentence = row.find('span', attrs={"style": "direction: ltr; line-height: 20px; font-size: 14px;"})
        sentence_translation = row.find("span", attrs={"class": "favourite-item-new__example-target-text"})

        if word and word_translation and sentence and sentence_translation:
            word = word.text.strip()
            word_translation = word_translation.text.strip()
            sentence = sentence.text
            sentence_translation = sentence_translation.text
            index = find_word_index(word)
            if index != -1:
                if str(word_translation) not in new_cards[index]["word_translations"]:
                    new_cards[index]["word_translations"].append(str(word_translation))
                new_cards[index]["sentences"].append(str(sentence))
                new_cards[index]["sentence_translations"].append(str(sentence_translation))
                if with_voices:
                    new_cards[index]["audio"].append(f"{word}{len(new_cards[index]['audio']) + 1}")
            else:
                new_cards.append({
                    "word": str(word),
                    "word_translations": [str(word_translation)],
                    "sentences": [str(sentence)],
                    "sentence_translations": [str(sentence_translation)],
                    **({"audio": [f"{word}1"]} if with_voices else {})
                })

    if with_voices:
        for card in new_cards:
            make_voices(card["sentences"], card["word"])

    return new_cards

def save_cards_custom_format(cards, filename, audio_format, with_voices):
    with open(filename, "w", encoding="utf-8") as f:
        for card in cards:
            word = card["word"]
            word_translations = "||".join(card["word_translations"])
            sentences = "||".join(card["sentences"])
            sentence_translations = "||".join(card["sentence_translations"])
            audio = "||".join(f"{a}.{audio_format}" for a in card.get("audio", []))
            line = f"{word};{word_translations};{sentences};{sentence_translations};{audio}" if with_voices else f"{word};{word_translations};{sentences};{sentence_translations}"
            f.write(line + "\n")

    print(f"✅ All cards are saved to a file: {filename}")

def process_all_files_in_folder(folder_path, with_voices, language_code, output_file, audio_format):
    all_new_cards = []

    if not os.path.isdir(folder_path):
        print(f'❌ There is no "{folder_path}" directory, please run "get_htmls.py" file first')
        return
    if not any(fname.endswith(".html") for fname in os.listdir(folder_path)):
        print(f'❌ Directory "{folder_path}" is empty or contains no .html files')
        return

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".html"):
            file_path = os.path.join(folder_path, file_name)
            print(f"🔄 Processing file: {file_path}")
            new_cards = process_html_file(file_path, with_voices, language_code)
            all_new_cards.extend(new_cards)

    save_cards_custom_format(all_new_cards, output_file, audio_format, with_voices)

if __name__ == "__main__":
    config = load_config()
    with_voices = config.get("generate_voices", False)
    language_code = config.get("language_code", "en")
    folder_path = config.get("html_folder_path", "favorites_htmls")
    output_file = config.get("output_cards_file", "output.txt")
    audio_format = config.get("audio_format", "mp3") 

    process_all_files_in_folder(folder_path, with_voices, language_code, output_file, audio_format)
