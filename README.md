# Betthupferl: A multi-dialectal dataset for German dialect ASR and dialect-to-standard speech translation.

This repository contains supplementary material for the paper 
> “A multi-dialectal dataset for German dialect ASR and dialect-to-standard speech translation” (Verena Blaschke, Miriam Winkler, Constantin Förster, Gabriele Wenger-Glemser, and Barbara Plank). Accepted to Interspeech 2025. Preprint: https://arxiv.org/abs/2506.02894

Please cite the paper if you use any of this data/code.

This repository does *not* contain any audio data.
Access to the audio data must be granted by Bayerischer Rundfunk on a case-by-case basis due to copyright restrictions (contact Gabriele Wenger-Glemser).
If you obtain the audio files, create a folder called `audio` and place them inside that folder.

All subfolders containing transcriptions are in zip archives with the password `MaiNLP` so as to prevent potential inclusion in web-scraped datasets (cf. [Jacovi et al., 2023](https://aclanthology.org/2023.emnlp-main.308/)). Unzip them to get the subfolders with the same name.
Please do not re-distribute the transcriptions.

You can find the following contents:
- Reference transcriptions:  
  - `transcriptions_dialect`: Dialectal and Standard German references for dialectal audios (converted from FOLKER annotations)
  - `transcriptions_standard_german`: Standard German references for Standard German audios (converted from FOLKER annotations)
  - `data_processed/transcriptions`: Converted versions of the files in `transcriptions_*`: one TSV file per story & language variety combination, also contains the corresponding audio filepaths
  - `data_processed/pure_text`: Converted versions of the files in `transcriptions_*`: one file per language variety (or group thereof) and transcription type (dialectal `_dial` or standardized `_deu`), one sentence per line. The files with `_gold_` in the name contain the original punctuation and capitalization, the files with `_goldnorm_` are lowercased and without punctuation.
- Word-level and sentence-level annotations of the references and/or ASR hypotheses are in the `analysis` folder (more information in the readme file there)/
- The code for ASR predictions and analyses is in `code` (more details in the readme file there). The scripts should be run from within that folder.
- The model predictions are in `predictions` (one subfolder per model). The original predictions are in the TSV files; the TXT files contain the pure text so as to be directly comparable with the files in `data_processed/pure_text`. **Important:** The TSV files contain older versions of the reference transcriptions. These older references are ignored when calculating the ASR scores.
- The ASR scores (WER, CER, BLEU) are in `scores`. The files ending with `zeroshot.tsv` contain the results tables (results averaged over sentences), and the files ending with `zeroshot_detailed.tsv` list the scores for each sentence.
- The annotation guidelines/descriptions and the data statement are in the PDF `data-statement_annotation-guidelines.pdf`.
