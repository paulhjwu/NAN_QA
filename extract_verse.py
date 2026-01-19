#!/usr/bin/env python3
"""
Extract chapter and verse content from SFM (Standard Format Marker) files.
"""

import re
import sys
from collections import defaultdict

def remove_footnotes(text):
    """
    Remove footnote content between \f and \f* markers.
    
    Args:
        text: The text to process
        
    Returns:
        Text with footnotes removed
    """
    # Remove everything between \f and \f* (including the markers)
    return re.sub(r'\\f\s+.*?\\f\*', '', text)

def remove_proper_name_markers(text):
    """
    Remove \pn and \pn* markers (proper name markers).
    
    Args:
        text: The text to process
        
    Returns:
        Text with \pn markers removed
    """
    # Remove \pn and \pn* markers
    text = re.sub(r'\\pn\*', '', text)
    text = re.sub(r'\\pn\s+', '', text)
    return text

def is_verse_placeholder(text):
    """
    Check if the verse content is just a placeholder (e.g., \vp [44]\vp*).
    
    Args:
        text: The verse content to check
        
    Returns:
        True if the verse is just a placeholder, False otherwise
    """
    # Remove whitespace and check if it matches the pattern \vp [number]\vp*
    stripped = text.strip()
    return bool(re.match(r'^\\vp\s*\[\d+\]\\vp\*$', stripped))

def parse_verse_number(verse_str):
    """
    Parse verse number or range and return a list of verse numbers.
    
    Args:
        verse_str: String containing verse number or range (e.g., "7" or "7-8")
        
    Returns:
        List of verse numbers as strings
    """
    # Check if it's a range (e.g., "7-8")
    range_match = re.match(r'(\d+)-(\d+)', verse_str)
    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        return [str(i) for i in range(start, end + 1)]
    else:
        # Single verse number
        return [verse_str]

def extract_chapters_and_verses(filename):
    """
    Extract chapter numbers and verse numbers with their content from an SFM file.
    Includes all \q (poetry/quotation) lines that follow a verse, removing the \q markers.
    Filters out \r lines, footnotes (\f ... \f*), and proper name markers (\pn ... \pn*).
    Handles verse ranges (e.g., 7-8) by expanding them into individual verses.
    Skips verses that are just placeholders (e.g., \vp [44]\vp*).
    Handles verses that may be empty initially but have content in \q lines.
    
    Args:
        filename: Path to the SFM file
        
    Returns:
        A list of tuples (chapter_num, verse_num, verse_content)
    """
    results = []
    current_chapter = None
    current_verses = []  # List of verse numbers for current verse(s)
    current_content = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            
            # Skip \r lines (cross-references)
            if re.match(r'\\r\s', line):
                continue
            
            # Check for chapter marker
            chapter_match = re.match(r'\\c\s+(\d+)', line)
            if chapter_match:
                # Save previous verse(s) if exists
                if current_chapter and current_verses:
                    verse_text = ' '.join(current_content).strip()
                    # Skip if it's just a placeholder or completely empty
                    if verse_text and not is_verse_placeholder(verse_text):
                        for verse_num in current_verses:
                            results.append((current_chapter, verse_num, verse_text))
                
                current_chapter = chapter_match.group(1)
                current_verses = []
                current_content = []
                continue
            
            # Check for verse marker (can be a number or range like "7-8")
            verse_match = re.match(r'\\v\s+([\d-]+)(?:\s+(.*))?', line)
            if verse_match:
                # Save previous verse(s) if exists
                if current_chapter and current_verses:
                    verse_text = ' '.join(current_content).strip()
                    # Skip if it's just a placeholder or completely empty
                    if verse_text and not is_verse_placeholder(verse_text):
                        for verse_num in current_verses:
                            results.append((current_chapter, verse_num, verse_text))
                
                # Start new verse(s) and remove footnotes and proper name markers
                verse_str = verse_match.group(1)
                current_verses = parse_verse_number(verse_str)
                verse_content = verse_match.group(2) if verse_match.group(2) else ""
                verse_content = remove_footnotes(verse_content)
                verse_content = remove_proper_name_markers(verse_content)
                # Start with content if present, otherwise start with empty list
                current_content = [verse_content] if verse_content.strip() else []
                continue
            
            # Check for \q marker (poetry/quotation lines)
            q_match = re.match(r'\\q\d?\s*(.*)', line)
            if q_match and current_verses:
                # Add the content after \q marker (without the marker itself)
                q_content = q_match.group(1)
                q_content = remove_footnotes(q_content)
                q_content = remove_proper_name_markers(q_content)
                if q_content.strip():  # Only add non-empty content
                    current_content.append(q_content)
                continue
        
        # Don't forget the last verse(s)
        if current_chapter and current_verses:
            verse_text = ' '.join(current_content).strip()
            # Skip if it's just a placeholder or completely empty
            if verse_text and not is_verse_placeholder(verse_text):
                for verse_num in current_verses:
                    results.append((current_chapter, verse_num, verse_text))
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_verses.py <sfm_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        verses = extract_chapters_and_verses(filename)
        
        # Count verses per chapter
        chapter_counts = defaultdict(int)
        for chapter, verse, content in verses:
            chapter_counts[chapter] += 1
        
        # Print results
        for chapter, verse, content in verses:
            print(f"Chapter {chapter}, Verse {verse}: {content}")
        
        print(f"\nTotal verses extracted: {len(verses)}")
        print(f"\nVerses per chapter:")
        for chapter in sorted(chapter_counts.keys(), key=int):
            print(f"  Chapter {chapter}: {chapter_counts[chapter]} verses")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()