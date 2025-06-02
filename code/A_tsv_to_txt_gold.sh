#!/usr/bin/env bash

rm -r ../data_processed/pure_text/
mkdir ../data_processed/pure_text/

# Files for the individual dialects/regions
for dialect in mittelfranken niederbayern oberbayern oberfranken oberpfalz schwaben unterfranken ;
do
    echo $dialect
    # Get the 4th/5th column (cut), delete the header lines (sed)
    cat ../data_processed/transcriptions/*${dialect}* | cut -f4 | sed '/TRANSCRIPTION_DIALECT/d' > ../data_processed/pure_text/${dialect}_gold_dial.txt
    cat ../data_processed/transcriptions/*${dialect}* | cut -f5 | sed '/TRANSCRIPTION_GERMAN/d' > ../data_processed/pure_text/${dialect}_gold_deu.txt
    # Normalization: remove punctuation and case
    cat ../data_processed/pure_text/${dialect}_gold_dial.txt | tr -d [:punct:] | tr '[:upper:]' '[:lower:]' > ../data_processed/pure_text/${dialect}_goldnorm_dial.txt
    cat ../data_processed/pure_text/${dialect}_gold_deu.txt | tr -d [:punct:] | tr '[:upper:]' '[:lower:]' > ../data_processed/pure_text/${dialect}_goldnorm_deu.txt
done

# All dialects/regions in one file
cat ../data_processed/pure_text/*gold_dial.txt > ../data_processed/pure_text/alldialects_gold_dial.txt
cat ../data_processed/pure_text/*gold_deu.txt > ../data_processed/pure_text/alldialects_gold_deu.txt
cat ../data_processed/pure_text/*goldnorm_dial.txt > ../data_processed/pure_text/alldialects_goldnorm_dial.txt
cat ../data_processed/pure_text/*goldnorm_deu.txt > ../data_processed/pure_text/alldialects_goldnorm_deu.txt

# Repeat for the German samples
for dialect in hochdeutschtrain hochdeutschdev hochdeutschtest hochdeutschdial ;
do
    echo $dialect
    cat ../data_processed/transcriptions/*${dialect}* | cut -f5 | sed '/TRANSCRIPTION_GERMAN/d' > ../data_processed/pure_text/${dialect}_gold_deu.txt
    cat ../data_processed/pure_text/${dialect}_gold_deu.txt | tr -d [:punct:] | tr '[:upper:]' '[:lower:]' > ../data_processed/pure_text/${dialect}_goldnorm_deu.txt
done

cat ../data_processed/pure_text/hochdeutschdial_gold_deu.txt ../data_processed/pure_text/hochdeutschtest_gold_deu.txt > ../data_processed/pure_text/allhochdeutsch_gold_deu.txt
cat ../data_processed/pure_text/hochdeutschdial_goldnorm_deu.txt ../data_processed/pure_text/hochdeutschtest_goldnorm_deu.txt > ../data_processed/pure_text/allhochdeutsch_goldnorm_deu.txt
