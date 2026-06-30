# Hippocampus Radiomics Feature Extraction

Automated extraction of 3D radiomic features from the **Medical Segmentation Decathlon (MSD) Dataset105 — Hippocampus** using [PyRadiomics](https://pyradiomics.readthedocs.io/). The pipeline processes MRI images paired with multi-label segmentation masks and extracts comprehensive shape, intensity, and texture features separately for the **Anterior** and **Posterior** hippocampal regions.

---

## Project Structure

```
Dataset105_Hippocampus/
├── extract_hippocampus_radiomics.py   # Main extraction script
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
├── imagesTr/                          # MRI images (*_0000.nii.gz)
├── labelsTr/                          # Segmentation masks (*.nii.gz)
│   │                                  #   0 = Background
│   │                                  #   1 = Anterior Hippocampus
│   │                                  #   2 = Posterior Hippocampus
└── hippocampus_radiomics.csv          # Output: extracted features
```

---

## How It Works

For each patient the script:

1. **Reads** the MRI image and its multi-label mask
2. **Z-score normalises** the image (`sitk.Normalize`) — standard for MRI intensity
3. **Checks** voxel spacing consistency across the dataset; if inconsistent, resamples to **1x1x1 mm**
4. **Creates two binary masks** from the multi-label mask:
   - `mask_anterior` — pixels where `label == 1`
   - `mask_posterior` — pixels where `label == 2`
5. **Runs PyRadiomics** independently on each binary mask
6. **Saves** 2 rows per patient (Anterior + Posterior) to a single CSV

---

## Server Paths

| Path | Description |
|---|---|
| Dataset | `/data1/students/manolina/dataset/nnUNet_raw/Dataset105_Hippocampus/` |
| Images | `/data1/students/manolina/dataset/nnUNet_raw/Dataset105_Hippocampus/imagesTr/` |
| Masks | `/data1/students/manolina/dataset/nnUNet_raw/Dataset105_Hippocampus/labelsTr/` |
| Output CSV | `/data1/students/manolina/hippocampus_radiomics.csv` |

---

## Installation and Usage

### 1. Activate Environment

```bash
conda activate manolina
```

### 2. Install Dependencies

```bash
# Recommended: conda (pre-built binaries, no compiler needed)
conda install -c conda-forge -c radiomics numpy SimpleITK pandas pyradiomics -y

# Alternative: pip from GitHub (requires gcc on Linux)
pip install setuptools wheel
pip install git+https://github.com/Radiomics/pyradiomics.git@master
```

### 3. Run Extraction

```bash
cd /data1/students/manolina/
python extract_hippocampus_radiomics.py
```

### 4. Expected Output

```
Step 1: Checking voxel spacings across the dataset...
Unique Spacings Found: {(1.0, 1.0, 1.0)}
Voxel spacing is consistent. No resampling required by PyRadiomics.

Step 2: Starting extraction for Anterior and Posterior regions...
Processing: hippocampus_001
Processing: hippocampus_002
...
Extraction complete. Saved 400 rows to /data1/students/manolina/hippocampus_radiomics.csv
```

---

## Dependencies

| Package | Version Used | Purpose |
|---|---|---|
| `numpy` | 2.2.6 | Numerical operations |
| `SimpleITK` | 2.5.5 | Medical image I/O and processing |
| `pyradiomics` | 3.1.1 | Radiomic feature extraction |
| `pandas` | 2.3.3 | CSV output |

---

## Output CSV — hippocampus_radiomics.csv

| | Value |
|---|---|
| **Total Rows** | 401 (1 header + 400 data rows) |
| **Total Columns** | 131 |
| **Patients** | 200 patients (e.g., `hippocampus_107`, `hippocampus_004`) |
| **Rows per Patient** | 2 — one Anterior, one Posterior |

---

## Column Groups

### Identity Columns (2)

| Column | Meaning |
|---|---|
| `Patient` | Patient ID (e.g., `hippocampus_107`) |
| `Label_Region` | Which ROI: `Anterior` or `Posterior` hippocampus |

---

### Diagnostics Columns (22) — `diagnostics_*`

Metadata about the extraction run. Not actual features — safe to drop before ML.

| Column | Meaning |
|---|---|
| `diagnostics_Versions_*` | PyRadiomics, Numpy, SimpleITK, PyWavelet, Python versions |
| `diagnostics_Configuration_Settings` | Full extractor settings used (`binWidth=25`, etc.) |
| `diagnostics_Image-original_Hash` | MD5 of the input image (reproducibility check) |
| `diagnostics_Image-original_Spacing` | Voxel spacing e.g. `(1.0, 1.0, 1.0)` |
| `diagnostics_Image-original_Size` | Full image dimensions |
| `diagnostics_Image-original_Mean/Min/Max` | Intensity range of the whole image |
| `diagnostics_Mask-original_Hash` | MD5 of the binary mask |
| `diagnostics_Mask-original_BoundingBox` | Bounding box of the ROI `(x, y, z, w, h, d)` |
| `diagnostics_Mask-original_VoxelNum` | Number of voxels inside the mask |
| `diagnostics_Mask-original_VolumeNum` | Number of connected regions (should be 1) |
| `diagnostics_Mask-original_CenterOfMassIndex` | Voxel-space centre of ROI |
| `diagnostics_Mask-original_CenterOfMass` | Physical-space centre of ROI (in mm) |

---

### Shape Features (14) — `original_shape_*`

3D geometric properties of the ROI mask. Resolution-independent.

| Column | Meaning |
|---|---|
| `MeshVolume` / `VoxelVolume` | Volume in mm3 |
| `SurfaceArea` | Surface area in mm2 |
| `SurfaceVolumeRatio` | Compactness indicator |
| `Sphericity` | How sphere-like the shape is (1 = perfect sphere) |
| `Elongation` | Ratio of 2nd to 1st axis length |
| `Flatness` | Ratio of least to major axis |
| `LeastAxisLength` / `MinorAxisLength` / `MajorAxisLength` | PCA-derived axis lengths |
| `Maximum3DDiameter` | Longest diameter across any direction |
| `Maximum2DDiameter(Column/Row/Slice)` | Longest 2D diameter per plane |

---

### First-Order Features (18) — `original_firstorder_*`

Statistics of raw intensity values inside the mask (after Z-score normalization).

| Column | Meaning |
|---|---|
| `Mean`, `Median` | Central tendency of voxel intensities |
| `Minimum`, `Maximum`, `Range` | Intensity spread |
| `10Percentile`, `90Percentile`, `InterquartileRange` | Robust intensity spread |
| `Variance`, `RootMeanSquared` | Dispersion |
| `Skewness` | Asymmetry of intensity distribution |
| `Kurtosis` | Peakedness / tail weight |
| `Entropy` | Randomness of intensity values |
| `Uniformity` | Opposite of entropy — how uniform intensities are |
| `Energy` / `TotalEnergy` | Sum of squared intensities |
| `MeanAbsoluteDeviation` / `RobustMeanAbsoluteDeviation` | Average deviation from mean |

---

### Texture Feature Groups (75 total)

#### GLCM — 24 features (`original_glcm_*`)

Gray-Level Co-occurrence Matrix. Captures pairwise voxel intensity relationships (texture patterns).

Key features: `Contrast`, `Correlation`, `Homogeneity (Idm)`, `Entropy (JointEntropy)`, `Energy (JointEnergy)`, `Autocorrelation`, `ClusterShade`, `ClusterProminence`

#### GLDM — 14 features (`original_gldm_*`)

Gray-Level Dependence Matrix. Measures how dependent neighbouring voxels are on having similar intensities.

Key features: `DependenceEntropy`, `GrayLevelVariance`, `HighGrayLevelEmphasis`, `LowGrayLevelEmphasis`, `LargeDependenceEmphasis`, `SmallDependenceEmphasis`

#### GLRLM — 16 features (`original_glrlm_*`)

Gray-Level Run-Length Matrix. Measures consecutive voxel runs of the same intensity (directional texture).

Key features: `RunEntropy`, `LongRunEmphasis`, `ShortRunEmphasis`, `GrayLevelNonUniformity`, `RunLengthNonUniformity`, `RunPercentage`

#### GLSZM — 16 features (`original_glszm_*`)

Gray-Level Size Zone Matrix. Similar to GLRLM but for connected 3D zones instead of runs.

Key features: `ZoneEntropy`, `LargeAreaEmphasis`, `SmallAreaEmphasis`, `ZonePercentage`, `GrayLevelNonUniformity`

#### NGTDM — 5 features (`original_ngtdm_*`)

Neighbourhood Gray-Tone Difference Matrix. Captures local contrast and coarseness.

Key features: `Coarseness`, `Contrast`, `Busyness`, `Complexity`, `Strength`

---

## Recommended ML Preprocessing

```python
import pandas as pd

df = pd.read_csv("hippocampus_radiomics.csv")

# Drop diagnostic metadata columns (not features)
drop_cols = [c for c in df.columns if c.startswith('diagnostics_')]
df_ml = df.drop(columns=drop_cols)

# Remaining: 2 ID columns + 107 actual radiomic features
# Shape: (400, 109)
print(df_ml.shape)
print(df_ml[['Patient', 'Label_Region']].head())
```

---

## Extractor Settings

| Setting | Value | Rationale |
|---|---|---|
| `binWidth` | 25 | Histogram bin width for texture features |
| `resampledPixelSpacing` | None (auto) | Set to `[1,1,1]` if multiple spacings detected |
| `interpolator` | `sitkBSpline` | High-quality resampling |
| `normalize` | False (PyRadiomics) | Z-score normalisation done manually before extraction |

Note: Z-score normalization (`sitk.Normalize`) is applied before PyRadiomics runs, which is the recommended approach for MRI data where absolute intensities are scanner-dependent.

---

## References

- [PyRadiomics Documentation](https://pyradiomics.readthedocs.io/)
- [MSD Dataset105 — Hippocampus](http://medicaldecathlon.com/)
- [SimpleITK Documentation](https://simpleitk.readthedocs.io/)

---
## License

This project is distributed under the MIT License. See `LICENSE` for more information.

---
## Contact

Manolina Das - [GitHub Profile](https://github.com/manolina-13)
