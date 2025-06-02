#!/usr/bin/env python3

import sys
from nltk import edit_distance
import re
import numpy as np
from glob import glob
from sacrebleu.metrics import BLEU


def preprocess_transcription(line):
    line = line.lower()
    # Remove word-initial/-final punctuation
    line = re.sub(r"(?<![\w])[^\w\s]", "", line)
    line = re.sub(r"[^\w\s](?![\w])", "", line)
    return line


def wer_cer(gold_dial, gold_deu, pred, german=False):
    # Sentence-level mean WER and CER
    wer_dial, wer_deu = [], []
    cer_dial, cer_deu = [], []
    if german:
        for deu, asr in zip(gold_deu, pred):
            deu_words, asr_words = deu.split(), asr.split()
            cer_deu.append(edit_distance(deu, asr) / len(deu))
            wer_deu.append(
                edit_distance(deu_words, asr_words) / len(deu_words))
    else:
        for dial, deu, asr in zip(gold_dial, gold_deu, pred):
            dial_words, deu_words, asr_words = dial.split(), deu.split(), asr.split()
            cer_dial.append(edit_distance(dial, asr) / len(dial))
            wer_dial.append(
                edit_distance(dial_words, asr_words) / len(dial_words))
            cer_deu.append(edit_distance(deu, asr) / len(deu))
            wer_deu.append(
                edit_distance(deu_words, asr_words) / len(deu_words))
    return (wer_dial, wer_deu,
            cer_dial, cer_deu)


def bleu_scores(gold_dial, gold_deu, pred,
                german=False):
    bleu = BLEU()
    bleu_deu = bleu.corpus_score(
        pred, [gold_deu]).score
#     print(bleu.get_signature())
    if german:
        bleu_dial = -1
        bleu_both = -1
    else:
        bleu_dial = bleu.corpus_score(
            pred, [gold_dial]).score
        bleu_both = bleu.corpus_score(
            pred, [gold_deu, gold_dial]).score
    return bleu_deu, bleu_dial, bleu_both


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: evaluate.py PREDICTIONS_FOLDER")
        sys.exit(1)

    results_folder = sys.argv[1]
    if results_folder.endswith("/"):
        results_folder = results_folder[:-1]
    out_file = results_folder.split("/")[-1]
    all_wer_dial_cleaned, all_wer_deu_cleaned = [], []
    all_cer_dial_cleaned, all_cer_deu_cleaned = [], []
    all_wer_dial_raw, all_wer_deu_raw = [], []
    all_cer_dial_raw, all_cer_deu_raw = [], []
    # One file with the average scores per dialect
    with open("../scores/" + out_file + ".tsv", "w") as f:
        f.write("ID\tN\t")
        f.write("WER_DIAL_CLEANED_MEAN\tWER_DIAL_CLEANED_STD\t")
        f.write("WER_DEU_CLEANED_MEAN\tWER_DEU_CLEANED_STD\t")
        f.write("CER_DIAL_CLEANED_MEAN\tCER_DIAL_CLEANED_STD\t")
        f.write("CER_DEU_CLEANED_MEAN\tCER_DEU_CLEANED_STD\t")
        f.write("BLEU_DIAL_REF_CLEANED\tBLEU_DEU_REF_CLEANED\t")
        f.write("BLEU_BOTH_REFs_CLEANED\t")
        f.write("WER_DIAL_RAW_MEAN\tWER_DIAL_RAW_STD\t")
        f.write("WER_DEU_RAW_MEAN\tWER_DEU_RAW_STD\t")
        f.write("CER_DIAL_RAW_MEAN\tCER_DIAL_RAW_STD\t")
        f.write("CER_DEU_RAW_MEAN\tCER_DEU_RAW_STD\t")
        f.write("BLEU_DIAL_REF_RAW\tBLEU_DEU_REF_RAW\t")
        f.write("BLEU_BOTH_REFs_RAW\n")
        # And one file with the scores for each predicted sentence
        # (for calculating correlations)
        with open("../scores/" + out_file + "_detailed.tsv",
                  "w") as f_det:
            f_det.write("ID\tGOLD_DIAL\tGOLD_DEU\tPRED\t")
            f_det.write("WER_DIAL_CLEANED\tWER_DEU_CLEANED\t")
            f_det.write("CER_DIAL_CLEANED\tCER_DEU_CLEANED\t")
            f_det.write("BLEU_DIAL_REF_CLEANED\tBLEU_DEU_REF_CLEANED\t")
            f_det.write("BLEU_BOTH_REFs_CLEANED\t")
            f_det.write("WER_DIAL_RAW\tWER_DEU_RAW\t")
            f_det.write("CER_DIAL_RAW\tCER_DEU_RAW\t")
            f_det.write("BLEU_DIAL_REF_RAW\tBLEU_DEU_REF_RAW\t")
            f_det.write("BLEU_BOTH_REFs_RAW\n")
            for dialect in ["oberbayern", "niederbayern",
                            "oberfranken", "mittelfranken", "unterfranken",
                            "oberpfalz", "schwaben", "alldialects",
                            "hochdeutschdial", "hochdeutschtest",
                            "allhochdeutsch"]:
                print(dialect)
                std_german = "hochdeutsch" in dialect
                sentences = []
                lines_dial_gold = []
                lines_dial_goldnorm = []
                lines_deu_gold = []
                lines_deu_goldnorm = []
                lines_pred = []
                lines_prednorm = []
                try:
                    if not std_german:
                        with open("../data_processed/pure_text/" + dialect + "_gold_dial.txt") as f_in:
                            lines_dial_gold = f_in.read().splitlines()
                        with open("../data_processed/pure_text/" + dialect + "_goldnorm_dial.txt") as f_in:
                            lines_dial_goldnorm = f_in.read().splitlines()
                    with open("../data_processed/pure_text/" + dialect + "_gold_deu.txt") as f_in:
                        lines_deu_gold = f_in.read().splitlines()
                    with open("../data_processed/pure_text/" + dialect + "_goldnorm_deu.txt") as f_in:
                        lines_deu_goldnorm = f_in.read().splitlines()
                    with open(results_folder + "/" + dialect + "_pred.txt") as f_in:
                        lines_pred = f_in.read().splitlines()
                    with open(results_folder + "/" + dialect + "_prednorm.txt") as f_in:
                        lines_prednorm = f_in.read().splitlines()
                    (wer_dial_raw, wer_deu_raw,
                     cer_dial_raw, cer_deu_raw) = wer_cer(
                        lines_dial_gold, lines_deu_gold, lines_pred,
                        german=std_german)
                    (wer_dial_cleaned, wer_deu_cleaned,
                     cer_dial_cleaned, cer_deu_cleaned) = wer_cer(
                        lines_dial_goldnorm, lines_deu_goldnorm, lines_prednorm,
                        german=std_german)
                    (bleu_deu_raw, bleu_dial_raw,
                     bleu_both_raw) = bleu_scores(
                        lines_dial_gold, lines_deu_gold, lines_pred,
                        german=std_german)
                    (bleu_deu_cleaned, bleu_dial_cleaned,
                     bleu_both_cleaned) = bleu_scores(
                        lines_dial_goldnorm, lines_deu_goldnorm, lines_prednorm,
                        german=std_german)
                    if not dialect.startswith("all"):
                        if std_german:
                            idx = 0
                            for (deu, pred, deu_c, pred_c,
                                 wer_deu_c, cer_deu_c,
                                 wer_deu_r, cer_deu_r) in zip(
                                    lines_deu_gold, lines_pred,
                                    lines_deu_goldnorm, lines_prednorm,
                                    wer_deu_cleaned, cer_deu_cleaned,
                                    wer_deu_raw, cer_deu_raw):
                                f_det.write(f"{dialect}-{idx}\t\t{deu}\t{pred}\t")
                                idx += 1
                                f_det.write(f"\t{wer_deu_c}\t")
                                f_det.write(f"\t{cer_deu_c}\t")
                                bleu_deu_c, _, _ = bleu_scores(
                                    None, [deu_c], [pred_c], german=True)
                                f_det.write(f"{bleu_deu_c}\t\t\t")
                                f_det.write(f"\t{wer_deu_r}\t")
                                f_det.write(f"\t{cer_deu_r}\t")
                                bleu_deu_r, _, _ = bleu_scores(
                                    None, [deu], [pred], german=True)
                                f_det.write(f"\t{bleu_deu_r}\t\n")
                        else:
                            idx = 0
                            for (dial, deu, pred, dial_c, deu_c, pred_c,
                                 wer_dial_c, wer_deu_c, cer_dial_c, cer_deu_c,
                                 wer_dial_r, wer_deu_r, cer_dial_r, cer_deu_r) in zip(
                                    lines_dial_gold, lines_deu_gold, lines_pred,
                                    lines_dial_goldnorm, lines_deu_goldnorm,
                                    lines_prednorm,
                                    wer_dial_cleaned, wer_deu_cleaned,
                                    cer_dial_cleaned, cer_deu_cleaned,
                                    wer_dial_raw, wer_deu_raw,
                                    cer_dial_raw, cer_deu_raw):
                                f_det.write(f"{dialect}-{idx}\t{dial}\t{deu}\t{pred}\t")
                                idx += 1
                                f_det.write(f"{wer_dial_c}\t{wer_deu_c}\t")
                                f_det.write(f"{cer_dial_c}\t{cer_deu_c}\t")
                                bleu_deu_c, bleu_dial_c, bleu_both_c = bleu_scores(
                                    [dial_c], [deu_c], [pred_c])
                                f_det.write(f"{bleu_dial_c}\t{bleu_deu_c}\t{bleu_both_c}\t")
                                f_det.write(f"{wer_dial_r}\t{wer_deu_r}\t")
                                f_det.write(f"{cer_dial_r}\t{cer_deu_r}\t")
                                bleu_deu_r, bleu_dial_r, bleu_both_r = bleu_scores(
                                    [dial], [deu], [pred])
                                f_det.write(f"{bleu_dial_r}\t{bleu_deu_r}\t{bleu_both_r}\n")
                except FileNotFoundError:
                    print("File not found for " + dialect)
                    wer_dial_cleaned, cer_dial_cleaned = [-1], [-1]
                    wer_deu_cleaned, cer_deu_cleaned = [-1], [-1]
                    bleu_dial_cleaned, bleu_deu_cleaned, bleu_both_cleaned = [-1], [-1], [-1]
                    wer_dial_raw, cer_dial_raw = [-1], [-1]
                    wer_deu_raw, cer_deu_raw = [-1], [-1]
                    bleu_dial_raw, bleu_deu_raw, bleu_both_raw = [-1], [-1], [-1]
                f.write(f"{dialect}\t{len(lines_pred)}\t")
                if std_german:
                    f.write("---\t---\t")
                    f.write(f"{np.mean(wer_deu_cleaned):.2f}\t{np.std(wer_deu_cleaned):.2f}\t")
                    f.write("---\t---\t")
                    f.write(f"{np.mean(cer_deu_cleaned):.2f}\t{np.std(cer_deu_cleaned):.2f}\t")
                    f.write(f"---\t{bleu_deu_cleaned:.2f}\t---\t")
                    f.write("---\t---\t")
                    f.write(f"{np.mean(wer_deu_raw):.2f}\t{np.std(wer_deu_raw):.2f}\t")
                    f.write("---\t---\t")
                    f.write(f"{np.mean(cer_deu_raw):.2f}\t{np.std(cer_deu_raw):.2f}\t")
                    f.write(f"---\t{bleu_deu_raw:.2f}\t---\n")
                else:
                    f.write(f"{np.mean(wer_dial_cleaned):.2f}\t{np.std(wer_dial_cleaned):.2f}\t")
                    f.write(f"{np.mean(wer_deu_cleaned):.2f}\t{np.std(wer_deu_cleaned):.2f}\t")
                    f.write(f"{np.mean(cer_dial_cleaned):.2f}\t{np.std(cer_dial_cleaned):.2f}\t")
                    f.write(f"{np.mean(cer_deu_cleaned):.2f}\t{np.std(cer_deu_cleaned):.2f}\t")
                    f.write(f"{bleu_dial_cleaned:.2f}\t{bleu_deu_cleaned:.2f}\t")
                    f.write(f"{bleu_both_cleaned:.2f}\t")
                    f.write(f"{np.mean(wer_dial_raw):.2f}\t{np.std(wer_dial_raw):.2f}\t")
                    f.write(f"{np.mean(wer_deu_raw):.2f}\t{np.std(wer_deu_raw):.2f}\t")
                    f.write(f"{np.mean(cer_dial_raw):.2f}\t{np.std(cer_dial_raw):.2f}\t")
                    f.write(f"{np.mean(cer_deu_raw):.2f}\t{np.std(cer_deu_raw):.2f}\t")
                    f.write(f"{bleu_dial_raw:.2f}\t{bleu_deu_raw:.2f}\t")
                    f.write(f"{bleu_both_raw:.2f}\n")
