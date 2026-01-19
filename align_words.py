#!/usr/bin/env python3
"""
Use fast_align to align words between two parallel text files line by line.
"""

import re
import sys
import subprocess
import tempfile
import os
import shutil

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

def prepare_parallel_corpus(file1, file2, output_file):
    """
    Prepare parallel corpus in the format required by fast_align.
    Format: source_text ||| target_text
    
    Args:
        file1: Path to first file (source)
        file2: Path to second file (target)
        output_file: Path to output file for fast_align input
        
    Returns:
        Tuple of (number of parallel lines written, list of (chapter, verse) tuples)
    """
    count = 0
    verse_info = []
    
    with open(file1, 'r', encoding='utf-8') as f1, \
         open(file2, 'r', encoding='utf-8') as f2, \
         open(output_file, 'w', encoding='utf-8') as out:
        
        for line1, line2 in zip(f1, f2):
            chapter1, verse1, text1 = extract_verse_info(line1)
            chapter2, verse2, text2 = extract_verse_info(line2)
            
            if text1 and text2:
                # fast_align expects: source ||| target
                out.write(f"{text1} ||| {text2}\n")
                # Store verse info (prefer first file's chapter/verse)
                chapter = chapter1 if chapter1 else chapter2
                verse = verse1 if verse1 else verse2
                verse_info.append((chapter, verse))
                count += 1
    
    return count, verse_info

def find_fast_align():
    """
    Find fast_align executable in various locations.
    
    Returns:
        Path to fast_align if found, None otherwise
    """
    # Check current directory first
    if os.path.isfile('./fast_align') and os.access('./fast_align', os.X_OK):
        return './fast_align'
    
    # Check if it's in PATH
    fast_align_path = shutil.which('fast_align')
    if fast_align_path:
        return fast_align_path
    
    # Check other common locations
    possible_paths = [
        os.path.expanduser('~/fast_align/build/fast_align'),
        '/usr/local/bin/fast_align',
        '/usr/bin/fast_align',
    ]
    
    for path in possible_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    return None

def run_fast_align(input_file, output_file, fast_align_path, reverse=False):
    """
    Run fast_align on the prepared corpus.
    
    Args:
        input_file: Path to parallel corpus file
        output_file: Path to save alignments
        fast_align_path: Path to fast_align executable
        reverse: If True, align target-to-source; otherwise source-to-target
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = [fast_align_path, '-i', input_file, '-d', '-o', '-v']
        if reverse:
            cmd.append('-r')
        
        with open(output_file, 'w') as out:
            result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, 
                                  text=True, check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running fast_align: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def parse_alignments(alignment_line):
    """
    Parse fast_align output format.
    Format: 0-0 1-1 2-3 ...
    
    Args:
        alignment_line: Line from fast_align output
        
    Returns:
        List of (source_idx, target_idx) tuples
    """
    alignments = []
    for pair in alignment_line.strip().split():
        if '-' in pair:
            src, tgt = pair.split('-')
            alignments.append((int(src), int(tgt)))
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
    if chapter and verse:
        output.append(f"=== Chapter {chapter}, Verse {verse} (Line {line_num}) ===")
    else:
        output.append(f"=== Line {line_num} ===")
    output.append(f"Source: {source_text}")
    output.append(f"Target: {target_text}")
    output.append("Alignments:")
    
    for src_idx, tgt_idx in sorted(alignments):
        if src_idx < len(src_words) and tgt_idx < len(tgt_words):
            output.append(f"  {src_idx}:{src_words[src_idx]} -> {tgt_idx}:{tgt_words[tgt_idx]}")
    
    return '\n'.join(output)

def main():
    if len(sys.argv) < 3:
        print("Usage: python align_words.py <source_file> <target_file> [output_file]")
        print("\nExample: python align_words.py mrk1.txt mrk2.txt alignments.txt")
        sys.exit(1)
    
    source_file = sys.argv[1]
    target_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "word_alignments.txt"
    
    # Check if input files exist
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found")
        sys.exit(1)
    if not os.path.exists(target_file):
        print(f"Error: Target file '{target_file}' not found")
        sys.exit(1)
    
    # Find fast_align
    fast_align_path = find_fast_align()
    if not fast_align_path:
        print("Error: fast_align not found.")
        print("Please ensure fast_align is:")
        print("  1. In the current directory (./fast_align)")
        print("  2. In your PATH")
        print("  3. At ~/fast_align/build/fast_align")
        print("\nYou can get it from: https://github.com/clab/fast_align")
        sys.exit(1)
    
    print(f"Using fast_align: {fast_align_path}")
    print(f"\nAligning words between:")
    print(f"  Source: {source_file}")
    print(f"  Target: {target_file}")
    print()
    
    # Create temporary files for fast_align
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_input:
        tmp_input_path = tmp_input.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_output:
        tmp_output_path = tmp_output.name
    
    try:
        # Step 1: Prepare parallel corpus
        print("Preparing parallel corpus...")
        num_lines, verse_info_list = prepare_parallel_corpus(source_file, target_file, tmp_input_path)
        print(f"Prepared {num_lines} parallel sentences")
        
        # Step 2: Run fast_align
        print("\nRunning fast_align...")
        if not run_fast_align(tmp_input_path, tmp_output_path, fast_align_path):
            sys.exit(1)
        
        print("Alignment complete!")
        
        # Step 3: Format and save output
        print(f"\nFormatting alignments and saving to {output_file}...")
        
        with open(source_file, 'r', encoding='utf-8') as f1, \
             open(target_file, 'r', encoding='utf-8') as f2, \
             open(tmp_output_path, 'r') as align_f, \
             open(output_file, 'w', encoding='utf-8') as out:
            
            line_num = 0
            verse_idx = 0
            for src_line, tgt_line, align_line in zip(f1, f2, align_f):
                line_num += 1
                chapter1, verse1, src_text = extract_verse_info(src_line)
                chapter2, verse2, tgt_text = extract_verse_info(tgt_line)
                alignments = parse_alignments(align_line)
                
                # Use chapter and verse from verse_info_list if available
                if verse_idx < len(verse_info_list):
                    chapter, verse = verse_info_list[verse_idx]
                    verse_idx += 1
                else:
                    chapter = chapter1 if chapter1 else chapter2
                    verse = verse1 if verse1 else verse2
                
                formatted = format_alignment_output(chapter, verse, src_text, tgt_text, alignments, line_num)
                out.write(formatted)
                out.write("\n\n")
        
        print(f"Done! Alignments saved to {output_file}")
        print(f"Total lines aligned: {num_lines}")
        
    finally:
        # Clean up temporary files
        if os.path.exists(tmp_input_path):
            os.unlink(tmp_input_path)
        if os.path.exists(tmp_output_path):
            os.unlink(tmp_output_path)

if __name__ == "__main__":
    main()