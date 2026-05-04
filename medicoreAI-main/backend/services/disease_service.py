import os
import glob
import json
import logging
from typing import List, Dict, Any

import pandas as pd
import joblib

logger = logging.getLogger(__name__)

# Paths relative to project root (parent of backend/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'MEDI_CORE_ASSIST'))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATASET_PATH = os.path.join(BASE_DIR, 'DATASET', 'dataset.csv')
DESCRIPTIONS_PATH = os.path.join(BASE_DIR, 'DATASET', 'symptom_Description.csv')
PRECAUTIONS_PATH = os.path.join(BASE_DIR, 'DATASET', 'symptom_precaution.csv')


def _latest_metadata_file() -> str:
    pattern = os.path.join(MODELS_DIR, 'model_metadata_*.json')
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError("No metadata JSON files found in 'models' directory.")
    files.sort(reverse=True)
    return files[0]


def load_artifacts() -> Dict[str, Any]:
    meta_file = _latest_metadata_file()
    with open(meta_file, 'r') as f:
        meta = json.load(f)
    model_path = os.path.join(MODELS_DIR, meta['model_file'])
    le_path = os.path.join(MODELS_DIR, meta['label_encoder_file'])

    model = joblib.load(model_path)

    try:
        label_encoder = joblib.load(le_path)
    except Exception:
        class DummyLE:
            classes_ = meta['classes']
            def inverse_transform(self, arr):
                return [self.classes_[i] for i in arr]
        label_encoder = DummyLE()

    if hasattr(model, 'feature_names_in_'):
        feature_names = list(model.feature_names_in_)
    else:
        if not os.path.exists(DATASET_PATH):
            raise FileNotFoundError("Cannot infer feature names; dataset.csv not found.")
        df = pd.read_csv(DATASET_PATH)
        symptom_cols = [c for c in df.columns if c.lower().startswith('symptom')]
        symptoms = set()
        for col in symptom_cols:
            vals = df[col].dropna().astype(str).str.strip()
            symptoms.update(v for v in vals if v and v.lower() != 'nan')
        feature_names = sorted(symptoms)

    return {
        'model': model,
        'label_encoder': label_encoder,
        'feature_names': feature_names,
        'meta': meta
    }


def load_disease_info() -> Dict[str, Dict[str, Any]]:
    disease_info = {
        'descriptions': {},
        'precautions': {}
    }

    try:
        if os.path.exists(DESCRIPTIONS_PATH):
            desc_df = pd.read_csv(DESCRIPTIONS_PATH)
            for _, row in desc_df.iterrows():
                disease_info['descriptions'][row['Disease']] = row['Description']
    except Exception as e:
        logger.warning("Could not load descriptions: %s", e)

    try:
        if os.path.exists(PRECAUTIONS_PATH):
            prec_df = pd.read_csv(PRECAUTIONS_PATH)
            for _, row in prec_df.iterrows():
                disease = row['Disease']
                precautions = []
                for i in range(1, 5):
                    prec_col = f'Precaution_{i}'
                    if prec_col in row and pd.notna(row[prec_col]) and row[prec_col].strip():
                        precautions.append(row[prec_col].strip())
                disease_info['precautions'][disease] = precautions
    except Exception as e:
        logger.warning("Could not load precautions: %s", e)

    return disease_info


def build_feature_vector(selected: List[str], feature_names: List[str]) -> pd.DataFrame:
    data = {name: 0 for name in feature_names}
    for s in selected:
        if s in data:
            data[s] = 1
    return pd.DataFrame([data])


def predict_disease(
    symptoms: List[str],
    model,
    label_encoder,
    feature_names: List[str],
    disease_info: Dict[str, Dict[str, Any]],
    top_n: int = 3,
) -> Dict[str, Any]:
    X_row = build_feature_vector(symptoms, feature_names)
    pred_idx = model.predict(X_row)[0]
    pred_label = label_encoder.inverse_transform([pred_idx])[0]

    result: Dict[str, Any] = {
        'predicted_disease': pred_label,
        'input_symptoms': symptoms,
    }

    if pred_label in disease_info['descriptions']:
        result['description'] = disease_info['descriptions'][pred_label]
    if pred_label in disease_info['precautions']:
        result['precautions'] = disease_info['precautions'][pred_label]

    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X_row)[0]
        pairs = list(zip(label_encoder.classes_, proba))
        pairs.sort(key=lambda x: x[1], reverse=True)
        result['top_predictions'] = []
        for d, p in pairs[:top_n]:
            disease_pred: Dict[str, Any] = {
                'disease': d,
                'probability': round(float(p), 4)
            }
            if d in disease_info['descriptions']:
                disease_pred['description'] = disease_info['descriptions'][d]
            if d in disease_info['precautions']:
                disease_pred['precautions'] = disease_info['precautions'][d]
            result['top_predictions'].append(disease_pred)

    return result
