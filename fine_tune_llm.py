"""
Fine-tuning Infrastructure for LLMs
Supports fine-tuning MedGemma and other medical LLMs on custom datasets
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import torch

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from datasets import Dataset, load_dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers or datasets not available. Install with: pip install transformers datasets")

class MedicalLLMFineTuner:
    """Fine-tune medical LLMs on custom datasets"""
    
    def __init__(self, model_name: str = "google/medgemma-27b-it", cache_dir: Optional[str] = None):
        self.model_name = model_name
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/huggingface/hub")
        self.tokenizer = None
        self.model = None
        
    def load_model_and_tokenizer(self, hf_token: Optional[str] = None):
        """Load model and tokenizer"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers and datasets required for fine-tuning")
        
        print(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            token=hf_token,
            cache_dir=self.cache_dir,
            trust_remote_code=True
        )
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            token=hf_token,
            cache_dir=self.cache_dir,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )
        
        print("Model and tokenizer loaded successfully")
    
    def prepare_dataset_from_json(self, json_path: str, text_field: str = "text") -> Dataset:
        """Prepare dataset from JSON file"""
        print(f"Loading dataset from {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to list of texts
        if isinstance(data, list):
            texts = [item[text_field] if isinstance(item, dict) else str(item) for item in data]
        elif isinstance(data, dict):
            texts = [str(v) for v in data.values()]
        else:
            raise ValueError("JSON must be a list or dict")
        
        # Create dataset
        dataset = Dataset.from_dict({"text": texts})
        return dataset
    
    def prepare_dataset_from_kaggle(self, dataset_name: str, subset: Optional[str] = None) -> Dataset:
        """Load dataset from Kaggle"""
        try:
            import kaggle
            print(f"Loading dataset from Kaggle: {dataset_name}")
            # Note: Requires Kaggle API credentials
            # Place kaggle.json in ~/.kaggle/
            dataset = load_dataset(f"kaggle/{dataset_name}", subset)
            return dataset
        except Exception as e:
            print(f"Error loading from Kaggle: {e}")
            print("Make sure kaggle.json is in ~/.kaggle/")
            raise
    
    def tokenize_dataset(self, dataset: Dataset, max_length: int = 512) -> Dataset:
        """Tokenize dataset"""
        if self.tokenizer is None:
            raise ValueError("Tokenizer not loaded. Call load_model_and_tokenizer() first.")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=max_length,
                padding="max_length"
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        return tokenized_dataset
    
    def fine_tune(
        self,
        train_dataset: Dataset,
        output_dir: str = "./fine_tuned_model",
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-5,
        save_steps: int = 500,
        eval_dataset: Optional[Dataset] = None
    ):
        """Fine-tune the model"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model and tokenizer must be loaded first")
        
        # Tokenize datasets
        print("Tokenizing datasets...")
        train_dataset = self.tokenize_dataset(train_dataset)
        if eval_dataset:
            eval_dataset = self.tokenize_dataset(eval_dataset)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=100,
            logging_steps=100,
            save_steps=save_steps,
            evaluation_strategy="steps" if eval_dataset else "no",
            eval_steps=save_steps if eval_dataset else None,
            save_total_limit=3,
            load_best_model_at_end=True if eval_dataset else False,
            fp16=torch.cuda.is_available(),
            bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
            gradient_accumulation_steps=4,
            dataloader_num_workers=2,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal LM, not masked LM
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )
        
        # Train
        print("Starting fine-tuning...")
        trainer.train()
        
        # Save model
        print(f"Saving fine-tuned model to {output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        print("Fine-tuning complete!")


def create_sample_dataset(output_path: str = "sample_medical_data.json"):
    """Create a sample medical dataset for fine-tuning"""
    sample_data = [
        {
            "text": "Patient presents with acute chest pain and shortness of breath. Chest X-ray shows bilateral lower lobe opacities consistent with pneumonia. No pneumothorax or pleural effusion noted."
        },
        {
            "text": "Brain MRI reveals a well-defined mass in the right frontal lobe, consistent with meningioma. No evidence of surrounding edema or mass effect."
        },
        {
            "text": "X-ray of the left femur shows a complete transverse fracture of the mid-shaft with minimal displacement. No evidence of comminution."
        },
        {
            "text": "CT scan of the chest demonstrates multiple pulmonary nodules, largest measuring 2.5 cm in the right upper lobe. No mediastinal lymphadenopathy."
        },
        {
            "text": "Blood test results show elevated white blood cell count (15,000/μL) and increased C-reactive protein (45 mg/L), consistent with bacterial infection."
        }
    ]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"Sample dataset created: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Fine-tune medical LLMs")
    parser.add_argument("--model", type=str, default="google/medgemma-27b-it", help="Model name")
    parser.add_argument("--dataset", type=str, help="Path to JSON dataset or Kaggle dataset name")
    parser.add_argument("--output", type=str, default="./fine_tuned_model", help="Output directory")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--hf_token", type=str, help="Hugging Face token")
    parser.add_argument("--create_sample", action="store_true", help="Create sample dataset")
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_dataset()
        return
    
    if not args.dataset:
        print("Error: --dataset required (or use --create_sample to create sample)")
        return
    
    # Initialize fine-tuner
    fine_tuner = MedicalLLMFineTuner(model_name=args.model)
    
    # Load model
    fine_tuner.load_model_and_tokenizer(hf_token=args.hf_token)
    
    # Load dataset
    if args.dataset.startswith("kaggle/"):
        dataset = fine_tuner.prepare_dataset_from_kaggle(args.dataset.replace("kaggle/", ""))
    else:
        dataset = fine_tuner.prepare_dataset_from_json(args.dataset)
    
    # Fine-tune
    fine_tuner.fine_tune(
        train_dataset=dataset,
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )


if __name__ == "__main__":
    main()


