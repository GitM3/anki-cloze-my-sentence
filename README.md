```markdown
# Cloze Mask Auto-Fill for Anki

Automatically generate a **contextual cloze-style mask** inside a sentence by
replacing a target word with a configurable placeholder (default: `◼◼◼`).

This add-on is designed for Japanese learners (or any language learners) who
want to train _contextual recall_ rather than isolated vocabulary memorization.\
It integrates into your existing note types and workflow, requires no special
models, and works with both new notes and bulk updates.

---

## ✨ Features

- **Automatically mask a target word** inside a sentence using any placeholder
  (default: `◼◼◼`).
- **Three configurable fields**:
  - Sentence field (input)
  - Word field (input)
  - Destination clozed field (output)
- **Optional note type filtering**
- **Automatic generation on field defocus** (Add/Edit window)
- **Bulk processing** from the Browser
- **Settings dialog** under Tools → _Cloze Mask Options…_
- Fully compatible with:
  - Custom note types
  - Yomitan / Migaku-style vocab mining workflows
  - Plugins that auto-generate example sentences
- Clean, modern code using Anki's current API (`update_note()`).

---

## 🔧 Installation

1. Create a directory inside your Anki `addons21` folder, for example:
```

addons21/cloze-mask-autofill/

```
2. Place `__init__.py` (this add-on's main file) inside the folder.

3. Restart Anki.

---

## ⚙️ Configuration

Open:

**Tools → Cloze Mask Options…**

You can configure:

| Setting | Description |
|--------|-------------|
| **Sentence field** | Field containing the full original sentence |
| **Word field** | Field containing the target word to be masked |
| **Destination field** | Field where the clozed/masked sentence will be written |
| **Mask string** | What to replace the target word with (default: `◼◼◼`) |
| **Note type filter** | Only apply to note types whose name contains these strings |
| **Generate on field exit** | Auto-create mask when leaving the sentence or word field |
| **Debug logging** | Print detailed steps to the console |

---

## 🖥️ Usage

### **Automatic mode**
While adding or editing a note:
- Fill in the *sentence field* and *word field*.
- As soon as you leave either field, the add-on generates the masked version and writes it to your output field.

### **Bulk mode**
In the Browser:
1. Select any number of notes  
2. Go to **Edit → Generate Cloze Masks**  
3. The add-on updates all selected notes automatically

---

## 🧠 Example

- Sentence:  
`これはペンですか？`

- Word:  
`ペン`

- Mask:  
`◼◼◼`

- Output:  
`これは◼◼◼ですか？`

---

## 🛠 Development Notes

- Uses `mw.col.update_note()` instead of deprecated `note.flush()`
- Safe for unsaved notes (checks for `note.id`)
- Word replacement is simple `sentence.find(word)` for now—expandable to:
- multi-occurrence replacement
- fuzzy/inflected matching
- regex-based replacement

Open an issue or PR if you'd like to extend functionality.

---

## 📄 License

MIT License  
Copyright © 2025

---

## ❤️ Acknowledgements

This add-on was developed as part of a custom Japanese-learning workflow integrating:
- Contextual vocabulary recall
- Multi-sentence exposure
- Personal example-sentence generation pipelines

Inspired by the structure and design of the author's **Kanji Constituent Auto-Fill** add-on.

---
```
