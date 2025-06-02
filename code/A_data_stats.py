#!/usr/bin/env python3

from glob import glob
import numpy as np
import nltk

dialect2stories = {}

for filepath in glob("../data_processed/transcriptions/*.tsv"):
    with open(filepath) as f:
        first_line = True
        for line in f:
            if first_line:
                first_line = False
                continue
            _, speaker, dialect, trans_dial, trans_deu, duration, _ = line.split("\t")
            duration = float(duration)
            try:
                try:
                    dialect2stories[dialect][filepath].append(
                        (duration, trans_dial, trans_deu, speaker))
                except KeyError:
                    dialect2stories[dialect][filepath] = [
                        (duration, trans_dial, trans_deu, speaker)]
            except KeyError:
                dialect2stories[dialect] = {filepath: [
                    (duration, trans_dial, trans_deu, speaker)]}


dialect2stats = {}
alldial_stories = set()
alldial_sentences = 0
alldial_speakers = set()
alldial_duration_seconds = 0
alldial_sentence_durations = []
alldial_sentence_lengths_deu = []
alldial_sentence_lengths_dial = []
alldial_levenshtein_chars_raw = []
alldial_levenshtein_words_raw = []
alldial_levenshtein_chars_cleaned = []
alldial_levenshtein_words_cleaned = []
alldeutest_stories = set()
alldeutest_sentences = 0
alldeutest_speakers = set()
alldeutest_duration_seconds = 0
alldeutest_sentence_durations = []
alldeutest_sentence_lengths_deu = []
alldeu_stories = set()
alldeu_sentences = 0
alldeu_speakers = set()
alldeu_duration_seconds = 0
alldeu_sentence_durations = []
alldeu_sentence_lengths_deu = []
allall_stories = set()
allall_sentences = 0
allall_speakers = set()
allall_duration_seconds = 0
allall_sentence_durations = []
allall_sentence_lengths_deu = []
for dialect in dialect2stories:
    print(dialect)
    if dialect == "hochdeutschtrain" or dialect == "hochdeutschdev":
        continue
    stories = [story for story in dialect2stories[dialect]]
    n_sentences = 0
    sentence_lengths_words_deu = []  # whitespace-based
    sentence_lengths_words_dial = []  # whitespace-based
    durations = []  # in seconds
    speakers = set()
    for story in dialect2stories[dialect]:
        sentences = dialect2stories[dialect][story]
        n_sentences += len(sentences)
        for duration, trans_dial, trans_deu, speaker in sentences:
            durations.append(duration)
            speakers.add(speaker)
            deu_words = trans_deu.split()
            sentence_lengths_words_deu.append(len(deu_words))
            if not dialect.startswith("hochdeutsch"):
                dial_words = trans_dial.split()
                sentence_lengths_words_dial.append(len(dial_words))
    speakers_f, speakers_m = 0, 0
    for speaker in speakers:
        if speaker[0] == "F":
            speakers_f += 1
        else:
            speakers_m += 1
    speaker_stats = ""
    if speakers_f >= 1:
        speaker_stats = str(speakers_f) + "F"
        if speakers_m >= 1:
            speaker_stats += ", " + str(speakers_m) + "M"
    elif speakers_m >= 1:
        speaker_stats = str(speakers_m) + "M"

    levenshtein_distances_chars_raw = []
    levenshtein_distances_words_raw = []
    levenshtein_distances_chars_cleaned = []
    levenshtein_distances_words_cleaned = []
    if not dialect.startswith("hochdeutsch"):
        with open(f"../data_processed/pure_text/{dialect}_gold_dial.txt") as f:
            dial_sents_raw = f.read().splitlines()
        deu_sents_raw = []
        with open(f"../data_processed/pure_text/{dialect}_gold_deu.txt") as f:
            deu_sents_raw = f.read().splitlines()
        for dial, deu in zip(dial_sents_raw, deu_sents_raw):
            max_len_chars = len(deu) if len(deu) > len(dial) else len(dial)
            levenshtein_distances_chars_raw.append(
                100 * nltk.edit_distance(deu, dial) / max_len_chars)
            dial = dial.split()
            deu = deu.split()
            max_len_words = len(deu) if len(deu) > len(dial) else len(dial)
            levenshtein_distances_words_raw.append(
                100 * nltk.edit_distance(deu, dial) / max_len_words)
        dial_sents_cleaned = []
        with open(f"../data_processed/pure_text/{dialect}_goldnorm_dial.txt") as f:
            dial_sents_cleaned = f.read().splitlines()
        deu_sents_cleaned = []
        with open(f"../data_processed/pure_text/{dialect}_goldnorm_deu.txt") as f:
            deu_sents_cleaned = f.read().splitlines()
        for dial, deu in zip(dial_sents_cleaned, deu_sents_cleaned):
            max_len_chars = len(deu) if len(deu) > len(dial) else len(dial)
            levenshtein_distances_chars_cleaned.append(
                100 * nltk.edit_distance(deu, dial) / max_len_chars)
            dial = dial.split()
            deu = deu.split()
            max_len_words = len(deu) if len(deu) > len(dial) else len(dial)
            levenshtein_distances_words_cleaned.append(
                100 * nltk.edit_distance(deu, dial) / max_len_words)
        dial_sents_raw = []

    dialect2stats[dialect] = [
        len(dialect2stories[dialect]), speaker_stats,
        n_sentences, round(sum(durations) / 60),
        durations,
        sentence_lengths_words_deu,
        sentence_lengths_words_dial,
        levenshtein_distances_words_raw,
        levenshtein_distances_chars_raw,
        levenshtein_distances_words_cleaned,
        levenshtein_distances_chars_cleaned,
    ]

    if dialect.startswith("hochdeutsch"):
        alldeu_stories.update(stories)
        alldeu_sentences += n_sentences
        alldeu_speakers.update(speakers)
        alldeu_duration_seconds += sum(durations)
        alldeu_sentence_durations += durations
        alldeu_sentence_lengths_deu += sentence_lengths_words_deu
        if dialect in ["hochdeutschtest", "hochdeutschdial"]:
            alldeutest_stories.update(stories)
            alldeutest_sentences += n_sentences
            alldeutest_speakers.update(speakers)
            alldeutest_duration_seconds += sum(durations)
            alldeutest_sentence_durations += durations
            alldeutest_sentence_lengths_deu += sentence_lengths_words_deu
    else:
        alldial_stories.update(stories)
        alldial_sentences += n_sentences
        alldial_speakers.update(speakers)
        alldial_duration_seconds += sum(durations)
        alldial_sentence_durations += durations
        alldial_sentence_lengths_deu += sentence_lengths_words_deu
        alldial_sentence_lengths_dial += sentence_lengths_words_dial
        alldial_levenshtein_chars_raw += levenshtein_distances_chars_raw
        alldial_levenshtein_words_raw += levenshtein_distances_words_raw
        alldial_levenshtein_chars_cleaned += levenshtein_distances_chars_cleaned
        alldial_levenshtein_words_cleaned += levenshtein_distances_words_cleaned
    allall_stories.update(stories)
    allall_sentences += n_sentences
    allall_speakers.update(speakers)
    allall_duration_seconds += sum(durations)
    allall_sentence_durations += durations
    allall_sentence_lengths_deu += sentence_lengths_words_deu

with open("../data_processed/data_stats.tsv", "w") as f:
    f.write("DIALECT\tSPEAKERS\tN_STORIES\t")
    f.write("N_SENTENCES\tTOTAL_AUDIO_MINUTES\t")
    f.write("SENTENCE_LENGTH_SECONDS_MEAN\tSENTENCE_LENGTH_SECONDS_STD\t")
    f.write("SENTENCE_LENGTH_WORDS_DEU_MEAN\tSENTENCE_LENGTH_WORDS_DEU_STD\t")
    f.write("SENTENCE_LENGTH_WORDS_DIAL_MEAN\t")
    f.write("SENTENCE_LENGTH_WORDS_DIAL_STD\t")
    f.write("LEVENSHTEIN_RAW_WORD_NORMALIZED_MEAN\t")
    f.write("LEVENSHTEIN_RAW_WORD_NORMALIZED_STD\t")
    f.write("LEVENSHTEIN_RAW_CHAR_NORMALIZED_MEAN\t")
    f.write("LEVENSHTEIN_RAW_CHAR_NORMALIZED_STD\t")
    f.write("LEVENSHTEIN_CLEANED_WORD_NORMALIZED_MEAN\t")
    f.write("LEVENSHTEIN_CLEANED_WORD_NORMALIZED_STD\t")
    f.write("LEVENSHTEIN_CLEANED_CHAR_NORMALIZED_MEAN\t")
    f.write("LEVENSHTEIN_CLEANED_CHAR_NORMALIZED_STD\n")

    for dialect in sorted(dialect2stats):
        if dialect.startswith("hochdeutsch"):
            continue
        stats = dialect2stats[dialect]
        f.write(f"{dialect}\t{stats[0]}\t{stats[1]}\t{stats[2]}\t{stats[3]}\t")
        f.write(f"{np.mean(stats[4]):.1f}\t{np.std(stats[4]):.1f}\t")
        f.write(f"{np.mean(stats[5]):.1f}\t{np.std(stats[5]):.1f}\t")
        f.write(f"{np.mean(stats[6]):.1f}\t{np.std(stats[6]):.1f}\t")
        f.write(f"{np.mean(stats[7]):.1f}\t{np.std(stats[7]):.1f}\t")
        f.write(f"{np.mean(stats[8]):.1f}\t{np.std(stats[8]):.1f}\t")
        f.write(f"{np.mean(stats[9]):.1f}\t{np.std(stats[9]):.1f}\t")
        f.write(f"{np.mean(stats[10]):.1f}\t{np.std(stats[10]):.1f}\n")

    f.write(f"ALL DIALECTS\t{len(alldial_stories)}\t")
    speakers_f, speakers_m = 0, 0
    for speaker in alldial_speakers:
        if speaker[0] == "F":
            speakers_f += 1
        else:
            speakers_m += 1
    f.write(f"{speakers_f}F, {speakers_m}M\t")
    f.write(f"{alldial_sentences}\t{round(alldial_duration_seconds / 60)}\t")
    f.write(f"{np.mean(alldial_sentence_durations):.1f}\t")
    f.write(f"{np.std(alldial_sentence_durations):.1f}\t")
    f.write(f"{np.mean(alldial_sentence_lengths_deu):.1f}\t")
    f.write(f"{np.std(alldial_sentence_lengths_deu):.1f}\t")
    f.write(f"{np.mean(alldial_sentence_lengths_dial):.1f}\t")
    f.write(f"{np.std(alldial_sentence_lengths_dial):.1f}\t")
    f.write(f"{np.mean(alldial_levenshtein_words_raw):.1f}\t")
    f.write(f"{np.std(alldial_levenshtein_words_raw):.1f}\t")
    f.write(f"{np.mean(alldial_levenshtein_chars_raw):.1f}\t")
    f.write(f"{np.std(alldial_levenshtein_chars_raw):.1f}\t")
    f.write(f"{np.mean(alldial_levenshtein_words_cleaned):.1f}\t")
    f.write(f"{np.std(alldial_levenshtein_words_cleaned):.1f}\t")
    f.write(f"{np.mean(alldial_levenshtein_chars_cleaned):.1f}\t")
    f.write(f"{np.std(alldial_levenshtein_chars_cleaned):.1f}\n")

    for german_split in [
            "hochdeutschtest", "hochdeutschdial"]:
        stats = dialect2stats[german_split]
        f.write(f"{german_split}\t{stats[0]}\t{stats[1]}\t")
        f.write(f"{stats[2]}\t{stats[3]}\t")
        f.write(f"{np.mean(stats[4]):.1f}\t{np.std(stats[4]):.1f}\t")
        f.write(f"{np.mean(stats[5]):.1f}\t{np.std(stats[5]):.1f}\t")
        f.write("---\t---\t---\t---\t---\t---\t---\t---\t---\t---\n")

    f.write(f"ALL GERMAN EVAL\t{len(alldeutest_stories)}\t")
    speakers_f, speakers_m = 0, 0
    for speaker in alldeutest_speakers:
        if speaker[0] == "F":
            speakers_f += 1
        else:
            speakers_m += 1
    f.write(f"{speakers_f}F, {speakers_m}M\t")
    f.write(f"{alldeutest_sentences}\t")
    f.write(f"{round(alldeutest_duration_seconds / 60)}\t")
    f.write(f"{np.mean(alldeutest_sentence_durations):.1f}\t")
    f.write(f"{np.std(alldeutest_sentence_durations):.1f}\t")
    f.write(f"{np.mean(alldeutest_sentence_lengths_deu):.1f}\t")
    f.write(f"{np.std(alldeutest_sentence_lengths_deu):.1f}\t")
    f.write("---\t---\t---\t---\t---\t---\t---\t---\t---\t---\n")

    f.write(f"ALL GERMAN\t{len(alldeu_stories)}\t")
    speakers_f, speakers_m = 0, 0
    for speaker in alldeu_speakers:
        if speaker[0] == "F":
            speakers_f += 1
        else:
            speakers_m += 1
    f.write(f"{speakers_f}F, {speakers_m}M\t")
    f.write(f"{alldeu_sentences}\t{round(alldeu_duration_seconds / 60)}\t")
    f.write(f"{np.mean(alldeu_sentence_durations):.1f}\t")
    f.write(f"{np.std(alldeu_sentence_durations):.1f}\t")
    f.write(f"{np.mean(alldeu_sentence_lengths_deu):.1f}\t")
    f.write(f"{np.std(alldeu_sentence_lengths_deu):.1f}\t")
    f.write("---\t---\t---\t---\t---\t---\t---\t---\t---\t---\n")

    f.write(f"FULL DATASET\t{len(allall_stories)}\t")
    speakers_f, speakers_m = 0, 0
    for speaker in allall_speakers:
        if speaker[0] == "F":
            speakers_f += 1
        else:
            speakers_m += 1
    f.write(f"{speakers_f}F, {speakers_m}M\t")
    f.write(f"{allall_sentences}\t{round(allall_duration_seconds / 60)}\t")
    f.write(f"{np.mean(allall_sentence_durations):.1f}\t")
    f.write(f"{np.std(allall_sentence_durations):.1f}\t")
    f.write(f"{np.mean(allall_sentence_lengths_deu):.1f}\t")
    f.write(f"{np.std(allall_sentence_lengths_deu):.1f}\t")
    f.write("---\t---\t---\t---\t---\t---\t---\t---\t---\t---\n")
