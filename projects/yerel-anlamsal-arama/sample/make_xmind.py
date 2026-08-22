#!/usr/bin/env python3
"""Synthetic .xmind test files — both formats (Zen content.json + XMind 8 content.xml),
as Turkish book-summary mindmaps like the user's corpus. Gitignored."""
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- Zen / 2020+ : content.json ---
ZEN = [{
    "id": "s1", "class": "sheet", "title": "Özet",
    "rootTopic": {
        "id": "r", "class": "topic", "title": "Atomik Alışkanlıklar",
        "notes": {"plain": {"content": "James Clear — küçük değişimlerin gücü"}},
        "children": {"attached": [
            {"id": "b1", "title": "Dört Yasa", "children": {"attached": [
                {"title": "Belirgin kıl"}, {"title": "Çekici kıl"},
                {"title": "Kolay kıl"}, {"title": "Tatmin edici kıl"}]}},
            {"id": "b2", "title": "Kimlik temelli alışkanlıklar",
             "notes": {"plain": {"content": "Ne yaptığına değil, kim olmak istediğine odaklan"}}},
            {"id": "b3", "title": "Alışkanlık döngüsü", "children": {"attached": [
                {"title": "İşaret"}, {"title": "İstek"}, {"title": "Tepki"}, {"title": "Ödül"}]}},
        ]}}}]

# --- XMind 8 : content.xml (namespaced) ---
XML8 = """<?xml version="1.0" encoding="UTF-8"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" version="2.0">
 <sheet id="s1">
  <topic id="r"><title>Hızlı ve Yavaş Düşünme</title>
   <children><topics type="attached">
     <topic><title>Sistem 1</title><notes><plain>Hızlı, otomatik, sezgisel düşünme</plain></notes></topic>
     <topic><title>Sistem 2</title><notes><plain>Yavaş, çaba gerektiren, mantıksal akıl yürütme</plain></notes>
       <children><topics type="attached">
         <topic><title>Bilişsel yanlılıklar</title></topic>
         <topic><title>Çıpalama etkisi</title></topic>
       </topics></children>
     </topic>
   </topics></children>
  </topic>
  <title>Sheet 1</title>
 </sheet>
</xmap-content>"""


def build():
    made = []
    p1 = HERE / "haritalar" / "atomik_aliskanliklar.xmind"
    p1.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(p1, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.json", json.dumps(ZEN, ensure_ascii=False))
        z.writestr("meta.json", json.dumps({"creator": {"name": "Tansel"}}, ensure_ascii=False))
    made.append(p1)

    p2 = HERE / "haritalar" / "hizli_yavas_dusunme.xmind"
    with zipfile.ZipFile(p2, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.xml", XML8)
    made.append(p2)
    return made


if __name__ == "__main__":
    for f in build():
        print("  ->", f.relative_to(HERE))
