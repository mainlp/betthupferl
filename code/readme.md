# Code for Betthupferl ASR and analyses

## A. Preprocessing
If necessary, convert MP3 files to WAV:
```
./A_convert-mp3towav.sh [FILE]
```

Preprocess the audio and transcription files. This creates one audio file per sentence, and one text file per story with one line per sentence. The output is in `../data_processed/audio` and `../data_processed/transcriptions`.
```
./A_process_audio_and_transcriptions.py
```

Extract the pure dialectal/German text from the transcripts (for the evaluation scripts later; -> `../data_processed/pure_text/{dialect}_gold_{dial,deu}.txt`). Then, calculate the data stats (-> `../data_processed/data_stats.tsv`).
```
./A_tsv_to_txt_gold.sh
./A_data_stats.py
```

## B. ASR
Run the already trained ASR models (zero-shot). Always specificy the model ID and the prefix of the stories you'd like to transcribe. Stories are transcribed one at a time, with the output (and gold transcriptions) saved to `../predictions/[model ID]/[story name].tsv`. 
Note that the TSV files in some cases contain older versions of the gold transcriptions (before some typos were fixed). 

```
./B_transcribe_zeroshot.py [model ID] ../data_processed/transcriptions/[story prefix]

# E.g., this transcribes all Billy stories with the medium-size Whisper model:
./B_transcribe_zeroshot.py openai/whisper-medium ../data_processed/transcriptions/billy

# These are all the models we use:
# - Whisper as released
./B_transcribe_zeroshot.py openai/whisper-tiny ../data_processed/transcriptions/
./B_transcribe_zeroshot.py openai/whisper-base ../data_processed/transcriptions/
./B_transcribe_zeroshot.py openai/whisper-small ../data_processed/transcriptions/
./B_transcribe_zeroshot.py openai/whisper-medium ../data_processed/transcriptions/
./B_transcribe_zeroshot.py openai/whisper-large-v2 ../data_processed/transcriptions/
./B_transcribe_zeroshot.py openai/whisper-large-v3 ../data_processed/transcriptions/
./B_transcribe_zeroshot.py openai/whisper-large-v3-turbo ../data_processed/transcriptions/
# - Whisper additionally fine-tuned on German
./B_transcribe_zeroshot.py bofenghuang/whisper-small-cv11-german ../data_processed/transcriptions/
./B_transcribe_zeroshot.py bofenghuang/whisper-medium-cv11-german ../data_processed/transcriptions/
./B_transcribe_zeroshot.py bofenghuang/whisper-large-v2-cv11-german ../data_processed/transcriptions/
# - Whisper additionally fine-tuned on Swiss German (with adapters)
./B_transcribe_zeroshot.py nizarmichaud/whisper-large-v3-turbo-swissgerman ../data_processed/transcriptions/
# - XLS-R
./B_transcribe_zeroshot.py AndrewMcDowell/wav2vec2-xls-r-300m-german-de ../data_processed/transcriptions/
./B_transcribe_zeroshot.py AndrewMcDowell/wav2vec2-xls-r-1B-german ../data_processed/transcriptions/
# - MMS
./B_transcribe_zeroshot.py facebook/mms-1b-all ../data_processed/transcriptions/
```

Ignore the reference columns (standard and dialect) in the prediction files in this repository -- they're a bit outdated (corrections have been made since then) and they're ignored for the score calculations!!

Convert the output files to pure text files:
```
./B_tsv_to_txt_pred.sh
```

## C. Evaluation and analysis
Calculate the word and character error rates as well as BLEU scores (saved to one TSV file per model in the `scores` directory):
```
# Run the evaluation script for one model's predictions:
# ./C_evaluate_preds.py [PREDICTIONS_FOLDER]
# E.g.,
./C_evaluate_preds.py ../predictions/openai-whisper-base_zeroshot

# Or for all of them:
./C_evaluate_all.sh
```

Analyze how well the automatic metrics correlate with each other and with the human judgments (the results are saved to `../analysis/correlations_{metrics,human_eval}_{spearman,pearson}.tsv`):
```
./C_correlations_metrics.py
```

Produce word-level alignments of the two gold transcriptions and one of the models' outputs for manual analysis:
```
# Picking the best zero-shot model here:
./C_align_gold_and_pred.py ../predictions/openai-whisper-large-v3_zeroshot/
```
The result is saved to `../analysis/wordaligned_deu_dial_openai-whisper-large-v3_zeroshot.tsv`, where it is further annotated (manually).

After carrying out the word-level annotations, get the stats of word- and sentence-level differences between the dialectal/standard references and the references and the best ASR hypotheses:
```
./C_wordlevel_stats.py > ../analysis/wordlevel_stats.txt
```
