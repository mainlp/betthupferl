#!/usr/bin/env bash

for model_dir in ../predictions/*/ ;
do
	echo ${model_dir}
	rm ${model_dir}*txt

	for dialect in mittelfranken niederbayern oberbayern oberfranken oberpfalz schwaben unterfranken ;
	do
	    echo $dialect
	    # Get the 6th column (cut) and delete the header lines (sed)
	    cat ${model_dir}*${dialect}* | cut -f6 | sed '/TRANSCRIPTION_MODEL/d' > ${model_dir}${dialect}_pred.txt
	     # Normalization: remove punctuation and case
    	cat ${model_dir}${dialect}_pred.txt | tr -d [:punct:] | tr '[:upper:]' '[:lower:]' > ${model_dir}${dialect}_prednorm.txt
	done

	cat ${model_dir}*_pred.txt > ${model_dir}alldialects_pred.txt
	cat ${model_dir}*_prednorm.txt > ${model_dir}alldialects_prednorm.txt

	# Repeat for German
	for dialect in hochdeutschtest hochdeutschdial ;
	do
	    echo $dialect
	    cat ${model_dir}*${dialect}* | cut -f6 | sed '/TRANSCRIPTION_MODEL/d' > ${model_dir}${dialect}_pred.txt
    	cat ${model_dir}${dialect}_pred.txt | tr -d [:punct:] | tr '[:upper:]' '[:lower:]' > ${model_dir}${dialect}_prednorm.txt
	done

	cat ${model_dir}hochdeutsch*_pred.txt > ${model_dir}allhochdeutsch_pred.txt
	cat ${model_dir}hochdeutsch*_prednorm.txt > ${model_dir}allhochdeutsch_prednorm.txt
done
