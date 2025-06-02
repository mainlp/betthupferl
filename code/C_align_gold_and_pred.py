#!/usr/bin/env python3

from C_levenshtein import levenshtein_words
import sys


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./align_gold_and_pred.py PREDICTIONS_FOLDER")
        sys.exit(1)

    predictions_folder = sys.argv[1]
    file1 = "../data_processed/pure_text/alldialects_gold_deu.txt"
    file2 = "../data_processed/pure_text/alldialects_gold_dial.txt"
    file3 = sys.argv[1] + "/alldialects_pred.txt"
    model_name = sys.argv[1].split("/")[-2] if sys.argv[1][-1] == "/" else sys.argv[1].split("/")[-1]
    lines1 = []
    with open(file1) as f:
        lines1 = f.readlines()
    lines2 = []
    with open(file2) as f:
        lines2 = f.readlines()
    lines3 = []
    with open(file3) as f:
        lines3 = f.readlines()
    with open(f"../analysis/wordaligned_deu_dial_{model_name}.tsv", "w") as f:
        f.write("GOLD_DIAL\tGOLD_DEU\tPRED\n")
        for line1, line2, line3 in zip(lines1, lines2, lines3):
            # Align the gold transcriptions (deu and dial)
            aligned12_1, aligned12_2, _ = levenshtein_words(
                line1.split(), line2.split())
            # Align the gold deu transcription with the predicted text
            aligned13_1, aligned13_3, _ = levenshtein_words(
                line1.split(), line3.split())
            # Align the two separately aligned versions of gold deu
            aligned_1, aligned_2, aligned_3 = [], [], []
            i, j = 0, 0
            while (i < len(aligned12_1) or j < len(aligned13_1)):
                if i == len(aligned12_1):
                    aligned_1.append("")
                    aligned_2.append("")
                    aligned_3.append(aligned13_3[j])
                    j += 1
                elif j == len(aligned13_1):
                    aligned_1.append(aligned12_1[i])
                    aligned_2.append(aligned12_2[i])
                    aligned_3.append("")
                    i += 1
                elif aligned12_1[i] == "":
                    if aligned13_1[j] == "":
                        aligned_1.append(aligned12_1[i])
                        aligned_2.append(aligned12_2[i])
                        aligned_3.append(aligned13_3[j])
                        i += 1
                        j += 1
                    else:
                        aligned_1.append(aligned12_1[i])
                        aligned_2.append(aligned12_2[i])
                        aligned_3.append("")
                        i += 1
                else:
                    if aligned13_1[j] == "":
                        aligned_1.append("")
                        aligned_2.append("")
                        aligned_3.append(aligned13_3[j])
                        j += 1
                    else:
                        aligned_1.append(aligned12_1[i])
                        aligned_2.append(aligned12_2[i])
                        aligned_3.append(aligned13_3[j])
                        i += 1
                        j += 1
            for a1, a2, a3 in zip(aligned_1, aligned_2, aligned_3):
                f.write(f"{a2}\t{a1}\t{a3}\n")
            f.write("\n")
