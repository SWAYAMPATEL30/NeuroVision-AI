"""
Analyze chest X-ray model training curves + prediction bias.

Outputs PNG plots into ./analysis_outputs/
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _require_file(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required file not found: {path}")
    return path


def plot_training_curves(history_csv: str, out_dir: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")  # headless
    import matplotlib.pyplot as plt

    df = pd.read_csv(history_csv)
    # Sometimes repeated epochs can be present; keep last row per epoch
    if "epoch" in df.columns:
        df = df.sort_values("epoch").groupby("epoch", as_index=False).tail(1)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Accuracy
    if "binary_accuracy" in df.columns:
        axes[0].plot(df["epoch"], df["binary_accuracy"], label="train")
    if "val_binary_accuracy" in df.columns:
        axes[0].plot(df["epoch"], df["val_binary_accuracy"], label="val")
    axes[0].set_title("Binary Accuracy")
    axes[0].set_xlabel("epoch")
    axes[0].set_ylabel("accuracy")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    # Loss
    if "loss" in df.columns:
        axes[1].plot(df["epoch"], df["loss"], label="train")
    if "val_loss" in df.columns:
        axes[1].plot(df["epoch"], df["val_loss"], label="val")
    axes[1].set_title("Binary Cross-Entropy Loss")
    axes[1].set_xlabel("epoch")
    axes[1].set_ylabel("loss")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    fig.tight_layout()

    out_path = out_dir / "training_curves.png"
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return out_path


def _load_image_rgb(path: str, target_size=(224, 224)):
    from PIL import Image

    img = Image.open(path).convert("RGB")
    if img.size != target_size:
        img = img.resize(target_size)
    arr = np.asarray(img).astype(np.float32) / 255.0
    return arr


def plot_prediction_bias(
    model_path: str,
    train_df_csv: str,
    out_dir: Path,
    sample_size: int = 500,
    seed: int = 42,
) -> tuple[Path, Path]:
    import matplotlib

    matplotlib.use("Agg")  # headless
    import matplotlib.pyplot as plt
    import tensorflow as tf

    df = pd.read_csv(train_df_csv)
    if "FilePath" not in df.columns:
        raise ValueError("train_df.csv must have a FilePath column")

    # Determine labels robustly: keep only columns that look like binary 0/1 labels.
    # This avoids accidentally including metadata columns like PatientId.
    def _is_binary_label(col: pd.Series) -> bool:
        if not pd.api.types.is_numeric_dtype(col):
            return False
        s = col.dropna()
        if len(s) == 0:
            return False
        # Allow small noise (e.g., float 0.0/1.0)
        vals = set(np.unique(s.values))
        return vals.issubset({0, 1, 0.0, 1.0})

    candidate_cols = [c for c in df.columns if c not in {"FilePath"}]
    label_cols = [c for c in candidate_cols if _is_binary_label(df[c])]
    if not label_cols:
        raise ValueError("No binary (0/1) label columns found in train_df.csv")

    model = tf.keras.models.load_model(model_path, compile=False)
    out_classes = int(model.output_shape[-1])
    if len(label_cols) != out_classes:
        # Match model outputs: keep the first N binary-label columns
        label_cols = label_cols[:out_classes]

    # Sample rows with existing files
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(df))

    paths = []
    for i in idx:
        p = str(df.iloc[i]["FilePath"])
        if isinstance(p, str) and os.path.exists(p):
            paths.append(p)
        if len(paths) >= sample_size:
            break

    if len(paths) < max(50, sample_size // 10):
        raise FileNotFoundError(
            f"Not enough image files found via FilePath. Found {len(paths)} existing paths."
        )

    # Predict in small batches (CPU-safe)
    batch = []
    preds = []
    bs = 16
    for p in paths:
        batch.append(_load_image_rgb(p))
        if len(batch) == bs:
            x = np.stack(batch, axis=0)
            y = model.predict(x, verbose=0)
            preds.append(y)
            batch = []
    if batch:
        x = np.stack(batch, axis=0)
        y = model.predict(x, verbose=0)
        preds.append(y)

    pred = np.concatenate(preds, axis=0)  # (N, C)
    if pred.ndim == 1:
        pred = pred.reshape(-1, 1)

    # "Top-1 label" distribution (argmax)
    top_idx = np.argmax(pred, axis=1)
    counts = np.bincount(top_idx, minlength=len(label_cols))
    freq = counts / counts.sum()

    fig1 = plt.figure(figsize=(12, 4))
    order = np.argsort(freq)[::-1]
    plt.bar([label_cols[i] for i in order], freq[order])
    plt.title(f"Top-1 Predicted Label Frequency (N={pred.shape[0]})")
    plt.ylabel("fraction")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    out1 = out_dir / "pred_top1_frequency.png"
    fig1.savefig(out1, dpi=160)
    plt.close(fig1)

    # Mean predicted probability per class
    mean_prob = pred.mean(axis=0)
    fig2 = plt.figure(figsize=(12, 4))
    order2 = np.argsort(mean_prob)[::-1]
    plt.bar([label_cols[i] for i in order2], mean_prob[order2])
    plt.title(f"Mean Predicted Probability per Class (N={pred.shape[0]})")
    plt.ylabel("mean probability")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    out2 = out_dir / "pred_mean_probability.png"
    fig2.savefig(out2, dpi=160)
    plt.close(fig2)

    return out1, out2


def main():
    base = Path(__file__).resolve().parent
    out_dir = base / "analysis_outputs"
    out_dir.mkdir(exist_ok=True)

    history_csv = _require_file(str(base / "chest_finetune_history.csv"))
    model_path = _require_file(str(base / "major_project-main" / "models" / "chest_xray_finetuned.h5"))
    train_df_csv = _require_file(str(base / "major_project-main" / "train_df.csv"))

    print("[INFO] Plotting training curves...")
    p1 = plot_training_curves(history_csv, out_dir)
    print(f"[OK] Saved: {p1}")

    print("[INFO] Checking prediction bias on a random sample...")
    try:
        p2, p3 = plot_prediction_bias(model_path, train_df_csv, out_dir, sample_size=500)
        print(f"[OK] Saved: {p2}")
        print(f"[OK] Saved: {p3}")
    except Exception as e:
        print("[WARN] Bias plots could not be generated:", e)
        print("       Training-curve plot is still available.")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

