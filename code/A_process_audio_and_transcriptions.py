#!/usr/bin/env python3

from pydub import AudioSegment
from glob import glob
import os
import shutil


for target_dir in ["../data_processed/audio",
                   "../data_processed/transcriptions"]:
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)


german_test = ["brumilla", "geschichten", "hummel"]
german_dev = []


for filepath in sorted(glob("../transcriptions_*/*.tsv")):
    print(filepath)
    filename = filepath.split("/")[-1]
    filename = filename[:-1 * len("-trans-mw.tsv")]
    print(filename)
    standard_german = False
    try:
        story_name, dialect = filename.split("-mundart-")
    except ValueError:
        # Some filenames aren't formatted according to the 
        # {title}-mundart-{dialect}.tsv pattern
        if filename == "kiesel-liesel-liesel-als-spionin":
            story_name = filename
            dialect = "niederbayern"
        elif filename == "241123_1855_Betthupferl---Gute-Nacht-Geschichten-fue_Das-Passauer-Donaunixerl-Die-Breze--Mundart":
            story_name = "das-passauer-donaunixerl-die-breze"
            dialect = "niederbayern"
        elif filename == "250111_0000_Betthupferl---Gute-Nacht-Geschichten-fue_Das-Passauer-Donaunixerl-II-Der-Baldriantee":
            story_name = "das-passauer-donaunixerl-der-baldriantee"
            dialect = "niederbayern"
        elif filename == "W0276608-strassenmusik":
            story_name = "das-passauer-donaunixerl-strassenmusik"
            dialect = "niederbayern"
        elif filename == "W0399783-frisur-und-natur":
            story_name = "seppls-erlebnisse-frisur-und-natur"
            dialect = "niederbayern"
        elif filename == "W0325803-der-kleine-fuchs":
            story_name = "fanny-fuchs-der-kleine-fuchs"
            dialect = "oberbayern"
        elif filename == "W0276592-mit-einem-fischotter-baden":
            story_name = "fanny-fuchs-mit-einem-fischotter-baden"
            dialect = "oberbayern"
        elif filename == "W0412462-die-zauberin":
            story_name = "das-maerchenbett-die-zauberin"
            dialect = "oberbayern"
        elif filename == "W0412455-der-zauberer":
            story_name = "das-maerchenbett-der-zauberer"
            dialect = "oberbayern"
        elif filename == "W0414849-die-babykatz":
            story_name = "as-gloine-freilein-trudi-traudi-die-babykatz"
            dialect = "oberpfalz"
        elif filename == "W0414851-das-hofhundjubilaeum":
            story_name = "as-gloine-freilein-trudi-traudi-das-hofhundjubilaeum"
            dialect = "oberpfalz"
        elif filename == "W0399950-gittis-geburtsdooch":
            story_name = "as-gloine-freilein-trudi-traudi-gittis-geburtsdooch"
            dialect = "oberpfalz"
        elif filename == "W0399949-da-willi":
            story_name = "as-gloine-freilein-trudi-traudi-da-willi"
            dialect = "oberpfalz"
        elif filename == "W0399384-meine-oma":
            story_name = "eine-seltsame-kindheit-an-der-pegnitz-meine-oma"
            dialect = "mittelfranken"
        elif filename == "W0390615-meine-lehrerin":
            story_name = "eine-seltsame-kindheit-an-der-pegnitz-meine-lehrerin"
            dialect = "mittelfranken"
        elif filename == "W0298173-als-leopardenfledermaus":
            story_name = "beppo-die-burgfledermaus-als-leopardenfledermaus"
            dialect = "mittelfranken"
        elif filename == "W0398732-nachts-am-teich":
            story_name = "lilu-laemmle-nachts-am-teich"
            dialect = "unterfranken"
        elif filename == "W0398733-das-alpaka":
            story_name = "lilu-laemmle-das-alpaka"
            dialect = "unterfranken"
        elif filename == "W0272874-eine-tafel-schokolade":
            story_name = "das-kleine-kaenguru-eine-tafel-schokolade"
            dialect = "oberfranken"
        elif filename == "W0528180-die-geheimnisvolle-tasche":
            story_name = "im-gasthaus-zum-blauen-storch-die-geheimnisvolle-tasche"
            dialect = "oberfranken"
        elif filename == "W0277054-wura":
            story_name = "grischdiene-die-schwaebische-stubenfliege-wura"
            dialect = "schwaben"
        elif filename == "W0276573-moiadibbl":
            story_name = "grischdiene-die-schwaebische-stubenfliege-moiadibbl"
            dialect = "schwaben"
        elif filename == "W0256386-haeschniggl":
            story_name = "grischdiene-die-schwaebische-stubenfliege-haeschniggl"
            dialect = "schwaben"
        elif "transcriptions_standard_german" in filepath:
            standard_german = True
            if filename == "240219_1855_Betthupferl---Gute-Nacht-Geschichten-fue_Die-geheime-Cofi-Bande-I-15-Federmaeppchen":
                story_name = "die-geheime-cofi-bande-federmaeppchen"
            elif filename == "240325_0000_Betthupferl---Gute-Nacht-Geschichten-fue_Bubu-weltbester-Freund-und-Kuscheltier-X-15":
                story_name = "bubu-weltbester-freund-und-kuscheltier-schon-so-gross"
            elif filename == "240903_0000_Betthupferl---Gute-Nacht-Geschichten-fue_Das-Blumenmaedchen-I-25-Die-schnarchende-En":
                story_name = "das-blumenmaedchen-die-schnarchende-ente"
            else:
                story_name = filename
            in_test = False
            for story_pfx in german_test:
                if story_name.startswith(story_pfx):
                    in_test = True
                    break
            if in_test:
                dialect = "hochdeutschtest"
            else:
                in_dev = False
                for story_pfx in german_dev:
                    if story_name.startswith(story_pfx):
                        in_dev = True
                        break
                if in_dev:
                    dialect = "hochdeutschdev"
                else:
                    dialect = "hochdeutschtrain"
        else:
            print("/!\\ couldn't parse filename")
            break
    dialect = dialect.split("-")[0]
    if (not dialect.startswith("hochdeutsch")) and "transcriptions_standard_german" in filepath:
        # Std German sentences from stories otherwise told in a dialect
        standard_german = True
        dialect = "hochdeutschdial"

    entries = []
    with open(filepath) as f:
        for line in f:
            cells = line.split("\t")
            speaker, lang = cells[0].strip().split("-")
            transcription = cells[3].strip()
            start = float(cells[4].strip())
            end = float(cells[5].strip())
            if standard_german:
                entries.append([speaker, lang, start, end, "", transcription])
            elif lang != "deu":
                entries.append([speaker, lang, start, end, transcription])
            else:
                entries[-1].append(transcription)

    audio_story = AudioSegment.from_wav(f"../audio/{filename}.wav")

    with open(f"../data_processed/transcriptions/{story_name}_{dialect}.tsv",
              "w") as f:
        f.write("INDEX\tSPEAKER\tDIALECT\tTRANSCRIPTION_DIALECT\tTRANSCRIPTION_GERMAN\tAUDIO_DURATION\tFILEPATH\n")
        for idx, entry in enumerate(entries):
            f.write("\t".join((str(idx), entry[0], dialect,
                               entry[4], entry[5])))
            audio_filename = f"data_processed/audio/{story_name}_{dialect}_{idx}.wav"
            start, stop = entry[2], entry[3]
            f.write(f"\t{stop - start}")
            f.write(f"\t{audio_filename}\n")
            audio_sentence = audio_story[start * 1000:stop * 1000]
            audio_sentence.export(f"../{audio_filename}", format="wav")
