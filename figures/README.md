# Generate Figures

## Paper Plots

These scripts were used to generate the plots for the [official SiSEC 2016 Paper](https://link.springer.com/chapter/10.1007%2F978-3-319-53547-0_31).

### Boxplots

To generate a single boxplot for a specific target use the `generate_boxplot.py` script.

```
python figures/generate_boxplot.py sisec_mus_2017.pandas --target vocals
```

#### Boxplots Vocals/Accompaniment

To reproduce the vocal/accompaniment plot from the paper, run the `figures/generate_boxplot_va.py` script

```
python figures/generate_boxplot_va.py sisec_mus_2017.pandas
```

#### Statistical evaluation – Pairwise Comparisons

```
python figures/generate_stats.py sisec_mus_2017.pandas
```
