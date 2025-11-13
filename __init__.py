from __future__ import annotations

"""
Anki add-on: Cloze Mask Auto-Fill
=================================

Automatically generates a "clozed" version of a sentence by replacing
a target word with a mask (e.g. ◼◼◼).

* Configurable sentence field, word field, and destination field
* Optional note-type filter
* Auto-fill on editing (field defocus)
* Bulk action in the Browser
* Options dialog (Tools ▸ Cloze Mask Options…)

Inspired by your Kanji Constituent Auto-Fill add-on.
"""

import json
from pathlib import Path
from typing import Dict, List

from anki.hooks import addHook
from aqt import mw
from aqt.qt import (QAction, QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
                    QLineEdit)
from aqt.utils import showInfo, tooltip

###############################################################################
# Configuration helpers
###############################################################################

ADDON_NAME = __name__
ADDON_DIR = Path(mw.addonManager.addonsFolder()) / ADDON_NAME
CFG_FILE = ADDON_DIR / "config.json"


def _defaults() -> Dict[str, object]:
    return {
        # Field with the full sentence
        "sentenceField": "Sentence",
        # Field with the target word to mask
        "wordField": "Reading",
        # Field where the clozed sentence is written
        "destinationField": "ClozeSentence",
        # Only process note types whose name contains any of these (comma-separated)
        "noteTypes": "",
        # Automatically generate when leaving sentence/word fields in the editor
        "lookupOnAdd": True,
        # Text to use as the mask (your choice: ◼◼◼)
        "maskString": "◼◼◼",
        # Label for the Browser bulk action
        "bulkActionLabel": "Generate Cloze Masks",
        # Debug logging
        "debug": False,
    }


def _load_cfg() -> Dict[str, object]:
    user = mw.addonManager.getConfig(ADDON_NAME) or {}
    return {**_defaults(), **user}


def _save_cfg(cfg: Dict[str, object]) -> None:
    mw.addonManager.writeConfig(ADDON_NAME, cfg)
    try:
        ADDON_DIR.mkdir(parents=True, exist_ok=True)
        CFG_FILE.write_text(json.dumps({"config": cfg}, ensure_ascii=False, indent=2))
    except Exception as e:
        print("[ClozeMask] couldn't write config.json:", e)


CFG: Dict[str, object] = _load_cfg()

###############################################################################
# Debug logging
###############################################################################

def log(*msg):
    if CFG.get("debug"):
        print("[ClozeMask]", *msg)

###############################################################################
# Core logic: populate one note
###############################################################################

def generate_cloze_sentence(sentence: str, word: str, mask: str) -> str | None:
    """Return sentence with first occurrence of word replaced by mask."""
    if not sentence or not word:
        return None

    idx = sentence.find(word)
    if idx == -1:
        return None

    # Replace only the first occurrence #TODO: More?
    before = sentence[:idx]
    after = sentence[idx + len(word):]
    return before + mask + after


def populate_cloze(note) -> bool:
    """
    Populate the destination field with a masked sentence, based on
    the configured sentenceField, wordField, destinationField.
    Returns True if note was modified.
    """
    nt_filter = [
        t.strip().lower()
        for t in str(CFG.get("noteTypes", "")).split(",")
        if t.strip()
    ]
    note_name = note.note_type()["name"].lower()

    if nt_filter and not any(t in note_name for t in nt_filter):
        log("Skip – note-type filtered:", note.note_type()["name"])
        return False

    sentence_field = CFG.get("sentenceField", "Sentence")
    word_field = CFG.get("wordField", "Reading")
    dest_field = CFG.get("destinationField", "ClozeSentence")
    mask = CFG.get("maskString", "◼◼◼")

    # Safety: fields must exist
    if sentence_field not in note or word_field not in note or dest_field not in note:
        log("Skip – missing sentence/word/destination field")
        return False

    # It's allowed that dest_field == sentence_field, but warn in debug
    if sentence_field == dest_field:
        log("Warning – destination field is same as sentence field")

    sentence = note[sentence_field].strip()
    word = note[word_field].strip()

    if not sentence or not word:
        log("Skip – empty sentence or word")
        return False

    clozed = generate_cloze_sentence(sentence, word, mask)
    if clozed is None:
        log("Skip – word not found in sentence:", word, "in", sentence)
        return False

    note[dest_field] = clozed
    log("Populated cloze:", clozed)
    return True

###############################################################################
# Hooks – automatic fill on field defocus
###############################################################################

def on_edit_focus(flag, note, field_idx):
    """
    Called when focus leaves a field in the editor.
    If lookupOnAdd is enabled, we try generating the cloze sentence when
    the user leaves either the sentence field or the word field.
    """
    if not CFG.get("lookupOnAdd", True):
        return flag

    col = mw.col
    model = note.note_type()
    field_names = col.models.field_names(model)

    try:
        sent_idx = field_names.index(CFG.get("sentenceField", "Sentence"))
    except ValueError:
        sent_idx = None

    try:
        word_idx = field_names.index(CFG.get("wordField", "Reading"))
    except ValueError:
        word_idx = None

    # If we just left either the sentence or the word field, try to populate
    if field_idx == sent_idx or field_idx == word_idx:
        log("Field defocus – trying note id", note.id)
        if populate_cloze(note):
            note.flush()

    return flag


if CFG.get("lookupOnAdd", True):
    addHook("editFocusLost", on_edit_focus)

###############################################################################
# Bulk action (Browser)
###############################################################################

def bulk_generate_cloze(nids: List[int]):
    global CFG
    CFG = _load_cfg()  # Refresh settings each run
    if not nids:
        tooltip("No notes selected")
        return

    col = mw.col
    changed = 0
    for nid in nids:
        note = col.get_note(nid)
        if populate_cloze(note):
            if note.id:
                col.update_note(note)
            changed += 1

    if changed:
        tooltip(f"Updated {changed} notes")
    else:
        tooltip("No notes needed")
    log("Bulk finished –", changed, "of", len(nids))


def browser_menu(browser):
    act = QAction(CFG.get("bulkActionLabel", "Generate Cloze Masks"), browser)
    act.triggered.connect(lambda _, b=browser: bulk_generate_cloze(b.selectedNotes()))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(act)


addHook("browser.setupMenus", browser_menu)

###############################################################################
# Options dialog
###############################################################################

def show_options():
    global CFG
    CFG = _load_cfg()

    dlg = QDialog(mw)
    dlg.setWindowTitle("Cloze Mask Options")
    lay = QFormLayout(dlg)

    w_sentence = QLineEdit(str(CFG.get("sentenceField", "Sentence")))
    w_word = QLineEdit(str(CFG.get("wordField", "Reading")))
    w_dest = QLineEdit(str(CFG.get("destinationField", "ClozeSentence")))
    w_types = QLineEdit(str(CFG.get("noteTypes", "")))
    w_mask = QLineEdit(str(CFG.get("maskString", "◼◼◼")))
    w_lookup = QCheckBox("Generate when leaving sentence/word fields")
    w_lookup.setChecked(bool(CFG.get("lookupOnAdd", True)))
    w_debug = QCheckBox("Enable debug logging (print to console)")
    w_debug.setChecked(bool(CFG.get("debug", False)))

    lay.addRow("Sentence field:", w_sentence)
    lay.addRow("Word field:", w_word)
    lay.addRow("Destination (clozed) field:", w_dest)
    lay.addRow("Note-type filter (comma):", w_types)
    lay.addRow("Mask string:", w_mask)
    lay.addRow(w_lookup)
    lay.addRow(w_debug)

    try:
        std = QDialogButtonBox.StandardButton
        btns = QDialogButtonBox(std.Ok | std.Cancel)
    except AttributeError:
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

    lay.addRow(btns)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)

    if not dlg.exec():
        return

    new_cfg = {
        "sentenceField": w_sentence.text().strip() or "Sentence",
        "wordField": w_word.text().strip() or "Reading",
        "destinationField": w_dest.text().strip() or "ClozeSentence",
        "noteTypes": w_types.text().strip(),
        "maskString": w_mask.text().strip() or "◼◼◼",
        "lookupOnAdd": w_lookup.isChecked(),
        "bulkActionLabel": CFG.get("bulkActionLabel", "Generate Cloze Masks"),
        "debug": w_debug.isChecked(),
    }

    _save_cfg(new_cfg)
    CFG = _load_cfg()
    showInfo("Cloze Mask settings saved.")


# Add to Tools menu
menu_act = QAction("Cloze Mask Options…", mw)
menu_act.triggered.connect(show_options)
mw.form.menuTools.addSeparator()
mw.form.menuTools.addAction(menu_act)

print("[ClozeMask] Cloze Mask Auto-Fill add-on loaded.")

