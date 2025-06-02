#!/usr/bin/env python3

from glob import glob
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import numpy as np


def corr_with_pval(df, method):
    # Based on https://stackoverflow.com/a/49040342 CC BY-SA 4.0
    r = df.corr(method=method)
    if method == "pearson":
        pval = df.corr(
            method=lambda x, y: pearsonr(x, y)[1]) - np.eye(*r.shape)
    elif method == "spearman":
        pval = df.corr(
            method=lambda x, y: spearmanr(x, y)[1]) - np.eye(*r.shape)
    else:
        print("Unknown correlation method", method)
    p = pval.applymap(
        lambda x: ''.join(['*' for t in [.05, .01, .001] if x < t]))
    return(r.round(4).astype(str) + p)


def read_eval_tsv(filename):
    df = pd.read_csv(filename, sep="\t", index_col=0)

    def map_scores(x):
        try:
            return int(str(x)[0])
        except ValueError:
            return np.nan

    df["meaning_scores"] = df["Bedeutung"].apply(map_scores)
    df["style_scores"] = df["Flüssigkeit"].apply(map_scores)
    return df


# Correlations between metrics

dfs = []
for file in glob("../scores/*detailed.tsv"):
    print(file)
    df = pd.read_csv(file, sep='\t', quoting=3, header=0)
    dfs.append(df)
df_all = pd.concat(dfs)

corr_with_pval(df_all, method='pearson').to_csv(
    "../analysis/correlations_metrics_all-models_pearson.tsv", sep="\t")
corr_with_pval(df_all, method='spearman').to_csv(
    "../analysis/correlations_metrics_all-models_spearman.tsv", sep="\t")

df_pred = pd.read_csv(
    "../scores/openai-whisper-large-v3_zeroshot_detailed.tsv",
    sep="\t", quoting=3, index_col=0)

corr_with_pval(df_pred, method='pearson').to_csv(
    "../analysis/correlations_metrics_whisper-large-v3_pearson.tsv", sep="\t")
corr_with_pval(df_pred, method='spearman').to_csv(
    "../analysis/correlations_metrics_whisper-large-v3_spearman.tsv", sep="\t")

# Correlations for human eval. Note that these only deal with the
# human-annotated subset!

df_c = read_eval_tsv("../analysis/sentence_eval_c.tsv")
df_f = read_eval_tsv("../analysis/sentence_eval_f.tsv")
df_e = read_eval_tsv("../analysis/sentence_eval_e.tsv")

df_annos = df_c[["meaning_scores", "style_scores"]].rename(
    columns={"meaning_scores": "meaning_scores_c",
             "style_scores": "style_scores_c"})
df_annos = df_annos.join(
    df_e[["meaning_scores", "style_scores"]],
    how="outer").rename(
    columns={"meaning_scores": "meaning_scores_e",
             "style_scores": "style_scores_e"})
df_annos = df_annos.join(
    df_f[["meaning_scores", "style_scores"]],
    how="outer").rename(
    columns={"meaning_scores": "meaning_scores_f",
             "style_scores": "style_scores_f"})

df_all = df_pred.join(
    df_annos,
    how="inner")

df_all["total_c"] = 0.5 * (
    df_all["meaning_scores_c"] + df_all["style_scores_c"])
df_all["total_e"] = 0.5 * (
    df_all["meaning_scores_e"] + df_all["style_scores_e"])
df_all["total_f"] = 0.5 * (
    df_all["meaning_scores_f"] + df_all["style_scores_f"])


corr_with_pval(df_all, method='pearson').to_csv(
    "../analysis/correlations_human_eval_pearson.tsv", sep="\t")
corr_with_pval(df_all, method='spearman').to_csv(
    "../analysis/correlations_human_eval_spearman.tsv", sep="\t")

for score in [
    "meaning_scores_c", "meaning_scores_e", "meaning_scores_f",
    "style_scores_c", "style_scores_e", "style_scores_f",
]:
    print(score, "(mean, stdev, nr)")
    print(f"{df_annos[score].mean():.1f}\t{df_annos[score].std():.1f}\t{len(df_annos[score].dropna())}")
    
for score in ["total_c", "total_e", "total_f",]:
    print(score, "(mean, stdev, nr)")
    print(f"{df_all[score].mean():.1f}\t{df_all[score].std():.1f}\t{len(df_all[score].dropna())}")

df_meaning_all = pd.concat(
    [df_annos["meaning_scores_c"].dropna(),
     df_annos["meaning_scores_e"].dropna(),
     df_annos["meaning_scores_f"].dropna()])
print("meaning (all)", "(mean, stdev, nr)")
print(f"{df_meaning_all.mean():.1f}\t{df_meaning_all.std():.1f}\t{len(df_meaning_all)}")
df_style_all = pd.concat(
    [df_annos["style_scores_c"].dropna(),
     df_annos["style_scores_e"].dropna(),
     df_annos["style_scores_f"].dropna()])
print("style (all)", "(mean, stdev, nr)")
print(f"{df_style_all.mean():.1f}\t{df_style_all.std():.1f}\t{len(df_style_all)}")
df_total_all = pd.concat(
    [df_all["total_c"].dropna(),
     df_all["total_e"].dropna(),
     df_all["total_f"].dropna()])
print("total (all)", "(mean, stdev, nr)")
print(f"{df_total_all.mean():.1f}\t{df_total_all.std():.1f}\t{len(df_total_all)}")
