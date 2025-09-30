#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My Clippings Splitter (versione completa)
- Divide My Clippings.txt in highlights per libro e newwords per lingua
- Determina la lingua principale di ciascun libro
- Produce file newwords per lingua (max 100 voci)
- Opzione aggiuntiva: serie di file newwords "tutti insieme" senza distinzione lingua (max 100 voci ciascuno)
"""

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import langid

# Limitare langid alle lingue di interesse
try:
    langid.set_languages(['it', 'en', 'fr', 'de'])
except Exception:
    pass

STOPWORDS = {
    'it': {"di","e","il","la","che","a","un","una","per","è","in","non","con","su","del","al",
           "si","se","le","gli","ho","mi","ma","anche","come","da","delle","degli","sul","tra",
           "poi","ancora","qui","lui","lei","noi","voi","o","dal","dalla","sulle","così"},
    'en': {"the","be","to","of","and","a","in","that","have","i","it","for","not","on","with",
           "he","as","you","do","at","this","but","his","by","from","they","we","say","her",
           "she","or","an","will","my","one","all","would","there","their","what","so","up"},
    'fr': {"le","la","les","de","un","une","à","et","en","que","qui","pas","pour","sur","dans",
           "est","au","aux","ce","il","elle","nous","vous","ne","se","mais","plus","comme",
           "par","avec","son","sa","ses","leur","leurs"},
    'de': {"der","die","das","und","zu","den","von","mit","nicht","ist","es","ein","im","auf",
           "für","an","als","auch","dass","wie","hat","ich","sie","er","oder","aus","bei",
           "wir","was","sein","nach","bei"}
}

ACCENTS = {
    'it': set("àèéìíòóùúÀÈÉÌÍÒÓÙÚ"),
    'fr': set("àâçéèêëîïôûùüÿœæÀÂÇÉÈÊËÎÏÔÛÙÜŸŒÆ"),
    'de': set("äöüÄÖÜß")
}

LANG_MAP = {'it': 'ita', 'en': 'eng', 'fr': 'fra', 'de': 'deu'}

class MyClippingsSplitter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("My Clippings Splitter")
        self.root.geometry("720x620")

        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()

        self.options = {
            "highlights": tk.BooleanVar(value=False),
            "ita": tk.BooleanVar(value=False),
            "eng": tk.BooleanVar(value=False),
            "fra": tk.BooleanVar(value=False),
            "deu": tk.BooleanVar(value=False),
            "newwords_unico": tk.BooleanVar(value=False),  # nuova opzione
            "all": tk.BooleanVar(value=True)
        }

        self.setup_ui()

    def setup_ui(self):
        title_label = tk.Label(self.root, text="My Clippings Splitter",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        desc_label = tk.Label(self.root,
                              text="Divide My Clippings.txt: highlights per libro e newwords per lingua (ITA/ENG/FRA/DEU)",
                              font=("Arial", 10))
        desc_label.pack(pady=(0,12))

        # File input
        file_frame = tk.Frame(self.root)
        file_frame.pack(fill="x", padx=20, pady=8)
        tk.Label(file_frame, text="File My Clippings.txt:", font=("Arial", 10, "bold")).pack(anchor="w")
        file_select_frame = tk.Frame(file_frame)
        file_select_frame.pack(fill="x", pady=5)
        self.file_entry = tk.Entry(file_select_frame, textvariable=self.input_file, state="readonly")
        self.file_entry.pack(side="left", fill="x", expand=True)
        tk.Button(file_select_frame, text="Sfoglia...", command=self.select_input_file).pack(side="right", padx=(5,0))

        # Cartella output
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(fill="x", padx=20, pady=8)
        tk.Label(dir_frame, text="Cartella di destinazione:", font=("Arial", 10, "bold")).pack(anchor="w")
        dir_select_frame = tk.Frame(dir_frame)
        dir_select_frame.pack(fill="x", pady=5)
        self.dir_entry = tk.Entry(dir_select_frame, textvariable=self.output_dir, state="readonly")
        self.dir_entry.pack(side="left", fill="x", expand=True)
        tk.Button(dir_select_frame, text="Sfoglia...", command=self.select_output_dir).pack(side="right", padx=(5,0))

        # Opzioni
        options_frame = tk.LabelFrame(self.root, text="Opzioni di elaborazione", font=("Arial", 10, "bold"))
        options_frame.pack(fill="x", padx=20, pady=12)
        tk.Checkbutton(options_frame, text="Highlights", variable=self.options["highlights"]).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Newwords ITA", variable=self.options["ita"]).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Newwords ENG", variable=self.options["eng"]).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Newwords FRA", variable=self.options["fra"]).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Newwords DEU", variable=self.options["deu"]).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Newwords senza distinzione di lingua",
                       variable=self.options["newwords_unico"]).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Tutto (attiva tutte le opzioni)",
                       variable=self.options["all"], command=self.toggle_all).pack(anchor="w", pady=(6,0))

        # Pulsante
        self.process_button = tk.Button(self.root, text="Elabora Clippings",
                                        command=self.process_clippings,
                                        font=("Arial", 12, "bold"),
                                        bg="#4CAF50", fg="white",
                                        state="disabled")
        self.process_button.pack(pady=16)

        # Log
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill="both", expand=True, padx=20, pady=8)
        tk.Label(log_frame, text="Log:", font=("Arial", 10, "bold")).pack(anchor="w")
        text_frame = tk.Frame(log_frame)
        text_frame.pack(fill="both", expand=True)
        self.log_text = tk.Text(text_frame, height=12, state="disabled")
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.input_file.trace("w", self.check_ready)
        self.output_dir.trace("w", self.check_ready)

    def toggle_all(self):
        all_selected = self.options["all"].get()
        for key in ["highlights","ita","eng","fra","deu","newwords_unico"]:
            self.options[key].set(all_selected)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message+"\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update()

    def select_input_file(self):
        file_path = filedialog.askopenfilename(title="Seleziona My Clippings.txt",
                                               filetypes=[("File di testo","*.txt"),("Tutti i file","*.*")])
        if file_path: self.input_file.set(file_path)

    def select_output_dir(self):
        dir_path = filedialog.askdirectory(title="Seleziona cartella di destinazione")
        if dir_path: self.output_dir.set(dir_path)

    def check_ready(self,*args):
        if self.input_file.get() and self.output_dir.get():
            self.process_button.config(state="normal")
        else:
            self.process_button.config(state="disabled")

    # ---------- funzioni lingua e dedup ----------
    def _tokenize_words(self,text):
        tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+",text)
        return [t.lower() for t in tokens if t.strip()]

    def _stopword_fraction(self,text,lang_code):
        words = self._tokenize_words(text)
        if not words: return 0.0
        sw = STOPWORDS.get(lang_code,set())
        count = sum(1 for w in words if w in sw)
        return count / len(words)

    def _has_accent_for_lang(self,text,lang_code):
        if lang_code not in ACCENTS: return 0
        accent_set = ACCENTS[lang_code]
        return 1 if any(c in accent_set for c in text) else 0

    def determine_language_for_book(self,book_title,highlights):
        candidate_texts=[]
        if book_title.strip(): candidate_texts.append(('title',book_title.strip()))
        for h in highlights:
            txt = h.get('text','')
            wc = len(self._tokenize_words(txt))
            if wc>=3: candidate_texts.append(('highlight',txt))
        if not candidate_texts: return None

        scores={'it':0.0,'en':0.0,'fr':0.0,'de':0.0}
        for kind,txt in candidate_texts:
            words = self._tokenize_words(txt)
            wc = max(1,len(words))
            text_weight = 1.0 if kind=='title' else min(3.0,wc/4.0)
            try:
                lid,_ = langid.classify(txt)
            except: lid=None
            for lang in ('it','en','fr','de'):
                stop_frac=self._stopword_fraction(txt,lang)
                accent_flag=self._has_accent_for_lang(txt,lang)
                lid_match=1.0 if lid==lang else 0.0
                text_lang_score = stop_frac*0.7 + lid_match*0.25 + accent_flag*0.05
                scores[lang]+= text_lang_score*text_weight
        total=sum(scores.values())
        if total<=0: return None
        best_lang,best_score = max(scores.items(), key=lambda kv:kv[1])
        if best_score/total>=0.4 or best_score>=1.5: return best_lang
        return None

    def remove_duplicate_newwords(self,all_newwords):
        seen=set()
        unique=[]
        for wd in all_newwords:
            normalized=' '.join(self._tokenize_words(wd.get('text','')))
            if not normalized: continue
            if normalized not in seen:
                seen.add(normalized)
                unique.append(wd)
        return unique

    def remove_similar_highlights(self,highlights):
        if len(highlights)<=1: return highlights
        filtered=[]
        for current in highlights:
            curr_words = set(self._tokenize_words(current['text']))
            is_dup=False
            for i,exist in enumerate(filtered):
                exist_words=set(self._tokenize_words(exist['text']))
                union = curr_words.union(exist_words)
                if not union: continue
                if len(curr_words.intersection(exist_words))/len(union)>=0.8:
                    is_dup=True
                    if len(current['text'])>len(exist['text']):
                        filtered[i]=current
                    break
            if not is_dup: filtered.append(current)
        return filtered

    # ---------- scrittura file ----------
    def write_newwords_from_buckets(self,buckets,output_dir,selected_langs):
        files_created=0
        words_per_file=100
        prefix_map={'ita':'newwords_ita','eng':'newwords_eng','fra':'newwords_fra','deu':'newwords_deu'}
        for key in selected_langs:
            words=buckets.get(key,[])
            if not words: continue
            prefix = prefix_map.get(key,f'newwords_{key}')
            total = len(words)
            for i in range(0,total,words_per_file):
                file_num=(i//words_per_file)+1
                filename=f'{prefix}_{file_num}.txt'
                filepath=os.path.join(output_dir,filename)
                slice_words=words[i:i+words_per_file]
                with open(filepath,'w',encoding='utf-8') as f:
                    for j,wd in enumerate(slice_words,start=1):
                        idx=i+j
                        f.write(f'[{idx}] {wd["text"]}\n')
                files_created+=1
                self.log(f"Creato {filename} con {len(slice_words)} voci")
        return files_created

    # ---------- pipeline principale ----------
    def process_clippings(self):
        input_file=self.input_file.get()
        output_dir=self.output_dir.get()
        if not input_file or not output_dir:
            messagebox.showerror("Errore","Seleziona sia il file che la cartella di destinazione")
            return
        if not os.path.exists(input_file):
            messagebox.showerror("Errore","Il file selezionato non esiste")
            return
        if not os.path.exists(output_dir):
            messagebox.showerror("Errore","La cartella di destinazione non esiste")
            return

        try:
            self.log("Inizio elaborazione...")
            self.process_button.config(state="disabled")

            # Lettura file
            try:
                with open(input_file,'r',encoding='utf-8-sig') as f:
                    content=f.read()
                self.log("File letto con encoding UTF-8")
            except UnicodeDecodeError:
                with open(input_file,'r',encoding='latin1') as f:
                    content=f.read()
                self.log("File letto con encoding Latin1")

            entries=content.split('==========')
            book_data={}
            all_newwords=[]
            total_clips=0
            skipped=0
            self.log(f"Trovate {len(entries)} sezioni da elaborare...")

            for entry in entries:
                entry=entry.strip()
                if not entry: continue
                lines=[line.rstrip() for line in entry.split('\n') if line.strip()]
                if len(lines)<3: skipped+=1; continue
                book_title=lines[0].strip()
                if not book_title: skipped+=1; continue
                position_info=lines[1].strip() if len(lines)>=2 else ""
                clip_text='\n'.join(lines[2:]).strip()
                if not clip_text: skipped+=1; continue
                wc=len(self._tokenize_words(clip_text))
                if wc>=4:
                    if book_title not in book_data: book_data[book_title]={'highlights':[]}
                    book_data[book_title]['highlights'].append({'text':clip_text,'position':position_info})
                else:
                    all_newwords.append({'text':clip_text,'position':position_info,'book_title':book_title})
                total_clips+=1

            self.log(f"Elaborati {total_clips} clippings, saltati {skipped}")
            self.log(f"Libri con highlights lunghi: {len(book_data)}")
            self.log(f"Newwords raccolte: {len(all_newwords)}")

            # dedup newwords
            before=len(all_newwords)
            all_newwords=self.remove_duplicate_newwords(all_newwords)
            removed=before-len(all_newwords)
            if removed: self.log(f"Rimosse {removed} newwords duplicate")

            # dedup highlights
            dup_h_removed=0
            for b in list(book_data.keys()):
                orig=len(book_data[b]['highlights'])
                book_data[b]['highlights']=self.remove_similar_highlights(book_data[b]['highlights'])
                dup_h_removed+=(orig-len(book_data[b]['highlights']))
            if dup_h_removed: self.log(f"Rimossi {dup_h_removed} highlight duplicati/simili")

            # lingua libri
            book_lang_map={}
            for book_title,data in book_data.items():
                lang=self.determine_language_for_book(book_title,data.get('highlights',[]))
                book_lang_map[book_title]=lang
                self.log(f"Libro: '{book_title[:60]}' -> lingua stimata: {lang if lang else 'non determinata'}")

            # buckets per lingua
            buckets={'ita':[],'eng':[],'fra':[],'deu':[]}
            fallback_count=0
            for wd in all_newwords:
                bt=wd.get('book_title')
                assigned=None
                if bt and bt in book_lang_map and book_lang_map[bt]:
                    assigned=LANG_MAP.get(book_lang_map[bt],None)
                if not assigned:
                    try:
                        lc,_=langid.classify(wd['text'])
                        assigned=LANG_MAP.get(lc,'eng')
                    except Exception:
                        assigned='eng'
                    fallback_count+=1
                if assigned not in buckets: assigned='eng'
                buckets[assigned].append(wd)

            self.log(f"Newwords assegnate per lingua: ita={len(buckets['ita'])}, eng={len(buckets['eng'])}, fra={len(buckets['fra'])}, deu={len(buckets['deu'])} (fallback: {fallback_count})")

            # highlights per libro
            files_written=0
            if self.options["highlights"].get() or self.options["all"].get():
                for book_title,data in book_data.items():
                    if data.get('highlights'):
                        safe_title=re.sub(r'[<>:"/\\|?*]','',book_title)
                        safe_title=re.sub(r'\s+','_',safe_title.strip())[:60]
                        filename=f'{safe_title}_highlights.md'
                        filepath=os.path.join(output_dir,filename)
                        with open(filepath,'w',encoding='utf-8') as f:
                            for clip in data['highlights']:
                                f.write(f'> {clip["text"]}\n\n')
                                if clip.get('position'): f.write(f'*{clip["position"]}*\n\n')
                                f.write('---\n\n')
                        files_written+=1
                        self.log(f"Creato file highlights: {filename}")

            # lingue da scrivere
            if self.options["all"].get():
                selected_langs=['ita','eng','fra','deu']
            else:
                selected_langs=[]
                for k in ["ita","eng","fra","deu"]:
                    if self.options[k].get(): selected_langs.append(k)

            # scrivi per lingua
            newword_files=self.write_newwords_from_buckets(buckets,output_dir,selected_langs)
            files_written+=newword_files

            # scrivi newwords uniche (serie di file da 100 voci)
            if self.options["newwords_unico"].get():
                words_per_file=100
                total=len(all_newwords)
                for i in range(0,total,words_per_file):
                    file_num=(i//words_per_file)+1
                    filename=f'newwords_{file_num}.txt'
                    filepath=os.path.join(output_dir,filename)
                    slice_words=all_newwords[i:i+words_per_file]
                    with open(filepath,'w',encoding='utf-8') as f:
                        for j,wd in enumerate(slice_words,start=1):
                            idx=i+j
                            f.write(f'[{idx}] {wd["text"]}\n')
                    files_written+=1
                    self.log(f"Creato file newwords serie: {filename} ({len(slice_words)} voci)")

            # riepilogo
            self.log("="*70)
            self.log("ELABORAZIONE COMPLETATA!")
            self.log(f"• Clippings processati: {total_clips}")
            self.log(f"• Newwords finali: {len(all_newwords)}")
            self.log(f"• File creati: {files_written}")
            self.log(f"• Cartella di destinazione: {output_dir}")
            self.log("="*70)

            messagebox.showinfo("Completato!",
                                f"Elaborazione completata!\n\nClippings processati: {total_clips}\nNewwords finali: {len(all_newwords)}\nFile totali creati: {files_written}\n\nI file sono stati salvati in:\n{output_dir}")

        except Exception as e:
            self.log(f"ERRORE: {str(e)}")
            messagebox.showerror("Errore", f"Si è verificato un errore:\n{str(e)}")
        finally:
            self.process_button.config(state="normal")

    def run(self):
        self.root.mainloop()


if __name__=="__main__":
    app=MyClippingsSplitter()
    app.run()
