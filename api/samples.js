export default function handler(req, res) {
  const samples = [
    {
      id: 'case_00025288_001',
      filename: '00025288_001.png',
      url: '/samples/00025288_001.png',
      title: 'Case 1: Pulmonary Mass & Consolidation',
      patient: 'Male, 62yo - Persistent cough & localized chest discomfort',
      pathology: 'Mass',
      description: 'Prominent focal parenchymal density identified in upper lobe territory.'
    },
    {
      id: 'case_00016650_000',
      filename: '00016650_000.png',
      url: '/samples/00016650_000.png',
      title: 'Case 2: Cardiomegaly (Enlarged Cardiac Silhouette)',
      patient: 'Female, 68yo - Exertional dyspnea & hypertension history',
      pathology: 'Cardiomegaly',
      description: 'Distinct transverse enlargement of heart border >50% thoracic diameter.'
    },
    {
      id: 'case_00005410_000',
      filename: '00005410_000.png',
      url: '/samples/00005410_000.png',
      title: 'Case 3: Pleural Effusion & Pulmonary Edema',
      patient: 'Male, 71yo - Orthopnea & bilateral basilar crackles',
      pathology: 'Effusion',
      description: 'Blunting of costophrenic angles accompanied by vascular congestion.'
    },
    {
      id: 'case_00004090_002',
      filename: '00004090_002.png',
      url: '/samples/00004090_002.png',
      title: 'Case 4: Infiltration & Bronchopneumonia',
      patient: 'Female, 45yo - High fever, productive cough, and pleuritic pain',
      pathology: 'Infiltration',
      description: 'Patchy reticular and alveolar opacities across lower lung zones.'
    },
    {
      id: 'case_00001297_000',
      filename: '00001297_000.png',
      url: '/samples/00001297_000.png',
      title: 'Case 5: Baseline Check (Clear / Low Pathology)',
      patient: 'Male, 34yo - Routine pre-employment occupational physical',
      pathology: 'Normal / Minor',
      description: 'Lungs clear bilaterally. Normal cardiac silhouette and costophrenic angles.'
    }
  ];

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  return res.status(200).json({ samples });
}
