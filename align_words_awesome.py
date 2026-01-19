#!/usr/bin/env python3
"""
Use awesome-align to align words between two parallel text files line by line.
"""

import re
import sys
import subprocess
import tempfile
import os

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
    Prepare parallel corpus in the format required by awesome-align.
    Format: source_text ||| target_text
    
    Args:
        file1: Path to first file (source)
        file2: Path to second file (target)
        output_file: Path to output file for awesome-align input
        
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
            
            if text1 and text2 and chapter1 and verse1:
                # awesome-align expects: source ||| target (same as fast_align)
                out.write(f"{text1} ||| {text2}\n")
                verse_info.append((chapter1, verse1))
                count += 1
    
    return count, verse_info

def check_awesome_align():
    """
    Check if awesome-align is installed.
    
    Returns:
        True if installed, False otherwise
    """
    try:
        result = subprocess.run(['awesome-align', '--help'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def run_awesome_align(input_file, output_file, model='bert-base-multilingual-cased'):
    """
    Run awesome-align on the prepared corpus.
    
    Args:
        input_file: Path to parallel corpus file
        output_file: Path to save alignments
        model: Model name or path (default: bert-base-multilingual-cased)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Using model: {model}")
        print("This may take a while on first run (downloading model)...")
        
        cmd = [
            'awesome-align',
            '--output_file', output_file,
            '--model_name_or_path', model,
            '--data_file', input_file,
            '--extraction', 'softmax',
            '--batch_size', '32'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Print any output from awesome-align
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running awesome-align: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def parse_alignments(alignment_line):
    """
    Parse awesome-align output format.
    Format: 0-0 1-1 2-3 ...
    
    Args:
        alignment_line: Line from awesome-align output
        
    Returns:
        List of (source_idx, target_idx) tuples
    """
    alignments = []
    for pair in alignment_line.strip().split():
        if '-' in pair:
            parts = pair.split('-')
            if len(parts) == 2:
                try:
                    src, tgt = int(parts[0]), int(parts[1])
                    alignments.append((src, tgt))
                except ValueError:
                    continue
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
    """Print instructions for installing awesome-align."""
    print("\n" + "="*70)
    print("AWESOME-ALIGN INSTALLATION INSTRUCTIONS")
    print("="*70)
    print("\nInstall via pip:")
    print("-" * 70)
    print("pip install awesome-align")
    print("\n# Or with GPU support:")
    print("pip install awesome-align torch")
    print("\nFor more information:")
    print("https://github.com/neulab/awesome-align")
    print("="*70 + "\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python align_words_awesome.py <source_file> <target_file> [output_file] [model]")
        print("\nExample: python align_words_awesome.py mrk1.txt mrk2.txt alignments.txt")
        print("         python align_words_awesome.py mrk1.txt mrk2.txt alignments.txt bert-base-multilingual-cased")
        sys.exit(1)
    
    source_file = sys.argv[1]
    target_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "word_alignments_awesome.txt"
    model = sys.argv[4] if len(sys.argv) > 4 else "bert-base-multilingual-cased"
    
    # Check if input files exist
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found")
        sys.exit(1)
    if not os.path.exists(target_file):
        print(f"Error: Target file '{target_file}' not found")
        sys.exit(1)
    
    # Check for awesome-align
    if not check_awesome_align():
        print("Error: awesome-align not found.")
        print_installation_instructions()
        sys.exit(1)
    
    print(f"Aligning words between:")
    print(f"  Source: {source_file}")
    print(f"  Target: {target_file}")
    print()
    
    # Create temporary file for awesome-align input
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_input:
        tmp_input_path = tmp_input.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_output:
        tmp_output_path = tmp_output.name
    
    try:
        # Step 1: Prepare parallel corpus
        print("Preparing parallel corpus...")
        num_lines, verse_info_list = prepare_parallel_corpus(source_file, target_file, tmp_input_path)
        print(f"Prepared {num_lines} parallel sentences")
        
        # Step 2: Run awesome-align
        print("\nRunning awesome-align...")
        if not run_awesome_align(tmp_input_path, tmp_output_path, model):
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
                    chapter, verse = chapter1 or "?", verse1 or "?"
                
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