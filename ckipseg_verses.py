#!/usr/bin/env python3
"""
Segment Chinese text in verse files using CKIP BERT-based transformer.
CKIP Transformers provides state-of-the-art Chinese word segmentation.
"""

import re
import sys
import os


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


def segment_chinese_ckip(text, ws_driver):
    """
    Segment Chinese text using CKIP Transformers.
    
    Args:
        text: Chinese text to segment
        ws_driver: CKIP word segmentation driver instance
        
    Returns:
        Space-separated segmented text
    """
    # CKIP returns a list of lists (one list per sentence)
    # We pass a single sentence, so we get [[word1, word2, ...]]
    result = ws_driver([text])
    
    # Join the words with spaces
    if result and len(result) > 0:
        return ' '.join(result[0])
    return text


def segment_file(input_file, output_file, ws_driver):
    """
    Segment all verses in a file using CKIP.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        ws_driver: CKIP word segmentation driver instance
        
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
                
                # Segment the text using CKIP
                segmented_text = segment_chinese_ckip(text, ws_driver)
                
                # Write with same format
                fout.write(f"Chapter {chapter}, Verse {verse}: {segmented_text}\n")
                count += 1
                
                # Print progress every 50 verses
                if count % 50 == 0:
                    print(f"  Processed {count} verses...")
            else:
                # Keep non-verse lines as-is
                fout.write(line)
    
    return count


def initialize_ckip():
    """
    Initialize CKIP Transformers word segmentation driver.
    
    Returns:
        Word segmentation driver instance
    """
    try:
        from ckip_transformers.nlp import CkipWordSegmenter
        
        print("Initializing CKIP Transformers (this may take a moment)...")
        print("Loading BERT model for word segmentation...")
        
        # Initialize the word segmenter with the default model
        # Use GPU if available, otherwise use CPU
        ws_driver = CkipWordSegmenter(model="bert-base", device=0)
        
        print("✓ CKIP model loaded successfully")
        return ws_driver
        
    except ImportError:
        print("\nError: ckip-transformers not installed.")
        print("\nTo install CKIP Transformers:")
        print("-" * 70)
        print("pip install ckip-transformers")
        print("\nFor GPU support (recommended):")
        print("pip install torch")
        print("\nFor more information, visit:")
        print("https://github.com/ckiplab/ckip-transformers")
        print("-" * 70)
        sys.exit(1)
    except Exception as e:
        print(f"\nError initializing CKIP: {e}")
        print("\nMake sure you have:")
        print("1. Installed ckip-transformers: pip install ckip-transformers")
        print("2. Installed PyTorch: pip install torch")
        print("3. Sufficient memory (model requires ~1GB)")
        sys.exit(1)


def main():
    # Check if input files are provided
    if len(sys.argv) > 1:
        input_files = sys.argv[1:]
    else:
        # Default files
        input_files = ['mrk1.txt', 'mrk2.txt']
    
    print("CKIP BERT-based Chinese Word Segmentation Tool")
    print("=" * 50)
    print()
    
    # Initialize CKIP word segmenter once for all files
    ws_driver = initialize_ckip()
    print()
    
    total_verses = 0
    
    for input_file in input_files:
        if not os.path.exists(input_file):
            print(f"Warning: File '{input_file}' not found, skipping...")
            continue
        
        # Generate output filename
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_ckip_segmented.txt"
        
        try:
            count = segment_file(input_file, output_file, ws_driver)
            total_verses += count
            print(f"✓ Segmented {count} verses")
            print(f"  Output saved to: {output_file}")
            print()
        except Exception as e:
            print(f"✗ Error processing {input_file}: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 50)
    print(f"Total verses segmented: {total_verses}")
    print()
    print("Done!")


if __name__ == "__main__":
    main()