import os
import nibabel as nib

base = "/home/koustav/modelComparison/nnunetTests/nnUNetv2_raw/Dataset105_Hippocampus"

for folder in ["imagesTr", "labelsTr"]:
    print(f"Checking {folder}")
    for fname in os.listdir(os.path.join(base, folder)):
        path = os.path.join(base, folder, fname)
        try:
            nib.load(path)
        except Exception as e:
            print(f"Failed to load {path}: {e}")

