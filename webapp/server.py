import os
import io
import base64
import json
import time
import numpy as np
import cv2
from PIL import Image
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tensorflow as tf
from keras.applications.densenet import DenseNet121
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
import threading

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)
tf_lock = threading.Lock()

# Workspace directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
NIH_DIR = os.path.join(PARENT_DIR, 'nih_new')
ASSET_DIR = os.path.join(PARENT_DIR, 'asset')
INNER_ASSET_DIR = os.path.join(PARENT_DIR, 'Chest-X-Ray-Medical-Diagnosis-with-Deep-Learning-main', 'asset')

LABELS = [
    'Cardiomegaly', 'Emphysema', 'Effusion', 'Hernia', 'Infiltration',
    'Mass', 'Nodule', 'Atelectasis', 'Pneumothorax', 'Pleural_Thickening',
    'Pneumonia', 'Fibrosis', 'Edema', 'Consolidation'
]

# Clinical explanations for Doctor and Patient modes
CLINICAL_KNOWLEDGE = {
    'Cardiomegaly': {
        'system': 'Cardiovascular',
        'severity_threshold': 0.35,
        'doctor_insight': 'Enlargement of cardiac silhouette exceeding standard cardiothoracic ratio (>0.50 on PA view). Consider hypertensive heart disease, dilated cardiomyopathy, or pericardial effusion.',
        'patient_explanation': 'Your heart looks somewhat enlarged on the X-ray. This happens when the heart works harder to pump blood, such as with elevated blood pressure or valve conditions.',
        'next_steps': 'Transthoracic Echocardiogram (TTE), 12-lead ECG, serum BNP/NT-proBNP test, and cardiology review.'
    },
    'Edema': {
        'system': 'Pulmonary Vascular',
        'severity_threshold': 0.30,
        'doctor_insight': 'Alveolar and interstitial fluid accumulation with haziness, Kerley B lines, and vascular cephalization. Often reflects elevated pulmonary capillary wedge pressure.',
        'patient_explanation': 'Fluid is collecting inside the lung tissues, which can make breathing feel heavy or short, often tied to heart or kidney fluid regulation.',
        'next_steps': 'Assessment of volume status, diuretic therapy consideration, continuous pulse oximetry, renal function panel.'
    },
    'Consolidation': {
        'system': 'Infectious / Inflammatory',
        'severity_threshold': 0.35,
        'doctor_insight': 'Homogeneous opacification of alveolar airspace with air bronchograms and preserved lung volume, classic for acute bacterial pneumonia or pulmonary hemorrhage.',
        'patient_explanation': 'A section of the lung is filled with inflammatory fluid instead of air, commonly caused by a localized lung infection (pneumonia).',
        'next_steps': 'Sputum culture, complete blood count (CBC with differential), empirical antimicrobial therapy.'
    },
    'Effusion': {
        'system': 'Pleural Space',
        'severity_threshold': 0.30,
        'doctor_insight': 'Pathologic fluid collection in the pleural space blunting the lateral or posterior costophrenic angle. May compress adjacent lung parenchyma.',
        'patient_explanation': 'Extra fluid has gathered between the outer surface of your lung and your chest wall, reducing room for the lung to fully expand.',
        'next_steps': 'Bedside thoracic ultrasound, lateral decubitus X-ray, consider diagnostic thoracentesis if etiology unknown.'
    },
    'Atelectasis': {
        'system': 'Airway / Parenchymal',
        'severity_threshold': 0.35,
        'doctor_insight': 'Volume loss of pulmonary segments with associated shift of fissures, ribs, or mediastinum toward the affected side.',
        'patient_explanation': 'A small part of your lung is temporarily collapsed or under-inflated, which frequently happens after shallow breathing or mucus congestion.',
        'next_steps': 'Incentive spirometry, deep breathing exercises, early mobilization, chest physiotherapy.'
    },
    'Pneumothorax': {
        'system': 'Pleural Emergency',
        'severity_threshold': 0.25,
        'doctor_insight': 'Air in pleural space with identifiable visceral pleural edge and absent distal pulmonary vascular markings. Immediately exclude tension pneumothorax.',
        'patient_explanation': 'Air has leaked into the space surrounding the lung, putting pressure on it. Needs prompt medical attention.',
        'next_steps': 'Immediate clinical evaluation of hemodynamics; upright expiration film or chest tube drainage if symptomatic/large.'
    },
    'Mass': {
        'system': 'Oncology / Lesion',
        'severity_threshold': 0.40,
        'doctor_insight': 'Circumscribed pulmonary lesion >30mm in diameter. Requires rigorous workup to differentiate malignancy from granuloma or abscess.',
        'patient_explanation': 'A distinct shadow or density larger than 3 cm is visible in the lung area, which requires detailed imaging to understand.',
        'next_steps': 'Contrast-enhanced Thoracic CT scan (HRCT), review prior historical radiographs, pulmonary consult.'
    },
    'Nodule': {
        'system': 'Parenchymal Lesion',
        'severity_threshold': 0.35,
        'doctor_insight': 'Focal pulmonary opacity <=30mm surrounded by aerated lung. Apply Fleischner Society guidelines based on size, margin, and patient risk factors.',
        'patient_explanation': 'A small, rounded spot (under 3 cm) noted in the lung. Often a benign scar from past infection, but deserves check-up.',
        'next_steps': 'High-resolution chest CT follow-up per Fleischner Society protocol in 3 to 12 months.'
    },
    'Pneumonia': {
        'system': 'Infectious',
        'severity_threshold': 0.30,
        'doctor_insight': 'Patchy or segmental alveolar infiltrates, often accompanied by clinical cough, fever, and leukocytosis.',
        'patient_explanation': 'Active infection in the lung causing inflammation and fluid accumulation in the small air sacs.',
        'next_steps': 'Correlate with temperature and oxygenation, sputum analysis, targeted antibiotic course.'
    },
    'Infiltration': {
        'system': 'Parenchymal',
        'severity_threshold': 0.35,
        'doctor_insight': 'Non-specific ill-defined density denoting cellular or liquid accumulation within the lung parenchyma.',
        'patient_explanation': 'Mild haze or cloudiness in the lung tissue indicating irritation, fluid, or developing infection.',
        'next_steps': 'Clinical correlation with symptoms, consider repeat chest X-ray in 4-6 weeks to check resolution.'
    },
    'Emphysema': {
        'system': 'Obstructive',
        'severity_threshold': 0.30,
        'doctor_insight': 'Overexpansion of lungs, flattened diaphragmatic domes, attenuated peripheral vascularity, increased retrosternal clear space.',
        'patient_explanation': 'Air sacs in the lungs are permanently enlarged, reducing elasticity, common with chronic smoking or COPD.',
        'next_steps': 'Spirometry (PFT), smoking cessation counseling, inhaled bronchodilator evaluation.'
    },
    'Fibrosis': {
        'system': 'Interstitial',
        'severity_threshold': 0.30,
        'doctor_insight': 'Reticular or reticulonodular interstitial opacities, traction bronchiectasis, architectural distortion, and subpleural honeycombing.',
        'patient_explanation': 'Scarring or thickening of the deep lung tissue that can make the lungs stiffer to inflate.',
        'next_steps': 'High-Resolution Computed Tomography (HRCT), DLCO diffusion testing, pulmonologist consultation.'
    },
    'Pleural_Thickening': {
        'system': 'Pleural',
        'severity_threshold': 0.30,
        'doctor_insight': 'Fibrotic thickening of the pleural membrane, commonly apical or along the costal margins, with or without calcification.',
        'patient_explanation': 'Thickening along the lining of the lungs, often a healed mark from past pleurisy or inflammation.',
        'next_steps': 'Evaluate for asbestos exposure history, assess stability against past chest X-rays.'
    },
    'Hernia': {
        'system': 'Diaphragmatic',
        'severity_threshold': 0.30,
        'doctor_insight': 'Intrathoracic protrusion of abdominal contents through a diaphragmatic aperture (hiatal, Bochdalek, or traumatic hernia).',
        'patient_explanation': 'Part of an abdominal structure has pushed slightly upward through the diaphragm into the lower chest area.',
        'next_steps': 'Barium swallow study or thoracoabdominal CT scan; surgical consult if symptomatic.'
    }
}

# Global AI Model Holders
model = None
grad_model = None

def init_model():
    global model, grad_model
    print("Loading DenseNet-121 Base Model...")
    weights_path = os.path.join(PARENT_DIR, 'densenet.hdf5')
    if not os.path.exists(weights_path):
        weights_path = os.path.join(PARENT_DIR, 'Chest-X-Ray-Medical-Diagnosis-with-Deep-Learning-main', 'densenet.hdf5')

    base_model = DenseNet121(weights=weights_path, include_top=False)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    predictions = Dense(len(LABELS), activation='sigmoid')(x)
    model = Model(inputs=base_model.input, outputs=predictions)

    pretrained_path = os.path.join(NIH_DIR, 'pretrained_model.h5')
    if not os.path.exists(pretrained_path):
        pretrained_path = os.path.join(PARENT_DIR, 'Chest-X-Ray-Medical-Diagnosis-with-Deep-Learning-main', 'nih_new', 'pretrained_model.h5')

    if os.path.exists(pretrained_path):
        print(f"Loading pretrained weights from {pretrained_path}...")
        model.load_weights(pretrained_path)
        print("Model weights successfully loaded!")
    else:
        print("Warning: pretrained weights not found, using base weights.")

    # Model for Grad-CAM
    grad_layer_name = 'conv5_block16_concat'
    grad_model = tf.keras.models.Model(
        inputs=[model.inputs],
        outputs=[model.get_layer(grad_layer_name).output, model.output]
    )
    print("Grad-CAM extraction pipeline initialized successfully!")

# Initialize model once
init_model()

def preprocess_image_array(img_pil):
    """Resize to (320, 320) and apply zero-mean unit-variance normalization"""
    img_resized = img_pil.convert('RGB').resize((320, 320))
    arr = np.array(img_resized, dtype=np.float32)
    mean = np.mean(arr)
    std = np.std(arr)
    if std == 0:
        std = 1.0
    arr_norm = (arr - mean) / std
    return np.expand_dims(arr_norm, axis=0), img_resized

def generate_gradcam_heatmap(norm_tensor, target_class_idx):
    """Compute Grad-CAM activation heatmap using GradientTape"""
    with tf.GradientTape() as tape:
        conv_outputs, model_preds = grad_model(norm_tensor)
        loss = model_preds[:, target_class_idx]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.math.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    return heatmap.numpy()

def encode_pil_to_base64(pil_img):
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode('utf-8')

def build_overlay(orig_pil, cam_map, colormap=cv2.COLORMAP_JET, alpha=0.45, threshold=0.15):
    """Generate colorized Grad-CAM heatmap and blended overlay"""
    orig_np = np.array(orig_pil)
    cam_resized = cv2.resize(cam_map, (orig_np.shape[1], orig_np.shape[0]))
    
    # Thresholding for clinical precision
    cam_thresh = np.copy(cam_resized)
    cam_thresh[cam_thresh < threshold] = 0.0
    if cam_thresh.max() > 0:
        cam_thresh = (cam_thresh / cam_thresh.max())

    cam_uint8 = np.uint8(255 * cam_thresh)
    colored_cam = cv2.applyColorMap(cam_uint8, colormap)
    colored_cam = cv2.cvtColor(colored_cam, cv2.COLOR_BGR2RGB)

    # Blend
    mask = (cam_thresh > 0.05).astype(np.float32)[..., np.newaxis]
    blended = (orig_np * (1.0 - alpha * mask) + colored_cam * (alpha * mask)).astype(np.uint8)

    # Contour / ROI Box detection
    contours, _ = cv2.findContours(cam_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = np.copy(blended)
    roi_detected = False
    for c in contours:
        if cv2.contourArea(c) > 300:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(contour_img, (x, y), (x + w, y + h), (0, 255, 230), 2)
            cv2.putText(contour_img, "AI Target ROI", (x, max(20, y - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 230), 1, cv2.LINE_AA)
            roi_detected = True

    return Image.fromarray(colored_cam), Image.fromarray(blended), Image.fromarray(contour_img), cam_resized

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/samples', methods=['GET'])
def get_samples():
    """Return pre-loaded clinical sample scans"""
    samples = [
        {
            'id': 'case_00025288_001',
            'filename': '00025288_001.png',
            'title': 'Case 1: Pulmonary Mass & Consolidation',
            'patient': 'Male, 62yo - Persistent cough & localized chest discomfort',
            'pathology': 'Mass',
            'description': 'Prominent focal parenchymal density identified in upper lobe territory.'
        },
        {
            'id': 'case_00016650_000',
            'filename': '00016650_000.png',
            'title': 'Case 2: Cardiomegaly (Enlarged Cardiac Silhouette)',
            'patient': 'Female, 68yo - Exertional dyspnea & hypertension history',
            'pathology': 'Cardiomegaly',
            'description': 'Distinct transverse enlargement of heart border >50% thoracic diameter.'
        },
        {
            'id': 'case_00005410_000',
            'filename': '00005410_000.png',
            'title': 'Case 3: Pleural Effusion & Pulmonary Edema',
            'patient': 'Male, 71yo - Orthopnea & bilateral basilar crackles',
            'pathology': 'Effusion',
            'description': 'Blunting of costophrenic angles accompanied by vascular congestion.'
        },
        {
            'id': 'case_00004090_002',
            'filename': '00004090_002.png',
            'title': 'Case 4: Infiltration & Bronchopneumonia',
            'patient': 'Female, 45yo - High fever, productive cough, and pleuritic pain',
            'pathology': 'Infiltration',
            'description': 'Patchy reticular and alveolar opacities across lower lung zones.'
        },
        {
            'id': 'case_00000003_001',
            'filename': '00000003_001.png',
            'title': 'Case 5: Baseline Check (Clear / Low Pathology)',
            'patient': 'Male, 34yo - Routine pre-employment occupational physical',
            'pathology': 'Normal / Minor',
            'description': 'Clear costophrenic recesses, normal cardiomediastinal contour, no acute infiltrates.'
        }
    ]
    return jsonify({'samples': samples})

@app.route('/api/predict', methods=['POST'])
def predict():
    start_time = time.time()
    img_pil = None
    sample_id = request.form.get('sample_id')
    selected_pathology = request.form.get('target_pathology', None)

    # 1. Load image from file upload, sample ID, or base64
    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        img_pil = Image.open(file.stream)
    elif sample_id:
        # Search for sample image file
        for folder in [os.path.join(NIH_DIR, 'images-small'), ASSET_DIR, INNER_ASSET_DIR]:
            candidate = os.path.join(folder, sample_id.replace('case_', ''))
            if os.path.exists(candidate):
                img_pil = Image.open(candidate)
                break
    elif request.json and 'image_base64' in request.json:
        data_str = request.json['image_base64']
        if ',' in data_str:
            data_str = data_str.split(',')[1]
        img_data = base64.b64decode(data_str)
        img_pil = Image.open(io.BytesIO(img_data))
        selected_pathology = request.json.get('target_pathology', None)

    if img_pil is None:
        return jsonify({'error': 'No valid X-Ray image provided.'}), 400

    # Convert to standard format
    img_pil = img_pil.convert('RGB')
    orig_w, orig_h = img_pil.size

    # Preprocess
    norm_tensor, resized_pil = preprocess_image_array(img_pil)

    # Model inference
    with tf_lock:
        preds = model.predict(norm_tensor)[0]
    
    # Build pathology results
    results = []
    for i, label in enumerate(LABELS):
        prob = float(preds[i])
        info = CLINICAL_KNOWLEDGE.get(label, {})
        thresh = info.get('severity_threshold', 0.35)
        
        if prob >= 0.50:
            risk = 'High'
            badge_color = 'danger'
        elif prob >= thresh:
            risk = 'Moderate'
            badge_color = 'warning'
        else:
            risk = 'Low'
            badge_color = 'success'

        results.append({
            'index': i,
            'pathology': label,
            'probability': round(prob, 4),
            'percentage': round(prob * 100, 1),
            'risk_level': risk,
            'badge_color': badge_color,
            'system': info.get('system', 'Thoracic'),
            'doctor_insight': info.get('doctor_insight', ''),
            'patient_explanation': info.get('patient_explanation', ''),
            'next_steps': info.get('next_steps', '')
        })

    # Sort by probability descending
    results.sort(key=lambda x: x['probability'], reverse=True)
    top_result = results[0]

    # Target class index for Grad-CAM
    if selected_pathology and selected_pathology in LABELS:
        target_idx = LABELS.index(selected_pathology)
        active_label = selected_pathology
    else:
        target_idx = top_result['index']
        active_label = top_result['pathology']

    # Compute Grad-CAM
    with tf_lock:
        cam_matrix = generate_gradcam_heatmap(norm_tensor, target_idx)
    
    # Generate visual representations
    cam_colored, overlay_img, contour_img, cam_resized = build_overlay(resized_pil, cam_matrix)

    # Encode images to base64
    orig_b64 = encode_pil_to_base64(resized_pil)
    cam_b64 = encode_pil_to_base64(cam_colored)
    overlay_b64 = encode_pil_to_base64(overlay_img)
    contour_b64 = encode_pil_to_base64(contour_img)

    processing_time_ms = int((time.time() - start_time) * 1000)

    # Summary clinical impression
    critical_findings = [r for r in results if r['risk_level'] in ['High', 'Moderate']]
    if not critical_findings:
        clinical_impression = "No acute high-grade thoracic pathology detected. Normal cardiopulmonary parameters observed within standard thresholds."
    else:
        names = [f"{r['pathology']} ({r['percentage']}%)" for r in critical_findings[:3]]
        clinical_impression = f"Elevated clinical risk detected for: {', '.join(names)}. Anatomic region highlighted via Grad-CAM saliency mapping."

    response_data = {
        'success': True,
        'processing_time_ms': processing_time_ms,
        'image_dimensions': {'width': orig_w, 'height': orig_h},
        'top_pathology': top_result['pathology'],
        'top_probability': top_result['probability'],
        'active_gradcam_label': active_label,
        'clinical_impression': clinical_impression,
        'pathologies': results,
        'images': {
            'original': orig_b64,
            'heatmap': cam_b64,
            'overlay': overlay_b64,
            'contour': contour_b64
        }
    }
    return jsonify(response_data)

@app.route('/api/gradcam', methods=['POST'])
def update_gradcam():
    """Switch Grad-CAM saliency map to another pathology without re-uploading"""
    data = request.json
    if not data or 'image_base64' not in data or 'target_pathology' not in data:
        return jsonify({'error': 'Missing image or target_pathology'}), 400

    target_label = data['target_pathology']
    if target_label not in LABELS:
        return jsonify({'error': f'Invalid pathology {target_label}'}), 400

    target_idx = LABELS.index(target_label)
    data_str = data['image_base64']
    if ',' in data_str:
        data_str = data_str.split(',')[1]
    img_data = base64.b64decode(data_str)
    img_pil = Image.open(io.BytesIO(img_data)).convert('RGB')
    
    norm_tensor, resized_pil = preprocess_image_array(img_pil)
    with tf_lock:
        cam_matrix = generate_gradcam_heatmap(norm_tensor, target_idx)
    
    # Custom colormap & threshold from user
    cmap_str = data.get('colormap', 'jet')
    cmap_map = {
        'jet': cv2.COLORMAP_JET,
        'magma': cv2.COLORMAP_MAGMA,
        'inferno': cv2.COLORMAP_INFERNO,
        'turbo': cv2.COLORMAP_TURBO,
        'viridis': cv2.COLORMAP_VIRIDIS
    }
    colormap = cmap_map.get(cmap_str, cv2.COLORMAP_JET)
    alpha = float(data.get('opacity', 0.45))
    threshold = float(data.get('threshold', 0.15))

    cam_colored, overlay_img, contour_img, _ = build_overlay(resized_pil, cam_matrix, colormap, alpha, threshold)

    return jsonify({
        'success': True,
        'active_gradcam_label': target_label,
        'images': {
            'heatmap': encode_pil_to_base64(cam_colored),
            'overlay': encode_pil_to_base64(overlay_img),
            'contour': encode_pil_to_base64(contour_img)
        }
    })

if __name__ == '__main__':
    port = 5000
    print(f"Starting Medical X-Ray AI Platform on http://127.0.0.1:{port}...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=False)
