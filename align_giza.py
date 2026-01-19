#!/usr/bin/env python3
"""
Use GIZA++ with Chinese word segmentation to align words between parallel text files.
"""

import re
import sys
import subprocess
import tempfile
import os
import shutil
from collections import defaultdict

def extract_verse_info(line):
    """
    Extract chapter, verse number, and text from a line.
    
    Args:
        line: Input line in format 'Chapter X, Verse Y: text'
        
    Returns:
        Tuple of (chapter, verse, text) or (None, None, line.strip())
    """
    match = re.match(r'Chapter (\d+), Verse (\d+):\s*(.*)', line.strip())
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, line.strip()

def segment_chinese(text):
    """
    Segment Chinese text using jieba.
    
    Args:
        text: Chinese text to segment
        
    Returns:
        Space-separated segmented text
    """
    try:
        import jieba
        # Segment and join with spaces
        return ' '.join(jieba.cut(text))
    except ImportError:
        print("Error: jieba not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'jieba'], check=True)
        import jieba
        return ' '.join(jieba.cut(text))

def prepare_giza_corpus(file1, file2, output_dir):
    """
    Prepare parallel corpus for GIZA++ with Chinese word segmentation.
    
    Args:
        file1: Path to first file (source)
        file2: Path to second file (target)
        output_dir: Directory to save prepared files
        
    Returns:
        Tuple of (source_file, target_file, num_lines, verse_info_list)
    """
    source_file = os.path.join(output_dir, 'source.txt')
    target_file = os.path.join(output_dir, 'target.txt')
    
    count = 0
    verse_info = []
    
    print("Segmenting Chinese text (this may take a moment)...")
    
    with open(file1, 'r', encoding='utf-8') as f1, \
         open(file2, 'r', encoding='utf-8') as f2, \
         open(source_file, 'w', encoding='utf-8') as src_out, \
         open(target_file, 'w', encoding='utf-8') as tgt_out:
        
        for line1, line2 in zip(f1, f2):
            chapter1, verse1, text1 = extract_verse_info(line1)
            chapter2, verse2, text2 = extract_verse_info(line2)
            
            if text1 and text2 and chapter1 and verse1:
                # Segment Chinese text
                segmented1 = segment_chinese(text1)
                segmented2 = segment_chinese(text2)
                
                src_out.write(f"{segmented1}\n")
                tgt_out.write(f"{segmented2}\n")
                verse_info.append((chapter1, verse1))
                count += 1
    
    return source_file, target_file, count, verse_info

def check_giza():
    """
    Check if GIZA++ is installed.
    
    Returns:
        True if GIZA++ is available, False otherwise
    """
    # Check for common GIZA++ executables
    giza_commands = ['GIZA++', 'giza++', 'giza-pp']
    
    for cmd in giza_commands:
        if shutil.which(cmd):
            return True
    
    # Check common installation paths
    common_paths = [
        '/usr/local/bin/GIZA++',
        '/usr/bin/GIZA++',
        os.path.expanduser('~/giza-pp/GIZA++-v2/GIZA++'),
        './GIZA++',
    ]
    
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return True
    
    return False

def find_executable(names):
    """Find an executable by checking multiple possible names and paths."""
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    
    # Check common installation paths
    for name in names:
        common_paths = [
            f'/usr/local/bin/{name}',
            f'/usr/bin/{name}',
            os.path.expanduser(f'~/giza-pp/GIZA++-v2/{name}'),
            os.path.expanduser(f'~/giza-pp/mkcls-v2/{name}'),
            f'./{name}',
        ]
        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
    
    return None

def create_snt_files_manually(source_file, target_file, snt_dir):
    """Create vocabulary and sentence files manually."""
    # Read files and build vocabularies
    src_vocab = defaultdict(int)
    tgt_vocab = defaultdict(int)
    src_sentences = []
    tgt_sentences = []
    
    with open(source_file, 'r', encoding='utf-8') as f:
        for line in f:
            words = line.strip().split()
            src_sentences.append(words)
            for word in words:
                src_vocab[word] += 1
    
    with open(target_file, 'r', encoding='utf-8') as f:
        for line in f:
            words = line.strip().split()
            tgt_sentences.append(words)
            for word in words:
                tgt_vocab[word] += 1
    
    # Write vocabulary files
    with open(os.path.join(snt_dir, 'source.vcb'), 'w', encoding='utf-8') as f:
        for i, (word, count) in enumerate(sorted(src_vocab.items()), 1):
            f.write(f"{i} {word} {count}\n")
    
    with open(os.path.join(snt_dir, 'target.vcb'), 'w', encoding='utf-8') as f:
        for i, (word, count) in enumerate(sorted(tgt_vocab.items()), 1):
            f.write(f"{i} {word} {count}\n")
    
    # Create word-to-id mappings
    src_word2id = {word: i for i, (word, _) in enumerate(sorted(src_vocab.items()), 1)}
    tgt_word2id = {word: i for i, (word, _) in enumerate(sorted(tgt_vocab.items()), 1)}
    
    # Write sentence files in GIZA++ snt format
    with open(os.path.join(snt_dir, 'source_target.snt'), 'w', encoding='utf-8') as fout:
        for sent_num, (src_words, tgt_words) in enumerate(zip(src_sentences, tgt_sentences), 1):
            fout.write(f"1\n")
            fout.write(' '.join(str(src_word2id.get(w, 0)) for w in src_words) + '\n')
            fout.write(' '.join(str(tgt_word2id.get(w, 0)) for w in tgt_words) + '\n')
    
    # Create reverse direction snt file
    with open(os.path.join(snt_dir, 'target_source.snt'), 'w', encoding='utf-8') as fout:
        for sent_num, (src_words, tgt_words) in enumerate(zip(src_sentences, tgt_sentences), 1):
            fout.write(f"1\n")
            fout.write(' '.join(str(tgt_word2id.get(w, 0)) for w in tgt_words) + '\n')
            fout.write(' '.join(str(src_word2id.get(w, 0)) for w in src_words) + '\n')
    
    print(f"Created vocabulary files with {len(src_vocab)} source and {len(tgt_vocab)} target words")
    print(f"Created sentence files with {len(src_sentences)} sentence pairs")

def run_giza(source_file, target_file, output_dir):
    """
    Run GIZA++ alignment.
    
    Args:
        source_file: Source corpus file
        target_file: Target corpus file
        output_dir: Output directory
        
    Returns:
        Path to alignment file if successful, None otherwise
    """
    try:
        giza_exec = find_executable(['GIZA++', 'giza++', 'giza-pp'])
        if not giza_exec:
            print("Error: GIZA++ executable not found")
            return None
        
        # Create sentence files
        print("Creating sentence pair files...")
        
        snt_dir = os.path.join(output_dir, 'snt')
        os.makedirs(snt_dir, exist_ok=True)
        
        # Try to find plain2snt
        plain2snt = find_executable(['plain2snt.out', 'plain2snt'])
        
        if plain2snt:
            result = subprocess.run([
                plain2snt,
                source_file,
                target_file,
                '-vcb1', os.path.join(snt_dir, 'source.vcb'),
                '-vcb2', os.path.join(snt_dir, 'target.vcb'),
                '-snt1', os.path.join(snt_dir, 'source_target.snt'),
                '-snt2', os.path.join(snt_dir, 'target_source.snt')
            ], capture_output=True, text=True)
            
            # Check if files were actually created
            if not os.path.exists(os.path.join(snt_dir, 'source.vcb')):
                print("Warning: plain2snt did not create files, using alternative method...")
                create_snt_files_manually(source_file, target_file, snt_dir)
        else:
            print("Warning: plain2snt not found, using alternative method...")
            create_snt_files_manually(source_file, target_file, snt_dir)
        
        # Generate cooccurrence file
        print("\nGenerating cooccurrence file...")
        snt2cooc = find_executable(['snt2cooc.out', 'snt2cooc'])
        
        cooc_file = os.path.join(output_dir, 'source_target.cooc')
        
        if snt2cooc:
            try:
                with open(cooc_file, 'w') as cooc_out:
                    result = subprocess.run([
                        snt2cooc,
                        os.path.join(snt_dir, 'source.vcb'),
                        os.path.join(snt_dir, 'target.vcb'),
                        os.path.join(snt_dir, 'source_target.snt')
                    ], stdout=cooc_out, stderr=subprocess.PIPE, text=True, check=True)
                print(f"Cooccurrence file created: {cooc_file}")
            except subprocess.CalledProcessError as e:
                print(f"Warning: snt2cooc failed: {e.stderr}")
                print("Continuing anyway, GIZA++ may fail...")
        else:
            print("Warning: snt2cooc not found, GIZA++ may fail without cooccurrence file")
        
        # Run GIZA++
        print(f"\nRunning GIZA++ alignment...")
        print("This may take several minutes...")
        
        alignment_output = os.path.join(output_dir, 'alignment')
        
        cmd = [
            giza_exec,
            '-S', os.path.join(snt_dir, 'source.vcb'),
            '-T', os.path.join(snt_dir, 'target.vcb'),
            '-C', os.path.join(snt_dir, 'source_target.snt'),
            '-CoocurrenceFile', cooc_file,
            '-o', alignment_output,
            '-p0', '0.98',
            '-m1', '5',
            '-m2', '0',
            '-m3', '3',
            '-m4', '3',
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"GIZA++ return code: {result.returncode}")
            print(f"GIZA++ stderr:\n{result.stderr}")
            if result.stdout:
                print(f"GIZA++ stdout:\n{result.stdout}")
            return None
        
        print("GIZA++ completed successfully!")
        
        # Find the final alignment file (usually .A3.final)
        final_alignment = f"{alignment_output}.A3.final"
        if os.path.exists(final_alignment):
            return final_alignment
        
        # Look for any .final file
        for f in os.listdir(output_dir):
            if f.endswith('.final'):
                return os.path.join(output_dir, f)
        
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Error running GIZA++: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_giza_alignment(alignment_file):
    """
    Parse GIZA++ alignment output.
    
    Args:
        alignment_file: Path to GIZA++ alignment file
        
    Returns:
        List of alignment lists
    """
    alignments = []
    
    with open(alignment_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # GIZA++ format has 3 lines per sentence
            if line.startswith('#'):
                # Skip comment line
                i += 1
                if i < len(lines):
                    # Target sentence
                    i += 1
                if i < len(lines):
                    # Source sentence with alignments
                    alignment_line = lines[i].strip()
                    sent_alignments = []
                    
                    # Parse alignment format: word ({ target_indices })
                    parts = alignment_line.split('({')
                    for j, part in enumerate(parts[1:], 0):
                        if '})' in part:
                            indices_str = part.split('})')[0].strip()
                            if indices_str:
                                for idx in indices_str.split():
                                    try:
                                        sent_alignments.append((j, int(idx) - 1))
                                    except ValueError:
                                        continue
                    
                    alignments.append(sent_alignments)
                    i += 1
            else:
                i += 1
    
    return alignments

def format_alignment_output(chapter, verse, source_text, target_text, alignments, line_num):
    """
    Format alignment output in a readable way.
    
    Args:
        chapter: Chapter number
        verse: Verse number
        source_text: Source sentence
        target_text: Target sentence
        alignments: List of (source_idx, target_idx) tuples
        line_num: Line number for reference
        
    Returns:
        Formatted string showing alignments
    """
    src_words = source_text.split()
    tgt_words = target_text.split()
    
    output = []
    output.append(f"=== Chapter {chapter}, Verse {verse} (Line {line_num}) ===")
    output.append(f"Source: {source_text}")
    output.append(f"Target: {target_text}")
    output.append("Alignments:")
    
    for src_idx, tgt_idx in sorted(alignments):
        if src_idx < len(src_words) and tgt_idx < len(tgt_words):
            output.append(f"  {src_idx}:{src_words[src_idx]} -> {tgt_idx}:{tgt_words[tgt_idx]}")
    
    return '\n'.join(output)

def print_installation_instructions():
    """Print GIZA++ installation instructions."""
    print("\n" + "="*70)
    print("GIZA++ INSTALLATION INSTRUCTIONS")
    print("="*70)
    print("\nInstall GIZA++:")
    print("-" * 70)
    print("cd ~")
    print("git clone https://github.com/moses-smt/giza-pp.git")
    print("cd giza-pp")
    print("make")
    print("\nThen add to PATH or copy executables:")
    print("sudo cp GIZA++-v2/GIZA++ /usr/local/bin/")
    print("sudo cp GIZA++-v2/snt2cooc.out /usr/local/bin/")
    print("sudo cp GIZA++-v2/plain2snt.out /usr/local/bin/")
    print("sudo cp mkcls-v2/mkcls /usr/local/bin/")
    print("\nAlso install jieba for Chinese segmentation:")
    print("pip install jieba")
    print("="*70 + "\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python align_giza.py <source_file> <target_file> [output_file]")
        print("\nExample: python align_giza.py mrk1.txt mrk2.txt giza_alignments.txt")
        sys.exit(1)
    
    source_file = sys.argv[1]
    target_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "giza_alignments.txt"
    
    # Check if input files exist
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found")
        sys.exit(1)
    if not os.path.exists(target_file):
        print(f"Error: Target file '{target_file}' not found")
        sys.exit(1)
    
    # Check for GIZA++
    if not check_giza():
        print("Error: GIZA++ not found.")
        print_installation_instructions()
        sys.exit(1)
    
    print(f"Aligning words using GIZA++ with Chinese segmentation:")
    print(f"  Source: {source_file}")
    print(f"  Target: {target_file}")
    print()
    
    # Create temporary working directory
    work_dir = tempfile.mkdtemp(prefix='giza_')
    print(f"Working directory: {work_dir}")
    
    try:
        # Step 1: Prepare corpus with segmentation
        print("\nStep 1: Preparing corpus with Chinese word segmentation...")
        src_file, tgt_file, num_lines, verse_info_list = prepare_giza_corpus(source_file, target_file, work_dir)
        print(f"Prepared {num_lines} parallel sentences")
        
        # Step 2: Run GIZA++
        print("\nStep 2: Running GIZA++ alignment...")
        alignment_file = run_giza(src_file, tgt_file, work_dir)
        
        if not alignment_file:
            print("Error: GIZA++ alignment failed")
            print(f"Check the working directory for debug info: {work_dir}")
            sys.exit(1)
        
        print("Alignment complete!")
        
        # Step 3: Parse and format output
        print(f"\nStep 3: Formatting alignments and saving to {output_file}...")
        
        alignments_list = parse_giza_alignment(alignment_file)
        
        with open(src_file, 'r', encoding='utf-8') as f1, \
             open(tgt_file, 'r', encoding='utf-8') as f2, \
             open(output_file, 'w', encoding='utf-8') as out:
            
            line_num = 0
            for src_line, tgt_line, aligns in zip(f1, f2, alignments_list):
                line_num += 1
                src_text = src_line.strip()
                tgt_text = tgt_line.strip()
                
                # Get chapter and verse info
                if line_num - 1 < len(verse_info_list):
                    chapter, verse = verse_info_list[line_num - 1]
                else:
                    chapter, verse = "?", "?"
                
                formatted = format_alignment_output(chapter, verse, src_text, tgt_text, aligns, line_num)
                out.write(formatted)
                out.write("\n\n")
        
        print(f"Done! Alignments saved to {output_file}")
        print(f"Total lines aligned: {num_lines}")
        
        # Clean up temporary directory
        shutil.rmtree(work_dir)
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Working directory preserved for debugging: {work_dir}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
