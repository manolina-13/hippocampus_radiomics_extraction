import nibabel as nib
import os

img_dir = 'imagesTr'
lbl_dir = 'labelsTr'

for f in os.listdir(img_dir):
    if not f.endswith('_0000.nii.gz'):
        continue
    case_id = f.replace('_0000.nii.gz', '')
    img = nib.load(os.path.join(img_dir, f)).shape
    lbl = nib.load(os.path.join(lbl_dir, f.replace('_0000', ''))).shape
    if img != lbl:
        print(f"Shape mismatch for {case_id}: Image {img}, Label {lbl}")

