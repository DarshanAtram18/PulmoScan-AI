export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { target_pathology, colormap, opacity, threshold, image_base64 } = req.body || {};
  return res.status(200).json({
    success: true,
    active_pathology: target_pathology || 'Mass',
    colormap: colormap || 'magma',
    opacity: opacity || 0.45,
    threshold: threshold || 0.15,
    images: {
      heatmap: image_base64 || '',
      overlay: image_base64 || '',
      contour: image_base64 || ''
    }
  });
}
