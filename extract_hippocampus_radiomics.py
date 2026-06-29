import os
import SimpleITK as sitk
from radiomics import featureextractor
import pandas as pd
import numpy as np

def extract_features():
    # 1. Initialize the extractor
    # You can configure settings here. We enable shape features explicitly 
    # since they are critical for small structures like the hippocampus.
    settings = {
        'binWidth': 25,
        'resampledPixelSpacing': None,  # Will update if spacing differs
        'interpolator': sitk.sitkBSpline
    }
    
    extractor = featureextractor.RadiomicsFeatureExtractor(**settings)
    
    # Alternatively, you can use:
    # extractor.disableAllFeatures()
    # extractor.enableFeatureClassByName('shape')
    # extractor.enableFeatureClassByName('firstorder')
    # extractor.enableFeatureClassByName('glcm')
    # extractor.enableFeatureClassByName('glrlm')
    # extractor.enableFeatureClassByName('glszm')
    
    results = []
    
    # Server paths
    base_dir  = "/data1/students/manolina/dataset/nnUNet_raw/Dataset105_Hippocampus"
    images_dir = "/data1/students/manolina/dataset/nnUNet_raw/Dataset105_Hippocampus/imagesTr"
    labels_dir = "/data1/students/manolina/dataset/nnUNet_raw/Dataset105_Hippocampus/labelsTr"
    output_dir = "/data1/students/manolina"
    
    print("Step 1: Checking voxel spacings across the dataset...")
    spacings = set()
    for patient_file in os.listdir(labels_dir):
        if not patient_file.endswith(".nii.gz"):
            continue
        
        img_file = patient_file.replace(".nii.gz", "_0000.nii.gz")
        img_path = os.path.join(images_dir, img_file)
        
        if os.path.exists(img_path):
            img = sitk.ReadImage(img_path)
            # Round spacing slightly to avoid float precision issues in set comparison
            spacing = tuple(round(s, 4) for s in img.GetSpacing())
            spacings.add(spacing)
            
    print(f"Unique Spacings Found: {spacings}")
    
    # If there are multiple spacings, it's statistically invalid to extract texture features without resampling
    if len(spacings) > 1:
        print("Multiple voxel spacings detected! PyRadiomics will be configured to resample to 1x1x1 mm.")
        extractor.settings['resampledPixelSpacing'] = [1, 1, 1]
    else:
        print("Voxel spacing is consistent. No resampling required by PyRadiomics.")

    print("\nStep 2: Starting extraction for Anterior and Posterior regions...")
    # Iterate over files
    for patient_file in os.listdir(labels_dir):
        if not patient_file.endswith(".nii.gz"): 
            continue
        
        # In MSD, training images often have _0000 suffix for the modality channel
        img_file = patient_file.replace(".nii.gz", "_0000.nii.gz")
        
        img_path = os.path.join(images_dir, img_file)
        label_path = os.path.join(labels_dir, patient_file)
        
        if not os.path.exists(img_path):
            print(f"Warning: Image for {patient_file} not found at {img_path}. Skipping.")
            continue
        
        # Read the image and label
        img = sitk.ReadImage(img_path)
        label = sitk.ReadImage(label_path)
        
        # Z-score Normalization (recommended for MRI intensities)
        img = sitk.Normalize(img)
        
        # 3. Split the labels (Background:0, Anterior:1, Posterior:2)
        # Create mask for Anterior (label 1)
        mask_anterior = sitk.Equal(label, 1)
        
        # Create mask for Posterior (label 2)
        mask_posterior = sitk.Equal(label, 2)
        
        patient_id = patient_file.replace('.nii.gz', '')
        print(f"Processing: {patient_id}")
        
        # 4. Extract separately
        try:
            feat_ant = extractor.execute(img, mask_anterior)
            # Filter out the generic PyRadiomics output logs and keep clean feature names
            ant_row = {k: v.item() if isinstance(v, (np.number, np.ndarray)) else str(v) 
                       for k, v in feat_ant.items() if not k.startswith('general_info')}
            ant_row['Label_Region'] = 'Anterior'
            ant_row['Patient'] = patient_id
            results.append(ant_row)
        except Exception as e:
            print(f"  Failed extracting Anterior for {patient_id}: {e}")
            
        try:
            feat_post = extractor.execute(img, mask_posterior)
            post_row = {k: v.item() if isinstance(v, (np.number, np.ndarray)) else str(v) 
                        for k, v in feat_post.items() if not k.startswith('general_info')}
            post_row['Label_Region'] = 'Posterior'
            post_row['Patient'] = patient_id
            results.append(post_row)
        except Exception as e:
            print(f"  Failed extracting Posterior for {patient_id}: {e}")

    # 5. Save to CSV
    if results:
        df = pd.DataFrame(results)
        
        # Reorder columns to put Patient and Label_Region first
        cols = ['Patient', 'Label_Region'] + [c for c in df.columns if c not in ['Patient', 'Label_Region']]
        df = df[cols]
        
        output_csv = os.path.join(output_dir, "hippocampus_radiomics.csv")
        df.to_csv(output_csv, index=False)
        print(f"\nExtraction complete. Saved {len(results)} rows to {output_csv}")
    else:
        print("\nNo features were extracted.")

if __name__ == "__main__":
    extract_features()
