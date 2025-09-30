# My Clippings Splitter

A Python GUI tool to process Kindle’s `My Clippings.txt`.
It splits highlights and “new words” by book and language, removes duplicates, and exports the results into clean text/markdown files.

## ✨ Features

* Extract highlights per book (`.md` files).
* Detects the main language of each book (Italian, English, French, German).
* Creates `newwords` lists per language (max 100 items per file).
* Optionally creates global `newwords` files (without language distinction).
* Deduplicates highlights and words.
* Simple Tkinter GUI, no command-line required.

## 🚀 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/my-clippings-splitter.git
   cd my-clippings-splitter
   ```
2. Install requirements (Python ≥ 3.8 recommended):

   ```bash
   pip install langid
   ```

   *(Tkinter is included in most Python distributions, but if missing, install it via your OS package manager.)*

## 🖥️ Usage

1. Export your Kindle `My Clippings.txt` to your computer.

2. Run the script:

   ```bash
   python 6dbfc2cf-4011-40b5-9d4d-aa4eba7bb2c8.py
   ```

3. In the GUI:

   * Select the `My Clippings.txt` file.
   * Choose an output folder.
   * Pick the processing options (highlights, newwords per language, etc.).
   * Click **Elabora Clippings**.

4. The processed files will be saved in the chosen folder.

## 📂 Output Examples

* `Book_Title_Highlights.md` → all highlights from that book.
* `newwords_eng_1.txt` → first 100 English new words.
* `newwords_ita_1.txt` → first 100 Italian new words.
* `newwords_1.txt` → combined list (if global option selected).

## ⚠️ Notes

* Only supports **Italian (ITA), English (ENG), French (FRA), German (DEU)**.
* Each `newwords` file is limited to 100 entries for readability.
* Language detection uses [langid](https://github.com/saffsd/langid.py).

## 📜 License

MIT License – feel free to use and adapt.
