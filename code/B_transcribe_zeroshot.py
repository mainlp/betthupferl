#!/usr/bin/env python3

import sys
import os
from glob import glob
import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration, Wav2Vec2ForCTC, Wav2Vec2Processor


def preprocess(path, whisper_sr):
    audio, orig_sr = librosa.load(path, sr=None)
    # Remove the occasional bit of trailing silence
    trimmed, _ = librosa.effects.trim(audio, top_db=30)
    # Resample -- Whisper requires a sampling rate of 16k Hz
    resampled = librosa.resample(trimmed, orig_sr=orig_sr, target_sr=whisper_sr)
    return resampled


def transcribe_whisper(
        audio, lang, task,
        processor, model, device):
    # 'audio' can be a single clip, or a list of audio clips
    if lang:
        forced_decoder_ids = processor.get_decoder_prompt_ids(
            language=lang, task=task)
    else:
        forced_decoder_ids = None
    input_features = processor(
        audio,
        sampling_rate=processor.feature_extractor.sampling_rate,
        return_tensors="pt").input_features
    input_features = input_features.to(device)
    predicted_ids = model.generate(
        input_features, forced_decoder_ids=forced_decoder_ids)
    transcriptions = processor.batch_decode(
        predicted_ids, skip_special_tokens=True)
    return transcriptions


def transcribe_mms(
        audio, processor, model, device):
    inputs = processor(
        audio,
        sampling_rate=processor.feature_extractor.sampling_rate,
        return_tensors="pt",
        padding=True,
    )
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model(
            inputs.input_values,
            attention_mask=inputs.attention_mask).logits
    predicted_ids = torch.argmax(outputs, dim=-1)
    transcriptions = processor.batch_decode(
        predicted_ids)
    return transcriptions


def get_files_and_metadata(in_file):
    print("Reading " + in_file)
    given_details = []
    audios = []
    with open(in_file) as f:
        first_line = True
        for line in f:
            if first_line:
                first_line = False
                continue
            idx, speaker, dialect, trans_deu, trans_dial, _, filepath = line.strip().split("\t")
            given_details.append(
                [idx, speaker, dialect, trans_deu, trans_dial])
            audios.append(preprocess(
                "../" + filepath, processor.feature_extractor.sampling_rate))
    return audios, given_details


def write_output(out_folder, in_file,
                 given_details, transcriptions):
    out_file = out_folder + "/" + in_file.split("/")[-1]
    print("Writing transcriptions to " + out_file)
    with open(out_file, "w") as f:
        f.write("INDEX\tSPEAKER\tDIALECT\tTRANSCRIPTION_DIALECT\tTRANSCRIPTION_GERMAN\tTRANSCRIPTION_MODEL\n")
        for details, trans in zip(given_details, transcriptions):
            f.write("\t".join(details))
            f.write("\t" + trans.strip() + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("transcribe_zeroshot.py MODEL_NAME GOLD_FILENAME_PREFIX")
        print("Example:")
        print("transcribe_zeroshot.py openai/whisper-medium ../data_processed/transcriptions/billy")
        sys.exit(1)

    model_name = sys.argv[1]
    glob_pattern = sys.argv[2] + "*"
    model_details_sfx = "_zeroshot"

    if "whisper" in model_name:
        target_lang = "german"  # no dialects available
        task = "transcribe"  # 'translate' only creates English output
        processor = WhisperProcessor.from_pretrained(model_name)
        model = WhisperForConditionalGeneration.from_pretrained(model_name)
    elif "mms" in model_name or "wav2vec2" in model_name:
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name)
        if "mms" in model_name:
            target_lang = "deu"  # no dialects available
            processor.tokenizer.set_target_lang(target_lang)
            model.load_adapter(target_lang)
    else:
        print("Unknown model:")
        print(model_name)
        sys.exit(1)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model = model.to(device)

    out_folder = "../predictions/" + model_name.replace("/", "-") + model_details_sfx
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    print(glob(glob_pattern))
    for in_file in glob(glob_pattern):
        audios, given_details = get_files_and_metadata(in_file)
        if "whisper" in model_name:
            transcriptions = transcribe_whisper(
                audios, target_lang, task, processor, model, device)
        elif "mms" in model_name or "wav2vec2" in model_name:
            transcriptions = transcribe_mms(
                audios, processor, model, device)
        write_output(out_folder, in_file,
                     given_details, transcriptions)
