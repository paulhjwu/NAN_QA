# Taiwanese Word Alignment Tools

A collection of tools for aligning words between parallel text files, specifically designed for working with Chinese and Taiwanese language texts. This toolkit supports multiple alignment methods and provides an interactive visualization interface.

## 📋 Overview

This workspace contains tools for:
- Extracting verses from SFM (Standard Format Marker) files
- Word-by-word alignment between parallel texts
- Chinese text segmentation
- Multiple alignment algorithms (fast_align, GIZA++, awesome-align)
- Interactive web-based visualization of alignments

## 🗂️ Files

### Core Alignment Tools

- **[`align_words.py`](align_words.py)** - Uses fast_align for word alignment
- **[`align_giza.py`](align_giza.py)** - Uses GIZA++ with Chinese word segmentation
- **[`align_words_awesome.py`](align_words_awesome.py)** - Uses awesome-align (neural-based alignment)

### Support Tools

- **[`extract_verse.py`](extract_verse.py)** - Extracts chapter and verse content from SFM files
- **[`segment_verses.py`](segment_verses.py)** - Segments Chinese text using jieba
- **[`alignment_viewer.html`](alignment_viewer.html)** - Interactive web viewer for alignment results

### Data Files

- **Source Files:**
  - `42MRK_p.SFM` - Mark (source format)
  - `42MRKTTVH.SFM` - Mark Taiwanese (source format)
  - `mrk_p.txt` / `mrk1.txt` / `mrk2.txt` - Processed text files
  - `mrkttvh.txt` - Taiwanese text

- **Segmented Files:**
  - `mrk1_segmented.txt` - Reference segmented version
  - `mrk2_segmented.txt` - AI-Generated segmented version

- **Alignment Results:**
  - `word_alignments.txt` - fast_align output
  - `giza_alignments.txt` / `giza_alignments_2.txt` - GIZA++ output
  - `my_alignments.txt` - Custom alignments (using awesome alignment)

## 🚀 Quick Start

### 0. Extract Verses from SFM Files (Optional)

If you're starting with SFM (Standard Format Marker) files, first extract the verses:

```bash
# Extract AI generated text
python extract_verse.py 42MRK_p.SFM > mrk2.txt

# Extract Reference text
python extract_verse.py 42MRKTTVH.SFM > mrk1.txt
```

This creates `mrk1.txt` and `mrk2.txt` with the respective texts.

### 1. Chinese Text Segmentation

First, segment Chinese text for better alignment:

```bash
python segment_verses.py mrk1.txt mrk2.txt
```

This creates `mrk1_segmented.txt` and `mrk2_segmented.txt`.

### 2. Word Alignment

Choose one of three alignment methods:

#### Option A: fast_align (Fast, Simple)

```bash
python align_words.py mrk1_segmented.txt mrk2_segmented.txt word_alignments.txt
```

**Requirements:**
- fast_align executable in PATH or current directory
- Download from: https://github.com/clab/fast_align

#### Option B: GIZA++ (Traditional, Accurate)

```bash
python align_giza.py mrk1_segmented.txt mrk2_segmented.txt giza_alignments.txt
```

**Requirements:**
- GIZA++ installed and in PATH
- jieba Python package: `pip install jieba`

**Installation:**
```bash
cd ~
git clone https://github.com/moses-smt/giza-pp.git
cd giza-pp
make
sudo cp GIZA++-v2/GIZA++ /usr/local/bin/
sudo cp GIZA++-v2/snt2cooc.out /usr/local/bin/
sudo cp GIZA++-v2/plain2snt.out /usr/local/bin/
sudo cp mkcls-v2/mkcls /usr/local/bin/
```

#### Option C: awesome-align (Neural, State-of-the-art)

```bash
python align_words_awesome.py mrk1_segmented.txt mrk2_segmented.txt awesome_alignments.txt bert-base-multilingual-cased
```

**Requirements:**
- awesome-align: `pip install awesome-align`
- PyTorch (for GPU support): `pip install torch`

### 3. View Results

Open [`alignment_viewer.html`](alignment_viewer.html) in a web browser and load your alignment file (e.g., `word_alignments.txt`, `giza_alignments.txt`, and `awesome_alignments.txt`).

**Features:**
- 📊 Interactive visualization
- 🔍 Search through alignments
- 📄 Pagination (10 verses per page)
- 📈 Statistics summary
- 📱 Responsive design

## 📊 Input File Format

Input files should contain verses in the format:

```
1:1 In the beginning...
1:2 And the earth was...
```

Or:

```
MRK 1:1 起頭 的 福音...
MRK 1:2 按照 預言...
```

## 📄 Output Format

Alignment files contain structured output:

```
=== Chapter 1, Verse 1 (Line 1) ===
Source: 起頭 的 福音
Target: tī khí-thâu ê hok-im
Alignments:
  0:起頭 -> 1:khí-thâu
  1:的 -> 2:ê
  2:福音 -> 3:hok-im
```

## 🛠️ Dependencies

### Python Packages

```bash
pip install jieba              # For Chinese segmentation
pip install awesome-align      # For neural alignment (optional)
pip install torch              # For GPU support (optional)
```

### External Tools

- **fast_align** - Fast statistical alignment
- **GIZA++** - Traditional statistical alignment

## 📈 Comparison of Methods

| Method | Speed | Accuracy | Setup Difficulty | Best For |
|--------|-------|----------|------------------|----------|
| fast_align | ⚡⚡⚡ Fast | 🎯 Good | 🔧 Easy | Quick results |
| GIZA++ | ⚡ Slow | 🎯🎯 Very Good | 🔧🔧 Moderate | Traditional MT |
| awesome-align | ⚡⚡ Medium | 🎯🎯🎯 Excellent | 🔧🔧🔧 Complex | Best quality |

## 🔍 Features

### [`segment_verses.py`](segment_verses.py)
- Automatic Chinese word segmentation using jieba
- Preserves verse structure
- Batch processing support

### [`align_giza.py`](align_giza.py)
- Chinese word segmentation integration
- GIZA++ wrapper with automatic setup
- Chapter and verse tracking
- Detailed alignment output

### [`align_words_awesome.py`](align_words_awesome.py)
- Neural transformer-based alignment
- Multiple model support (BERT, XLM-R, mBERT)
- GPU acceleration support
- State-of-the-art accuracy

### [`alignment_viewer.html`](alignment_viewer.html)
- No installation required (pure HTML/JS)
- Real-time search and filtering
- Pagination for large files
- Word-by-word alignment display
- Statistics dashboard

## 📝 Examples

### Segment and Align with GIZA++

```bash
# Step 1: Segment Chinese text
python segment_verses.py mrk1.txt mrk2.txt

# Step 2: Align with GIZA++
python align_giza.py mrk1_segmented.txt mrk2_segmented.txt output.txt

# Step 3: Open alignment_viewer.html and load output.txt
```

### Using awesome-align with Different Models

```bash
# Default multilingual BERT
python align_words_awesome.py mrk1.txt mrk2.txt alignments.txt

# XLM-RoBERTa (better for low-resource languages)
python align_words_awesome.py mrk1.txt mrk2.txt alignments.txt xlm-roberta-base

# Chinese-specific model
python align_words_awesome.py mrk1.txt mrk2.txt alignments.txt bert-base-chinese
```

## 🤝 Contributing

Feel free to submit issues or pull requests to improve these tools!

## 📄 License

These tools are provided as-is for educational and research purposes.

## 🔗 Resources

- [fast_align GitHub](https://github.com/clab/fast_align)
- [GIZA++ GitHub](https://github.com/moses-smt/giza-pp)
- [awesome-align GitHub](https://github.com/neulab/awesome-align)
- [jieba GitHub](https://github.com/fxsjy/jieba)

## 📧 Support

For questions or issues, please check the individual script help messages:

```bash
python align_words.py --help
python align_giza.py --help
python align_words_awesome.py --help
```