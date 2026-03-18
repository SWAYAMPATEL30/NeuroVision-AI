"""
Fine-tune the custom chest X-ray model (CustomNet121) on the NIH ChestX-ray8 dataset.

This script is designed to:
- Load your existing chest model weights from `major_project-main/models/chest_xray.h5`
- Re-create the training/validation generators similar to `major_project-main/chestxray.ipynb`
- Continue training (fine-tune) the model with a lower learning rate
- Save the updated weights to `major_project-main/models/chest_xray_finetuned.h5`

NOTE:
- The NIH ChestX-ray8 Kaggle dataset you linked is the same dataset used in `chestxray.ipynb`.
- Make sure your `train_df.csv` and image files are prepared exactly as in the notebook:
  - `major_project-main/train_df.csv` should have a `FilePath` column pointing to each image.
  - The label columns should be the 14 pathology labels.
"""

import os
import csv
from typing import Tuple, List

import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint,
    LearningRateScheduler,
    EarlyStopping,
    CSVLogger,
)
from tensorflow.keras.models import load_model

try:
    import kagglehub
except ImportError:
    kagglehub = None


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

DATA_CSV = "major_project-main/train_df.csv"  # generated from NIH ChestX-ray8
IMAGE_DIR = None  # FilePath column already includes the full/relative path

ORIGINAL_MODEL_PATH = "major_project-main/models/chest_xray.h5"
FINETUNED_MODEL_PATH = "major_project-main/models/chest_xray_finetuned.h5"

BATCH_SIZE = 8
IMAGE_SIZE = (320, 320)  # matches the notebook
EPOCHS = 10  # fine-tuning epochs (you can increase if you have GPU/time)
VAL_SPLIT = 0.15  # validation split from the existing train_df
RANDOM_STATE = 1993


def build_generators(df: pd.DataFrame, label_cols: List[str]):
    """
    Build train and validation generators from the existing train_df.csv.

    Assumes:
    - df has a 'FilePath' column with image paths
    - label_cols lists the label columns to use
    """
    labels = list(label_cols)

    # Train/validation split
    from sklearn.model_selection import train_test_split

    train_df, valid_df = train_test_split(
        df, test_size=VAL_SPLIT, random_state=RANDOM_STATE
    )

    # Image augmentation & normalization (similar to notebook)
    train_datagen = ImageDataGenerator(
        samplewise_center=True,
        samplewise_std_normalization=True,
        shear_range=0.1,
        zoom_range=0.15,
        rotation_range=5,
        width_shift_range=0.1,
        height_shift_range=0.05,
        horizontal_flip=True,
        vertical_flip=False,
        rescale=1.0 / 255.0,
        fill_mode="reflect",
    )

    valid_datagen = ImageDataGenerator(
        samplewise_center=True,
        samplewise_std_normalization=True,
        rescale=1.0 / 255.0,
    )

    train_gen = train_datagen.flow_from_dataframe(
        dataframe=train_df,
        directory=IMAGE_DIR,
        x_col="FilePath",
        y_col=labels,
        class_mode="raw",
        batch_size=BATCH_SIZE,
        shuffle=True,
        seed=RANDOM_STATE,
        target_size=IMAGE_SIZE,
    )

    valid_gen = valid_datagen.flow_from_dataframe(
        dataframe=valid_df,
        directory=IMAGE_DIR,
        x_col="FilePath",
        y_col=labels,
        class_mode="raw",
        batch_size=BATCH_SIZE,
        shuffle=False,
        seed=RANDOM_STATE,
        target_size=IMAGE_SIZE,
    )

    return train_gen, valid_gen, labels


def build_lr_schedule(
    lr_start=1e-5,
    lr_max=5e-5,
    lr_min=0,
    lr_rampup_epochs=3,
    lr_sustain_epochs=0,
    lr_exp_decay=0.8,
):
    """
    A gentle learning rate schedule for fine-tuning (smaller LR than original training).
    """

    def lrfn(epoch):
        if epoch < lr_rampup_epochs:
            lr = (lr_max - lr_start) / lr_rampup_epochs * epoch + lr_start
        elif epoch < lr_rampup_epochs + lr_sustain_epochs:
            lr = lr_max
        else:
            lr = (lr_max - lr_min) * lr_exp_decay ** (
                epoch - lr_rampup_epochs - lr_sustain_epochs
            ) + lr_min
        return lr

    return LearningRateScheduler(lrfn, verbose=1)


def _find_file_recursive(root: str, filename: str) -> str:
    """Search for a file by name under a root directory."""
    for dirpath, _, filenames in os.walk(root):
        if filename in filenames:
            return os.path.join(dirpath, filename)
    raise FileNotFoundError(f"{filename} not found under {root}")


def _build_train_df_from_kaggle(dataset_root: str, output_csv: str) -> None:
    """
    Build train_df.csv compatible with the original notebook from NIH ChestX-ray8.

    - Reads Data_Entry_2017.csv
    - Expands 'Finding Labels' into 14 binary columns
    - Adds 'FilePath' column with absolute paths to each image
    """
    print(f"[INFO] Building train_df.csv from NIH ChestX-ray8 at: {dataset_root}")

    meta_path = _find_file_recursive(dataset_root, "Data_Entry_2017.csv")
    print(f"[INFO] Found metadata CSV at: {meta_path}")

    # Known CheXpert/NIH labels (14)
    pathology_labels: List[str] = [
        "Atelectasis",
        "Cardiomegaly",
        "Effusion",
        "Infiltration",
        "Mass",
        "Nodule",
        "Pneumonia",
        "Pneumothorax",
        "Consolidation",
        "Edema",
        "Emphysema",
        "Fibrosis",
        "Pleural_Thickening",
        "Hernia",
    ]

    df_meta = pd.read_csv(meta_path)
    if "Image Index" not in df_meta.columns or "Finding Labels" not in df_meta.columns:
        raise ValueError(
            "Expected columns 'Image Index' and 'Finding Labels' in Data_Entry_2017.csv"
        )

    # Build mapping from image filename -> full path (scan once to avoid O(N^2))
    print("[INFO] Indexing all image files (this may take a while once)...")
    image_map = {}
    for dirpath, _, filenames in os.walk(dataset_root):
        for fname in filenames:
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                image_map[fname] = os.path.join(dirpath, fname)
    print(f"[INFO] Indexed {len(image_map)} image files.")

    rows: List[dict] = []
    missing_count = 0

    for _, row in df_meta.iterrows():
        img_name = row["Image Index"]
        findings = row["Finding Labels"]

        if img_name not in image_map:
            missing_count += 1
            continue

        entry = {
            "PatientId": row.get("Patient ID", None),
            "FilePath": image_map[img_name],
        }

        # Initialize all labels to 0
        for label in pathology_labels:
            entry[label] = 0

        # Parse findings (multi-label, separated by '|')
        for lbl in str(findings).split("|"):
            lbl = lbl.strip()
            if lbl == "No Finding" or not lbl:
                continue
            if lbl in pathology_labels:
                entry[lbl] = 1

        rows.append(entry)

    train_df = pd.DataFrame(rows)
    print(f"[INFO] Built train_df with {len(train_df)} rows (skipped {missing_count} missing images).")

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    train_df.to_csv(output_csv, index=False)
    print(f"[INFO] Saved train_df.csv to: {output_csv}")


def ensure_train_df_exists() -> None:
    """
    Ensure `DATA_CSV` exists. If not, automatically download NIH ChestX-ray8 via kagglehub
    and build train_df.csv from it.
    """
    if os.path.exists(DATA_CSV):
        print(f"[INFO] Using existing CSV: {DATA_CSV}")
        return

    if kagglehub is None:
        raise ImportError(
            "kagglehub is not installed, and train_df.csv is missing. "
            "Install kagglehub with `pip install kagglehub` or create train_df.csv manually."
        )

    print("[INFO] train_df.csv not found. Downloading NIH ChestX-ray8 via kagglehub...")
    dataset_root = kagglehub.dataset_download("nih-chest-xrays/data")
    print(f"[INFO] Dataset downloaded to: {dataset_root}")

    _build_train_df_from_kaggle(dataset_root, DATA_CSV)


def get_last_epoch_from_history() -> int:
    """Get the last completed epoch from training history CSV."""
    if not os.path.exists("chest_finetune_history.csv"):
        return 0
    
    try:
        df = pd.read_csv("chest_finetune_history.csv")
        if len(df) > 0:
            last_epoch = int(df['epoch'].max())
            print(f"[INFO] Found training history: last completed epoch = {last_epoch}")
            return last_epoch + 1  # Start from next epoch
    except Exception as e:
        print(f"[WARNING] Could not read training history: {e}")
    
    return 0


def load_chest_model() -> Tuple[tf.keras.Model, int, int]:
    """
    Load existing chest model if available, otherwise raise a clear error.
    Returns: (model, output_classes, initial_epoch)
    """
    # Check if fine-tuned model exists (resume from checkpoint)
    if os.path.exists(FINETUNED_MODEL_PATH):
        print(f"[INFO] Found existing fine-tuned model at: {FINETUNED_MODEL_PATH}")
        print("[INFO] Resuming fine-tuning from checkpoint...")
        model = load_model(FINETUNED_MODEL_PATH, compile=False)
        initial_epoch = get_last_epoch_from_history()
    elif not os.path.exists(ORIGINAL_MODEL_PATH):
        raise FileNotFoundError(
            f"Original chest model not found at {ORIGINAL_MODEL_PATH}. "
            "Make sure you've trained and saved chest_xray.h5 first."
        )
    else:
        # The custom chest model (CustomNet121) uses only standard Keras layers,
        # so we don't need a custom_objects dict here.
        print(f"Loading existing chest model from: {ORIGINAL_MODEL_PATH}")
        model = load_model(ORIGINAL_MODEL_PATH, compile=False)
        initial_epoch = 0

    # Re-compile with a smaller learning rate for fine-tuning
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="binary_crossentropy",
        metrics=["binary_accuracy"],
    )

    # Determine how many output classes the model has
    output_classes = int(model.output_shape[-1])
    print(f"[INFO] Chest model output classes: {output_classes}")
    print(f"[INFO] Starting from epoch: {initial_epoch}")

    model.summary()
    return model, output_classes, initial_epoch


def main():
    print("=" * 60)
    print("Fine-tuning Custom Chest X-Ray Model (CustomNet121)")
    print("=" * 60)

    # Ensure training CSV exists (auto-download & build if needed)
    ensure_train_df_exists()

    # Load dataframe
    df = pd.read_csv(DATA_CSV)
    print(f"Loaded dataframe from {DATA_CSV} with {len(df)} rows.")

    # All label columns from CSV (after PatientId, FilePath)
    all_labels = list(df.columns[2:])
    print(f"Detected {len(all_labels)} label columns in CSV.")

    # Load model and get its output class count (resume from checkpoint if available)
    model, model_output_classes, initial_epoch = load_chest_model()

    # Align labels with model outputs to avoid mismatch
    if model_output_classes != len(all_labels):
        print(
            f"[INFO] Model outputs {model_output_classes} classes, "
            f"but CSV has {len(all_labels)} label columns."
        )
        if model_output_classes < len(all_labels):
            label_cols = all_labels[:model_output_classes]
            print(
                f"[INFO] Using first {model_output_classes} labels to match model: {label_cols}"
            )
        else:
            raise ValueError(
                "Model expects more output classes than labels available in CSV. "
                "Please check your dataset and model configuration."
            )
    else:
        label_cols = all_labels

    # Build generators with aligned label columns
    train_gen, valid_gen, labels = build_generators(df, label_cols)

    # Callbacks: checkpoint, LR schedule, early stopping, and CSV logger
    os.makedirs(os.path.dirname(FINETUNED_MODEL_PATH), exist_ok=True)
    checkpoint_cb = ModelCheckpoint(
        FINETUNED_MODEL_PATH,
        monitor="val_binary_accuracy",
        verbose=1,
        save_best_only=True,
        mode="max",
    )
    lr_schedule_cb = build_lr_schedule()
    early_stopping_cb = EarlyStopping(
        monitor="val_binary_accuracy",
        patience=3,
        mode="max",
        restore_best_weights=True,
        verbose=1,
    )
    csv_logger_cb = CSVLogger("chest_finetune_history.csv", append=True)

    # Fine-tune (resume from checkpoint if available)
    if initial_epoch > 0:
        print(f"\nResuming fine-tuning from epoch {initial_epoch} (with early stopping and LR schedule)...")
    else:
        print("\nStarting fine-tuning (with early stopping and LR schedule)...")
    
    history = model.fit(
        train_gen,
        validation_data=valid_gen,
        epochs=EPOCHS,
        initial_epoch=initial_epoch,
        callbacks=[checkpoint_cb, lr_schedule_cb, early_stopping_cb, csv_logger_cb],
    )

    print("\nFine-tuning complete.")
    print(f"Best fine-tuned model saved to: {FINETUNED_MODEL_PATH}")


if __name__ == "__main__":
    main()

