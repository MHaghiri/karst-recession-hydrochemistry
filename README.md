# Recession-Based Karst Development Classes and Their Hydrogeochemical and Isotopic Signatures

**Dolomitic hard-rock aquifers of the northern Alborz, Iran**

![Study area and geology](docs/Fig_1.png)

*Figure 1. Study area: location within Iran, geological map of the hard-rock formations of northern Alborz Province with the 19 sampling points (springs S1&ndash;S11, qanats Q1&ndash;Q4, wells W1&ndash;W4), and a simplified karst-development map.*

---

## About

This repository contains the analysis and plotting code for the study:

> Haghiri, M., Habibi, S., & Izadi, I. *Linking Recession-Based Karst Development Classes to Hydrogeochemical and Isotopic Signatures in Dolomitic Hard-Rock Aquifers (Alborz, Iran).* Hydrogeology Journal (in review).

Recession analysis is widely used to classify karst development, but whether these hydrodynamic classes correspond to distinct hydrogeochemical and isotopic signatures has rarely been tested. The study examines this link across **11 springs, 4 qanats and 4 wells** in **2,057 km&sup2;** of dolomitic hard-rock formations in the Alborz Range.

### Key findings

- **Hydrodynamics.** Maillet recession analysis gives recession coefficients of 0.0014&ndash;0.0159 day<sup>&minus;1</sup> and dynamic storage of 10.9&ndash;1,087.2 &times;10<sup>6</sup> m<sup>3</sup>, classifying sources into five karst-development classes (Class I conduit-dominant to Class V diffuse-flow).
- **Hydrochemistry.** Mg&ndash;HCO<sub>3</sub> facies dominate 17 of 19 samples; PCA confirms Mg<sup>2+</sup>&ndash;HCO<sub>3</sub><sup>&minus;</sup> control (PC1 = 69.9%), identifying dolomite dissolution as the first-order process.
- **Linking the two.** Conduit-dominated sources show lower TDS, more negative saturation indices and greater isotopic variability; diffuse-flow sources show higher mineralization and stable &delta;<sup>18</sup>O (&minus;10 to &minus;7&permil;), consistent with longer residence times.
- **Recharge.** Stable isotopes indicate recharge dominated by high-elevation snowmelt with minimal evaporation.

## Methods covered by the code

| Figure | Analysis |
|---|---|
| Fig. 2 | Discharge hydrographs, Maillet recession curves, dynamic storage, drying time, Mangin-type V&ndash;&alpha; plot |
| Fig. 3 | Piper, Durov and Schoeller diagrams; water-type classification |
| Fig. 4 | Gibbs diagrams, bivariate ion-ratio plots, chloro-alkaline indices |
| Fig. 5 | Pearson correlation, PCA biplot and scree plot, Ward cluster analysis |
| Fig. 6 | Mineral saturation indices (calcite, dolomite, gypsum, halite) |
| Fig. 7 | Interpolated major-ion maps, hydrochemical facies map, seasonal EC change |
| Figs. 8&ndash;9 | &delta;<sup>2</sup>H&ndash;&delta;<sup>18</sup>O relationships, meteoric water lines, d-excess, altitude effect |
| Fig. 10 | Ion-ratio process maps, isotope maps, Water Quality Index |

Figure 1 (maps) was prepared in GIS software and is not produced by these scripts.

## Repository contents

```
.
|-- code/            Python scripts, one per manuscript figure
|-- data/            input data (not included; see below)
|-- docs/            images used in this README
|-- requirements.txt Python dependencies
|-- LICENSE
`-- README.md
```

### Scripts

| Script |
|---|
| [`code/Fig10_process_maps.py`](code/Fig10_process_maps.py) |
| [`code/Fig2_hydrodynamic.py`](code/Fig2_hydrodynamic.py) |
| [`code/Fig3_geochemical_classification.py`](code/Fig3_geochemical_classification.py) |
| [`code/Fig4_ion_ratio_process.py`](code/Fig4_ion_ratio_process.py) |
| [`code/Fig5_statistical_analysis.py`](code/Fig5_statistical_analysis.py) |
| [`code/Fig6_saturation_index.py`](code/Fig6_saturation_index.py) |
| [`code/Fig7_hydrochemical_maps.py`](code/Fig7_hydrochemical_maps.py) |
| [`code/Fig8_Fig9_isotopes.py`](code/Fig8_Fig9_isotopes.py) |

## Running the code

1. Install Python 3.9 or later, then the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Place the input files in `data/` (see *Data availability*).

3. Each script has a **USER SETTINGS** block at the top. Set the input paths
   (`DATA_PATH`, `EXCEL_PATH`, `ISOTOPE_XLSX`, `SHAPEFILE_PATH`, ...) and the
   output folder (`OUT_DIR` / `OUTPUT_DIR`) to locations on your machine, then run, e.g.:

   ```bash
   python code/Fig2_hydrodynamic.py
   ```

   Each script writes its figure as a vector PDF and a PNG.

## Data availability

The field and laboratory data (discharge records, major-ion chemistry, stable
isotopes and the study-area boundary) are not included in this repository.
They are available from the corresponding author on reasonable request.

## Citation

If you use this code, please cite the article (full reference to be added on publication):

```
Haghiri M, Habibi S, Izadi I (in review) Linking recession-based karst development
classes to hydrogeochemical and isotopic signatures in dolomitic hard-rock aquifers
(Alborz, Iran). Hydrogeology Journal.
```

## Authors

- **Mohammad Haghiri** (corresponding author), Department of Earth and Environmental Sciences, University of Illinois Chicago &mdash; mhaghi2@uic.edu
- **Sasan Habibi**, Zamin Kavosh Oxin Consulting Engineers Company, Tehran
- **Ibrahim Izadi**

## License

The code is released under the MIT License (see [LICENSE](LICENSE)).
