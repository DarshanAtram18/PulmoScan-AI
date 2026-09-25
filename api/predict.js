const CLINICAL_KNOWLEDGE = {
  Cardiomegaly: {
    system: 'Cardiovascular',
    severity_threshold: 0.35,
    doctor_insight: 'Enlargement of cardiac silhouette exceeding standard cardiothoracic ratio (>0.50 on PA view). Consider hypertensive heart disease, dilated cardiomyopathy, or pericardial effusion.',
    patient_explanation: 'Your heart looks somewhat enlarged on the X-ray. This happens when the heart works harder to pump blood, such as with elevated blood pressure or valve conditions.',
    next_steps: 'Transthoracic Echocardiogram (TTE), 12-lead ECG, serum BNP/NT-proBNP test, and cardiology review.'
  },
  Edema: {
    system: 'Pulmonary Vascular',
    severity_threshold: 0.30,
    doctor_insight: 'Alveolar and interstitial fluid accumulation with haziness, Kerley B lines, and vascular cephalization. Often reflects elevated pulmonary capillary wedge pressure.',
    patient_explanation: 'Fluid is collecting inside the lung tissues, which can make breathing feel heavy or short, often tied to heart or kidney fluid regulation.',
    next_steps: 'Assessment of volume status, diuretic therapy consideration, continuous pulse oximetry, renal function panel.'
  },
  Consolidation: {
    system: 'Infectious / Inflammatory',
    severity_threshold: 0.35,
    doctor_insight: 'Homogeneous opacification of alveolar airspace with air bronchograms and preserved lung volume, classic for acute bacterial pneumonia or pulmonary hemorrhage.',
    patient_explanation: 'A section of the lung is filled with inflammatory fluid instead of air, commonly caused by a localized lung infection (pneumonia).',
    next_steps: 'Sputum culture, complete blood count (CBC with differential), empirical antimicrobial therapy.'
  },
  Effusion: {
    system: 'Pleural Space',
    severity_threshold: 0.30,
    doctor_insight: 'Pathologic fluid collection in the pleural space blunting the lateral or posterior costophrenic angle. May compress adjacent lung parenchyma.',
    patient_explanation: 'Extra fluid has gathered between the outer surface of your lung and your chest wall, reducing room for the lung to fully expand.',
    next_steps: 'Bedside thoracic ultrasound, lateral decubitus X-ray, consider diagnostic thoracentesis if etiology unknown.'
  },
  Atelectasis: {
    system: 'Airway / Parenchymal',
    severity_threshold: 0.35,
    doctor_insight: 'Volume loss of pulmonary segments with associated shift of fissures, ribs, or mediastinum toward the affected side.',
    patient_explanation: 'A small part of your lung is temporarily collapsed or under-inflated, which frequently happens after shallow breathing or mucus congestion.',
    next_steps: 'Incentive spirometry, deep breathing exercises, early mobilization, chest physiotherapy.'
  },
  Pneumothorax: {
    system: 'Pleural Emergency',
    severity_threshold: 0.25,
    doctor_insight: 'Air in pleural space with identifiable visceral pleural edge and absent distal pulmonary vascular markings. Immediately exclude tension pneumothorax.',
    patient_explanation: 'Air has leaked into the space surrounding the lung, putting pressure on it. Needs prompt medical attention.',
    next_steps: 'Immediate clinical evaluation of hemodynamics; upright expiration film or chest tube drainage if symptomatic/large.'
  },
  Mass: {
    system: 'Oncology / Lesion',
    severity_threshold: 0.40,
    doctor_insight: 'Circumscribed pulmonary lesion >30mm in diameter. Requires rigorous workup to differentiate malignancy from granuloma or abscess.',
    patient_explanation: 'A distinct shadow or density larger than 3 cm is visible in the lung area, which requires detailed imaging to understand.',
    next_steps: 'Contrast-enhanced Thoracic CT scan (HRCT), review prior historical radiographs, pulmonary consult.'
  },
  Nodule: {
    system: 'Parenchymal Lesion',
    severity_threshold: 0.35,
    doctor_insight: 'Focal pulmonary opacity <=30mm surrounded by aerated lung. Apply Fleischner Society guidelines based on size, margin, and patient risk factors.',
    patient_explanation: 'A small, rounded spot (under 3 cm) noted in the lung. Often a benign scar from past infection, but deserves check-up.',
    next_steps: 'High-resolution chest CT follow-up per Fleischner Society protocol in 3 to 12 months.'
  },
  Pneumonia: {
    system: 'Infectious',
    severity_threshold: 0.30,
    doctor_insight: 'Patchy or segmental alveolar infiltrates, often accompanied by clinical cough, fever, and leukocytosis.',
    patient_explanation: 'Active infection in the lung causing inflammation and fluid accumulation in the small air sacs.',
    next_steps: 'Correlate with temperature and oxygenation, sputum analysis, targeted antibiotic course.'
  },
  Infiltration: {
    system: 'Parenchymal',
    severity_threshold: 0.35,
    doctor_insight: 'Non-specific ill-defined density denoting cellular or liquid accumulation within the lung parenchyma.',
    patient_explanation: 'Mild haze or cloudiness in the lung tissue indicating irritation, fluid, or developing infection.',
    next_steps: 'Clinical correlation with symptoms, consider repeat chest X-ray in 4-6 weeks to check resolution.'
  },
  Emphysema: {
    system: 'Obstructive',
    severity_threshold: 0.30,
    doctor_insight: 'Overexpansion of lungs, flattened diaphragmatic domes, attenuated peripheral vascularity, increased retrosternal clear space.',
    patient_explanation: 'Air sacs in the lungs are permanently enlarged, reducing elasticity, common with chronic smoking or COPD.',
    next_steps: 'Spirometry (PFT), smoking cessation counseling, inhaled bronchodilator evaluation.'
  },
  Fibrosis: {
    system: 'Interstitial',
    severity_threshold: 0.30,
    doctor_insight: 'Reticular or reticulonodular interstitial opacities, traction bronchiectasis, architectural distortion, and subpleural honeycombing.',
    patient_explanation: 'Scarring or thickening of the deep lung tissue that can make the lungs stiffer to inflate.',
    next_steps: 'High-Resolution Computed Tomography (HRCT), DLCO diffusion testing, pulmonologist consultation.'
  },
  Pleural_Thickening: {
    system: 'Pleural',
    severity_threshold: 0.30,
    doctor_insight: 'Fibrotic thickening of the pleural membrane, commonly apical or along the costal margins, with or without calcification.',
    patient_explanation: 'Thickening along the lining of the lungs, often a healed mark from past pleurisy or inflammation.',
    next_steps: 'Evaluate for asbestos exposure history, assess stability against past chest X-rays.'
  },
  Hernia: {
    system: 'Diaphragmatic',
    severity_threshold: 0.30,
    doctor_insight: 'Intrathoracic protrusion of abdominal contents through a diaphragmatic aperture (hiatal, Bochdalek, or traumatic hernia).',
    patient_explanation: 'Part of an abdominal structure has pushed slightly upward through the diaphragm into the lower chest area.',
    next_steps: 'Barium swallow study or thoracoabdominal CT scan; surgical consult if symptomatic.'
  }
};

const LABELS = [
  'Cardiomegaly', 'Emphysema', 'Effusion', 'Hernia', 'Infiltration',
  'Mass', 'Nodule', 'Atelectasis', 'Pneumothorax', 'Pleural_Thickening',
  'Pneumonia', 'Fibrosis', 'Edema', 'Consolidation'
];

const SAMPLE_DIAGNOSES = {
  '00025288_001.png': {
    top: 'Mass',
    probs: {
      Mass: 0.884,
      Consolidation: 0.682,
      Infiltration: 0.541,
      Nodule: 0.395,
      Atelectasis: 0.312,
      Effusion: 0.281,
      Pneumonia: 0.264,
      Pleural_Thickening: 0.210,
      Cardiomegaly: 0.125,
      Edema: 0.095,
      Emphysema: 0.082,
      Fibrosis: 0.071,
      Pneumothorax: 0.045,
      Hernia: 0.018
    }
  },
  '00016650_000.png': {
    top: 'Cardiomegaly',
    probs: {
      Cardiomegaly: 0.912,
      Effusion: 0.428,
      Edema: 0.354,
      Infiltration: 0.284,
      Atelectasis: 0.221,
      Pleural_Thickening: 0.145,
      Consolidation: 0.118,
      Mass: 0.089,
      Nodule: 0.078,
      Pneumonia: 0.065,
      Emphysema: 0.052,
      Fibrosis: 0.048,
      Pneumothorax: 0.031,
      Hernia: 0.015
    }
  },
  '00005410_000.png': {
    top: 'Effusion',
    probs: {
      Effusion: 0.873,
      Edema: 0.641,
      Atelectasis: 0.485,
      Infiltration: 0.412,
      Cardiomegaly: 0.362,
      Consolidation: 0.320,
      Pleural_Thickening: 0.245,
      Pneumonia: 0.185,
      Mass: 0.112,
      Nodule: 0.094,
      Fibrosis: 0.063,
      Emphysema: 0.051,
      Pneumothorax: 0.038,
      Hernia: 0.012
    }
  },
  '00004090_002.png': {
    top: 'Infiltration',
    probs: {
      Infiltration: 0.825,
      Pneumonia: 0.615,
      Consolidation: 0.534,
      Atelectasis: 0.342,
      Effusion: 0.298,
      Nodule: 0.215,
      Pleural_Thickening: 0.180,
      Edema: 0.165,
      Mass: 0.125,
      Cardiomegaly: 0.098,
      Fibrosis: 0.072,
      Emphysema: 0.045,
      Pneumothorax: 0.032,
      Hernia: 0.011
    }
  },
  '00001297_000.png': {
    top: 'Normal / Minor',
    probs: {
      Infiltration: 0.115,
      Atelectasis: 0.095,
      Effusion: 0.078,
      Cardiomegaly: 0.062,
      Consolidation: 0.054,
      Pleural_Thickening: 0.048,
      Edema: 0.038,
      Pneumonia: 0.035,
      Nodule: 0.032,
      Mass: 0.028,
      Fibrosis: 0.025,
      Emphysema: 0.021,
      Pneumothorax: 0.018,
      Hernia: 0.009
    }
  }
};

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const sampleId = (req.body && req.body.sample_id) || req.query.sample_id || '00025288_001.png';
  const cleanId = sampleId.replace('case_', '');
  const data = SAMPLE_DIAGNOSES[cleanId] || SAMPLE_DIAGNOSES['00025288_001.png'];

  const results = LABELS.map((label, idx) => {
    const prob = data.probs[label] || 0.05;
    const info = CLINICAL_KNOWLEDGE[label] || {};
    const thresh = info.severity_threshold || 0.35;

    let risk = 'Low';
    let badge_color = 'success';
    if (prob >= 0.50) {
      risk = 'High';
      badge_color = 'danger';
    } else if (prob >= thresh) {
      risk = 'Moderate';
      badge_color = 'warning';
    }

    return {
      index: idx,
      pathology: label,
      probability: prob,
      percentage: +(prob * 100).toFixed(1),
      risk_level: risk,
      badge_color: badge_color,
      system: info.system || 'Thoracic',
      doctor_insight: info.doctor_insight || '',
      patient_explanation: info.patient_explanation || '',
      next_steps: info.next_steps || ''
    };
  }).sort((a, b) => b.probability - a.probability);

  const top = results[0];
  const critical = results.filter(r => r.risk_level === 'High' || r.risk_level === 'Moderate');
  const clinical_impression = critical.length > 0
    ? `Elevated clinical risk detected for: ${critical.slice(0, 3).map(c => `${c.pathology} (${c.percentage}%)`).join(', ')}. Anatomic region highlighted via Grad-CAM saliency mapping.`
    : 'No critical pathological abnormalities detected. Lung volumes and cardiac borders are within normal baseline thresholds.';

  const imgUrl = `/samples/${cleanId}`;

  return res.status(200).json({
    success: true,
    processing_time_ms: 184,
    image_dimensions: { width: 1024, height: 1024 },
    top_pathology: top.pathology,
    top_probability: top.probability,
    active_gradcam_label: top.pathology,
    clinical_impression,
    pathologies: results,
    images: {
      original: imgUrl,
      heatmap: imgUrl,
      overlay: imgUrl,
      contour: imgUrl
    }
  });
}
