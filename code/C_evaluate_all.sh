#!/usr/bin/env bash

for pred_folder in ../predictions/*
do
	echo ${pred_folder}
	./C_evaluate_preds.py ${pred_folder}
done
