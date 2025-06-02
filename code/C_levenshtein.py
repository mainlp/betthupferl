# Used in C_align_gold_and_preds.py

import numpy as np
import re
import string


# For now: regular Levenshtein implementation for comparing 2 strings
def levenshtein_chars(seq1, seq2):
    matrix = np.zeros((len(seq1) + 1, len(seq2) + 1))
    # Set-up (deleting/inserting all chars)
    for i in range(1, len(seq1) + 1):
        matrix[i, 0] = i
    for j in range(1, len(seq2) + 1):
        matrix[0, j] = j

    del_cost = 1
    ins_cost = 1
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            if seq1[i - 1] == seq2[j - 1]:
                subst_cost = 0
            else:
                # Could be modified to account for the
                # similarity of the associated phones
                subst_cost = 1
            matrix[i, j] = min(matrix[i - 1, j] + del_cost,
                               matrix[i, j - 1] + ins_cost,
                               matrix[i - 1, j - 1] + subst_cost)
    return matrix[-1, -1] / max(len(seq1), len(seq2))


# Aligns 2 lists of strings and computes the distance between them.
# Substitution costs are based on the character-level Levenshtein
# distance between the words.
def levenshtein_words(seq1, seq2,
                      normalize_by_longest=True,
                      return_alignment=True):
    matrix = np.zeros((len(seq1) + 1, len(seq2) + 1))
    # Set-up (deleting/inserting all chars)
    for i in range(1, len(seq1) + 1):
        matrix[i, 0] = i
    for j in range(1, len(seq2) + 1):
        matrix[0, j] = j

    del_cost = 1
    ins_cost = 1
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            # Ignore casing and punctuation for the
            # alignment
            word1 = normalize_word(seq1[i - 1])
            word2 = normalize_word(seq2[j - 1])
            if word1 == word2:
                subst_cost = 0
            else:
                subst_cost = levenshtein_chars(word1, word2)
            matrix[i, j] = min(matrix[i - 1, j] + del_cost,
                               matrix[i, j - 1] + ins_cost,
                               matrix[i - 1, j - 1] + subst_cost)

    divisor = max(len(seq1), len(seq2)) if normalize_by_longest else len(seq1)
    dist = matrix[-1, -1] / divisor

    if not return_alignment:
        return dist

    # Get the aligned sequences
    aligned1, aligned2 = [], []
    i = len(seq1)
    j = len(seq2)
    while (i > 0 or j > 0):
        if i < 0:
            i = 0
        if j < 0:
            j = 0
        if i == 0:
            word1 = ""
        else:
            word1 = normalize_word(seq1[i - 1])
        if j == 0:
            word2 = ""
        else:
            word2 = normalize_word(seq2[j - 1])
        if word1 == word2:
            if matrix[i, j] == matrix[i - 1, j - 1]:
                # Same word
                i -= 1
                j -= 1
                aligned1.append(seq1[i])
                aligned2.append(seq2[j])
        else:
            subst_cost = levenshtein_chars(word1, word2)
            if matrix[i, j] == matrix[i - 1, j - 1] + subst_cost:
                # Substitution
                i -= 1
                j -= 1
                aligned1.append(seq1[i])
                aligned2.append(seq2[j])
            elif matrix[i, j] == matrix[i - 1, j] + del_cost:
                # Deletion
                i -= 1
                aligned1.append(seq1[i])
                aligned2.append("")
            elif matrix[i, j] == matrix[i, j - 1] + ins_cost:
                # Insertion
                j -= 1
                aligned1.append("")
                aligned2.append(seq2[j])
            else:
                print("?? something went wrong")
    aligned1.reverse()
    aligned2.reverse()
    return aligned1, aligned2, dist


regex = re.compile('[%s]' % re.escape(string.punctuation))
def normalize_word(word):
    # Remove casing and punctuation.
    # (Moot if we read in the normalized files.)
    return regex.sub('', word.lower())
