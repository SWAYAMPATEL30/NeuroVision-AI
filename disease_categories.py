"""
Comprehensive Disease Categories Database
Covers major disease categories for medical classification
"""

# Comprehensive disease categories based on ICD-10 and medical classifications
COMPREHENSIVE_DISEASES = {
    # Respiratory Diseases
    "respiratory": [
        "pneumonia", "bronchitis", "asthma", "copd", "tuberculosis", "lung cancer",
        "pneumothorax", "pleural effusion", "atelectasis", "pulmonary edema",
        "pulmonary embolism", "respiratory failure", "acute respiratory distress syndrome",
        "pneumonitis", "bronchiectasis", "emphysema", "lung abscess", "pleurisy"
    ],
    
    # Cardiovascular Diseases
    "cardiovascular": [
        "heart attack", "myocardial infarction", "heart failure", "cardiomyopathy",
        "arrhythmia", "atrial fibrillation", "coronary artery disease", "angina",
        "cardiomegaly", "pericarditis", "endocarditis", "hypertension", "hypotension",
        "aortic stenosis", "mitral valve disease", "congestive heart failure",
        "cardiac arrest", "stroke", "cerebrovascular accident"
    ],
    
    # Neurological Diseases
    "neurological": [
        "alzheimer's disease", "parkinson's disease", "epilepsy", "seizure",
        "meningitis", "encephalitis", "brain tumor", "brain cancer", "stroke",
        "multiple sclerosis", "als", "amyotrophic lateral sclerosis", "dementia",
        "migraine", "headache", "concussion", "traumatic brain injury", "neuropathy"
    ],
    
    # Musculoskeletal Diseases
    "musculoskeletal": [
        "fracture", "broken bone", "osteoporosis", "arthritis", "rheumatoid arthritis",
        "osteoarthritis", "gout", "bursitis", "tendonitis", "sprain", "strain",
        "herniated disc", "scoliosis", "osteomyelitis", "bone cancer", "sarcoma"
    ],
    
    # Gastrointestinal Diseases
    "gastrointestinal": [
        "gastritis", "ulcer", "peptic ulcer", "gastroenteritis", "colitis",
        "crohn's disease", "irritable bowel syndrome", "ibs", "hepatitis",
        "cirrhosis", "liver cancer", "pancreatitis", "appendicitis", "diverticulitis",
        "gallstones", "cholecystitis", "gastroesophageal reflux", "gerd"
    ],
    
    # Infectious Diseases
    "infectious": [
        "infection", "bacterial infection", "viral infection", "fungal infection",
        "sepsis", "septicemia", "pneumonia", "tuberculosis", "hiv", "aids",
        "hepatitis", "influenza", "flu", "covid-19", "coronavirus", "meningitis",
        "encephalitis", "urinary tract infection", "uti", "cellulitis"
    ],
    
    # Cancer/Tumors
    "cancer": [
        "cancer", "tumor", "malignancy", "carcinoma", "sarcoma", "lymphoma",
        "leukemia", "lung cancer", "breast cancer", "prostate cancer", "colon cancer",
        "liver cancer", "pancreatic cancer", "brain cancer", "bone cancer",
        "skin cancer", "melanoma", "metastasis", "benign tumor"
    ],
    
    # Endocrine/Metabolic Diseases
    "endocrine": [
        "diabetes", "diabetes mellitus", "type 1 diabetes", "type 2 diabetes",
        "hypothyroidism", "hyperthyroidism", "thyroid cancer", "goiter",
        "addison's disease", "cushing's syndrome", "obesity", "metabolic syndrome"
    ],
    
    # Renal/Urinary Diseases
    "renal": [
        "kidney disease", "renal failure", "kidney failure", "nephritis",
        "kidney stones", "nephrolithiasis", "urinary tract infection", "uti",
        "bladder cancer", "kidney cancer", "renal cell carcinoma", "cystitis"
    ],
    
    # Skin Diseases
    "dermatological": [
        "dermatitis", "eczema", "psoriasis", "skin cancer", "melanoma",
        "basal cell carcinoma", "squamous cell carcinoma", "acne", "rash",
        "cellulitis", "impetigo", "shingles", "herpes zoster"
    ],
    
    # Blood/Hematological Diseases
    "hematological": [
        "anemia", "iron deficiency anemia", "leukemia", "lymphoma",
        "thrombocytopenia", "hemophilia", "sickle cell disease", "blood clot",
        "deep vein thrombosis", "dvt", "pulmonary embolism"
    ],
    
    # Eye Diseases
    "ophthalmic": [
        "cataract", "glaucoma", "macular degeneration", "retinal detachment",
        "conjunctivitis", "pink eye", "diabetic retinopathy", "eye infection"
    ],
    
    # Ear/Nose/Throat Diseases
    "ent": [
        "otitis media", "ear infection", "sinusitis", "rhinitis", "tonsillitis",
        "pharyngitis", "laryngitis", "hearing loss", "vertigo", "meniere's disease"
    ],
    
    # Autoimmune Diseases
    "autoimmune": [
        "rheumatoid arthritis", "lupus", "systemic lupus erythematosus",
        "multiple sclerosis", "crohn's disease", "ulcerative colitis",
        "psoriasis", "type 1 diabetes", "hashimoto's thyroiditis"
    ],
    
    # Mental Health
    "mental_health": [
        "depression", "anxiety", "bipolar disorder", "schizophrenia",
        "ptsd", "post-traumatic stress disorder", "adhd", "autism",
        "dementia", "alzheimer's disease"
    ],
    
    # Other Common Conditions
    "other": [
        "fever", "pain", "inflammation", "edema", "swelling", "normal",
        "healthy", "no finding", "no abnormality", "support devices"
    ]
}

# Flattened comprehensive disease list for zero-shot classification
ALL_DISEASES = []
for category, diseases in COMPREHENSIVE_DISEASES.items():
    ALL_DISEASES.extend(diseases)

# Remove duplicates and sort
ALL_DISEASES = sorted(list(set(ALL_DISEASES)))

# Disease categories for organized classification
DISEASE_CATEGORIES = list(COMPREHENSIVE_DISEASES.keys())

def get_diseases_by_category(category):
    """Get diseases for a specific category"""
    return COMPREHENSIVE_DISEASES.get(category, [])

def get_all_diseases():
    """Get comprehensive list of all diseases"""
    return ALL_DISEASES

def search_diseases(query):
    """Search for diseases matching a query"""
    query_lower = query.lower()
    matches = [d for d in ALL_DISEASES if query_lower in d.lower() or d.lower() in query_lower]
    return matches

def get_category_for_disease(disease):
    """Get category for a specific disease"""
    disease_lower = disease.lower()
    for category, diseases in COMPREHENSIVE_DISEASES.items():
        if disease_lower in [d.lower() for d in diseases]:
            return category
    return "other"




