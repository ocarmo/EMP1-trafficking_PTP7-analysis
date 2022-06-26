import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger
from statsmodels.sandbox.stats.multicomp import MultiComparison
from statannotations.Annotator import Annotator

logger.info('Import OK')

input_folder = 'python_results/summary_results/'
output_folder = 'python_results/plotting/'

# initialize python_results folders
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
    
# ---------------- imports ----------------
# csv generated from 'Co-occurrents_C2-C3.ijm' FIJI Macro
cooccur_df = pd.read_csv(f'{input_folder}cooccur_df.csv').drop('Unnamed: 0', axis=1)

# ---------------- plotting ----------------
c = 'w'
hpi_order = cooccur_df.hpi.unique().tolist()
hpi_prism_colors = ['k', '#FF0C6B', '#3E9798', '#462F73']
hpi_palette = dict(zip(hpi_order, hpi_prism_colors))

# set y/x-max to max value in whole dataframe plus 10
perc_both_max = (cooccur_df.perc_both.max() + 10)

for (cellline_serum), cellline_serum_df in cooccur_df.groupby(['cell_line', 'antibody']):
    # must sort df to avoid weird bug
    cellline_serum_df = cellline_serum_df.sort_values(by=['hpi'])

    # calculate mean per cellline_serum_df
    mean_col = cellline_serum_df.groupby(['date_fill', 'hpi'])[
        ['perc_both']].mean()
    mean_col = mean_col.reset_index().sort_values(by=['hpi'])

    # stats playground
    mc = MultiComparison(mean_col['perc_both'], mean_col['hpi'])
    mc_table = mc.tukeyhsd()
    mc_df = pd.DataFrame(
        data=mc_table._results_table.data[1:], columns=mc_table._results_table.data[0])
    mc_df_trim = mc_df[mc_df['reject'] == True][['group1', 'group2', 'p-adj']]
    mc_df_true_print = mc_df_trim.to_string(index=False)
    if 'Empty' in mc_df_true_print:
        mc_df_true_print = ''

    # start plotting
    fig, ax = plt.subplots()
    fig.set_size_inches(5.6, 2.4)

    # plot all data
    ax = sns.stripplot(
        y='hpi',
        x='perc_both',
        hue='hpi',
        data=cellline_serum_df, size=6, alpha=0.2,  palette=hpi_palette
    )

    # plot mean values
    sns.boxplot(y=mean_col['hpi'],
                x=mean_col['perc_both'], boxprops=dict(facecolor=c), palette=hpi_palette, ax=ax,)
    sns.stripplot(
        y='hpi',
        x='perc_both',
        hue='hpi',
        data=mean_col, size=6, alpha=1, ax=ax, palette=hpi_palette, linewidth=1
    )

    # format axes
    ax.set_xlim([0, perc_both_max])

    # Hide the right and top spines
    sns.despine(top=True, right=True)

    # remove extra legend handles
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:4], labels[:4], title=f'{cellline_serum}', bbox_to_anchor=(
        1, 1.02), loc='upper left')

    # adjust y axis label
    if cellline_serum[0] == 'oc67':
        ax.set_xlabel(f'HA & {cellline_serum[1]} co-occurrence (%)')
    else:
        ax.set_xlabel(f'GFP & {cellline_serum[1]} co-occurrence (%)')

    # print any significant differences from Tukey HSD
    ax.text(0.78, 0.3, mc_df_true_print, fontsize=8,
            transform=plt.gcf().transFigure)

    # fit to subplot and save
    plt.tight_layout()
    plt.savefig(
        f'{output_folder}{cellline_serum[0]}-{cellline_serum[1]}.png', format='png', dpi=300)
