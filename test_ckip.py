from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker

# 1. Initialize the models
# Use device=0 for GPU, or device=-1 for CPU
# Models: 'bert-base' (accurate) or 'albert-tiny' (fast)
print("Loading models...")
ws_driver = CkipWordSegmenter(model="bert-base", device=0)
pos_driver = CkipPosTagger(model="bert-base", device=0)
ner_driver = CkipNerChunker(model="bert-base", device=0)

# 2. Prepare text (List of sentences)
text = [
    "傅達仁今將執行安樂死，卻突然爆出自己20年前遭緯來體育台封殺",
    "台灣的半導體產業非常發達"
]

# 3. Run Pipeline
# ws (Word Segmentation) -> pos (Part of Speech) -> ner (Named Entity Recognition)
ws = ws_driver(text)
pos = pos_driver(ws)
ner = ner_driver(text)

# 4. Print Results
for sentence, sentence_ws, sentence_pos, sentence_ner in zip(text, ws, pos, ner):
    print(f"\nOriginal: {sentence}")
    print(f"Segmented: {' '.join(sentence_ws)}")
    print(f"POS Tags: {' '.join(sentence_pos)}")
    for entity in sentence_ner:
        print(f"Entity: {entity}")