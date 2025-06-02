#!/usr/bin/env python3

from collections import Counter
from glob import glob


def read_file(filename,
              diff_deu_word_lvl, diff_sent_lvl,
              errors_deu_word_lvl, errors_sent_lvl,
              diff2error,
              n_words, n_sents):
    with open(filename) as f:
        first_line = True
        sent_diffs = set()
        sent_errors = set()
        for line in f:
            if first_line:
                first_line = False
                continue
            cells = line.split("\t")
            if not line.strip():
                # end of sentence
                n_sents += 1
                for diff in sent_diffs:
                    diff_sent_lvl.append(diff)
                sent_diffs = set()
                for error in sent_errors:
                    errors_sent_lvl.append(error)
                sent_errors = set()
            elif cells[2].strip():
                n_words += 1
                word_diffs = cells[3]
                if not word_diffs.strip():
                    word_diffs = "NONE"
                for diff in word_diffs.split(","):
                    diff = diff.strip()
                    diff_deu_word_lvl.append(diff)
                    sent_diffs.add(diff)
                    if diff.startswith("Phon") or diff == "NONE":
                        error = cells[6]
                        for ignore in [
                                "Punctuation etc. (ok)",
                                "Punctuation that makes an important difference",
                                "Wrong capitalization"]:
                            error = error.replace(
                                ignore + ", ", "")
                            error = error.replace(
                                ignore, "")
                        if error.endswith(", "):
                            error = error[:-2]
                        diff2error.append((diff, error))
                    else:
                        error_diag = cells[7].strip()
                        if not error_diag:
                            print(line)
                            continue
                        diff2error.append((diff, error_diag))
                    if diff in ["DET + PROPN",
                                "Other",
                                "Possessive",
                                "Verbs",
                                "Word order",
                                "Dropped PRON"]:
                        sent_diffs.add("Grammar (any)")
                pred_errors = cells[6]
                if pred_errors.strip():
                    for error in pred_errors.split(","):
                        errors_deu_word_lvl.append(error.strip())
                        sent_errors.add(error.strip())
                else:
                    errors_deu_word_lvl.append("[identical to deu]")

    return (diff_deu_word_lvl, diff_sent_lvl,
            errors_deu_word_lvl, errors_sent_lvl,
            diff2error,
            n_words, n_sents)


diff_deu_word_lvl = []
diff_sent_lvl = []
errors_deu_word_lvl = []
errors_sent_lvl = []
diff2error = []
n_words = 0
n_sents = 0

for filename in glob("../analysis/comparison_*.tsv"):
    print(filename)
    (diff_deu_word_lvl, diff_sent_lvl,
     errors_deu_word_lvl, errors_sent_lvl,
     diff2error,
     n_words, n_sents) = read_file(
        filename,
        diff_deu_word_lvl, diff_sent_lvl,
        errors_deu_word_lvl, errors_sent_lvl,
        diff2error,
        n_words, n_sents)

print("\nTotal German reference words: " + str(n_words))
print()
for (diff, n) in Counter(diff_deu_word_lvl).most_common():
    print(f"{diff}\t{n}")
print()
for (error, n) in Counter(errors_deu_word_lvl).most_common():
    print(f"{error}\t{n}")
print()
print()

print("Total reference sentences: " + str(n_sents))
print()
for (diff, n) in Counter(diff_sent_lvl).most_common():
    print(f"{diff}\t{n}")
print()
for (error, n) in Counter(errors_sent_lvl).most_common():
    print(f"{error}\t{n}")
print()
print()
for key in sorted(Counter(diff2error)):
    print(f"{key[0]}\t{key[1]}\t{Counter(diff2error)[key]}")
