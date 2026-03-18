"""
Example usage of the Medical Disease Classification System
"""

from medical_classifier import MedicalClassifier
import json

def example_image_classification():
    """Example: Classify disease from medical image"""
    print("=" * 60)
    print("Example 1: Image Classification")
    print("=" * 60)
    
    classifier = MedicalClassifier()
    
    # Replace with your image path
    image_path = "path/to/your/medical_scan.jpg"
    
    results = classifier.classify(
        image_path=image_path,
        generate_report=True
    )
    
    print("\nResults:")
    print(json.dumps(results, indent=2))


def example_text_classification():
    """Example: Classify disease from medical report text"""
    print("=" * 60)
    print("Example 2: Text Report Classification")
    print("=" * 60)
    
    classifier = MedicalClassifier()
    
    report_text = """
    Patient presents with acute chest pain and shortness of breath.
    Chest X-ray shows bilateral lower lobe opacities consistent with 
    pneumonia. No pneumothorax or pleural effusion noted.
    """
    
    results = classifier.classify(
        report_text=report_text,
        generate_report=True
    )
    
    print("\nResults:")
    print(json.dumps(results, indent=2))


def example_combined_analysis():
    """Example: Combined image and text analysis"""
    print("=" * 60)
    print("Example 3: Combined Image + Text Analysis")
    print("=" * 60)
    
    classifier = MedicalClassifier()
    
    image_path = "path/to/chest_xray.jpg"
    report_text = "Patient with history of smoking, presenting with cough and fever."
    
    results = classifier.classify(
        image_path=image_path,
        report_text=report_text,
        generate_report=True
    )
    
    print("\nResults:")
    print(json.dumps(results, indent=2))


def example_individual_models():
    """Example: Use individual models separately"""
    print("=" * 60)
    print("Example 4: Individual Model Usage")
    print("=" * 60)
    
    classifier = MedicalClassifier()
    
    from PIL import Image
    image = Image.open("path/to/medical_scan.jpg")
    
    # Use MedSigLIP with custom prompts
    custom_prompts = [
        "broken bone", "fracture", "pneumonia", 
        "tumor", "normal chest x-ray"
    ]
    medsiglip_result = classifier.classify_with_medsiglip(
        image, 
        text_prompts=custom_prompts
    )
    print("\nMedSigLIP Results:")
    print(json.dumps(medsiglip_result, indent=2))
    
    # Use CheXpert for common diseases
    chexpert_result = classifier.classify_with_chexpert(image)
    print("\nCheXpert Results:")
    print(json.dumps(chexpert_result, indent=2))


if __name__ == "__main__":
    # Uncomment the example you want to run
    
    # example_image_classification()
    # example_text_classification()
    # example_combined_analysis()
    # example_individual_models()
    
    print("\nPlease uncomment one of the example functions to run it.")
    print("Make sure to update the image paths with your actual files.")




