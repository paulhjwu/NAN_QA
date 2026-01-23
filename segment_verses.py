#!/usr/bin/env python3
"""
Segment Chinese text in verse files using jieba word segmentation.
"""

import re
import sys
import os

# Initialize jieba with traditional Chinese dictionary
_jieba_initialized = False

def _initialize_jieba():
    """Initialize jieba with traditional Chinese dictionary."""
    global _jieba_initialized
    if not _jieba_initialized:
        try:
            import jieba
            jieba.set_dictionary('trad_dict.txt')
            _jieba_initialized = True
        except ImportError:
            print("Error: jieba not installed. Installing...")
            import subprocess
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'jieba'], check=True)
            import jieba
            jieba.set_dictionary('trad_dict.txt')
            _jieba_initialized = True

def extract_verse_info(line):
    """
    Extract chapter, verse number, and text from a line.
    
    Args:
        line: Input line in format 'Chapter X, Verse Y: text'
        
    Returns:
        Tuple of (chapter, verse, text) or None if not a verse line
    """
    match = re.match(r'Chapter (\d+), Verse (\d+):\s*(.*)', line.strip())
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None

def segment_chinese(text):
    """
    Segment Chinese text using jieba with traditional Chinese dictionary.
    
    Args:
        text: Chinese text to segment
        
    Returns:
        Space-separated segmented text
    """
    _initialize_jieba()
    import jieba
    # Segment and join with spaces
    return ' '.join(jieba.cut(text))

def segment_file(input_file, output_file):
    """
    Segment all verses in a file.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        
    Returns:
        Number of verses processed
    """
    count = 0
    
    print(f"Processing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        
        for line in fin:
            verse_info = extract_verse_info(line)
            
            if verse_info:
                chapter, verse, text = verse_info
                
                # Segment the text
                segmented_text = segment_chinese(text)
                
                # Write with same format
                fout.write(f"Chapter {chapter}, Verse {verse}: {segmented_text}\n")
                count += 1
            else:
                # Keep non-verse lines as-is
                fout.write(line)
    
    return count

def main():
    # Check if input files are provided
    if len(sys.argv) > 1:
        input_files = sys.argv[1:]
    else:
        # Default files
        input_files = ['mrk1.txt', 'mrk2.txt']
    
    print("Chinese Word Segmentation Tool")
    print("=" * 50)
    print()
    
    total_verses = 0
    
    for input_file in input_files:
        if not os.path.exists(input_file):
            print(f"Warning: File '{input_file}' not found, skipping...")
            continue
        
        # Generate output filename
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_segmented.txt"
        
        try:
            count = segment_file(input_file, output_file)
            total_verses += count
            print(f"✓ Segmented {count} verses")
            print(f"  Output saved to: {output_file}")
            print()
        except Exception as e:
            print(f"✗ Error processing {input_file}: {e}")
            print()
    
    print("=" * 50)
    print(f"Total verses segmented: {total_verses}")
    print()
    print("Done!")

if __name__ == "__main__":
    main()