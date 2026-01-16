const functions = require('firebase-functions');
const fetch = require('node-fetch');

const BACKEND_URL = 'https://ai-debate-api-66nr2u3stq-uk.a.run.app';

// Proxy function to forward requests to Cloud Run
exports.api = functions.https.onRequest(async (req, res) => {
  // Enable CORS
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.status(204).send('');
    return;
  }

  try {
    const path = req.path === '/' ? '' : req.path;
    const url = `${BACKEND_URL}${path}${req.url.includes('?') ? '?' + req.url.split('?')[1] : ''}`;
    
    const options = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      options.body = JSON.stringify(req.body);
    }

    const response = await fetch(url, options);
    
    // Handle streaming responses
    if (response.headers.get('content-type')?.includes('text/event-stream')) {
      res.set('Content-Type', 'text/event-stream');
      res.set('Cache-Control', 'no-cache');
      res.set('Connection', 'keep-alive');
      response.body.pipe(res);
    } else {
      const data = await response.text();
      res.status(response.status).send(data);
    }
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: error.message });
  }
});
