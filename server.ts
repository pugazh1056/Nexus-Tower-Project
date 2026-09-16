import express, { Request, Response } from 'express';
import cors from 'cors';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import http from 'node:http';
import { createProxyMiddleware, fixRequestBody } from 'http-proxy-middleware';
import { apiRouter } from './api_router.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;
const HOST = '0.0.0.0';

// Enable CORS
app.use(cors());

// Parse JSON and form bodies
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// If an external FASTAPI_URL is explicitly provided via environment, proxy /api requests to it;
// otherwise, serve all /api endpoints natively via the integrated TypeScript API router.
if (process.env.FASTAPI_URL) {
  const FASTAPI_TARGET = process.env.FASTAPI_URL;
  console.log(`[Nexus Tower] Proxying /api/* -> ${FASTAPI_TARGET}`);
  const apiProxy = createProxyMiddleware({
    target: FASTAPI_TARGET,
    changeOrigin: true,
    ws: true,
    pathFilter: '/api',
    on: {
      proxyReq: fixRequestBody,
      error: (err: Error, _req: http.IncomingMessage, res: http.ServerResponse | import('node:net').Socket) => {
        console.error(`[API Proxy Error] Unable to connect to FastAPI at ${FASTAPI_TARGET}:`, err.message);
        if ('writeHead' in res && !res.headersSent) {
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(
            JSON.stringify({
              error: 'Bad Gateway',
              message: 'FastAPI backend service is currently unavailable',
              target: FASTAPI_TARGET,
              details: err.message,
            })
          );
        }
      },
    },
  });
  app.use(apiProxy);
} else {
  console.log('[Nexus Tower] Serving /api/* via native TypeScript API router');
  app.use('/api', apiRouter);
}

// --- Static Assets & Clean Page Routes ---
app.use('/assets', express.static(path.join(__dirname, 'assets')));
app.use(express.static(__dirname, { extensions: ['html'] }));

app.get('/', (_req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/login', (_req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, 'login.html'));
});

app.get('/control-tower', (_req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, 'control-tower.html'));
});

app.get('/procurement', (_req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, 'procurement.html'));
});

app.get('/inventory', (_req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, 'inventory.html'));
});

app.get('/production', (_req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, 'production.html'));
});

app.get('/logistics', (_req: Request, res: Response) => {
  res.sendFile(path.join(__dirname, 'logistics.html'));
});

// Standalone Health Check for Express Gateway
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'ok',
    gateway: 'Nexus Tower Server',
    mode: process.env.FASTAPI_URL ? 'Proxy' : 'Native',
    timestamp: new Date().toISOString(),
    uptime_seconds: process.uptime(),
  });
});

// Start Express Server
app.listen(PORT, HOST, () => {
  console.log(`[Nexus Tower] Server listening at http://${HOST}:${PORT}`);
});
