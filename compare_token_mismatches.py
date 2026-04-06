#!/usr/bin/env python3
"""
Compare two segmented files and output mismatched tokens using Levenshtein distance.
"""
import sys
from difflib import SequenceMatcher

def read_tokens(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip().split() for line in f if line.strip()]

def compare_lines(tokens1, tokens2):
    matcher = SequenceMatcher(None, tokens1, tokens2)
    mismatches = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            mismatches.append((tag, tokens1[i1:i2], tokens2[j1:j2], i1, j1))
    return mismatches

def main(file1, file2):
    lines1 = read_tokens(file1)
    lines2 = read_tokens(file2)
    with open('compared.txt', 'w', encoding='utf-8') as fout:
        min_lines = min(len(lines1), len(lines2))
        for idx in range(min_lines):
            mismatches = compare_lines(lines1[idx], lines2[idx])
            if mismatches:
                fout.write(f"Line {idx+1}:\n")
                for tag, t1, t2, i1, j1 in mismatches:
                    fout.write(f"  {tag}: {t1} -> {t2}\n")
        if len(lines1) != len(lines2):
            fout.write(f"Warning: File lengths differ ({len(lines1)} vs {len(lines2)})\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} file1 file2")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
