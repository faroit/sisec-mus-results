# Generate Figures

## Paper Plots

These scripts were used to generate the plots for the [official SiSEC 2016 Paper](https://link.springer.com/chapter/10.1007%2F978-3-319-53547-0_31).

### Boxplots

![vocalssdr](https://user-images.githubusercontent.com/72940/31861668-8cf3c236-b731-11e7-82a6-b04e0697272b.png)

To generate a single boxplot for a specific target use the `generate_boxplot.py` script.

```
python figures/generate_boxplot.py sisec_mus_2017.pandas --target vocals
```

#### Boxplots Vocals/Accompaniment

![evaluation](https://user-images.githubusercontent.com/72940/31861667-8aeebc98-b731-11e7-8258-fac2074d5d52.png)

To reproduce the vocal/accompaniment plot from the paper, run the `figures/generate_boxplot_va.py` script

```
python figures/generate_boxplot_va.py sisec_mus_2017.pandas
```

#### Statistical evaluation – Pairwise Comparisons

![wilcox_voc_sdr](https://user-images.githubusercontent.com/72940/31861669-8ee0a9e2-b731-11e7-9d71-32d0a6f81ddd.png)

```
python figures/generate_stats.py sisec_mus_2017.pandas
```
