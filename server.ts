import express, { Request, Response } from 'express';
import cors from 'cors';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn, ChildProcess } from 'node:child_process';
import http from 'node:http';
import { createProxyMiddleware, fixRequestBody } from 'http-proxy-middleware';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;
const HOST = '0.0.0.0';

// Determine FastAPI Backend Target Port / URL (Default 8001 to avoid container control-plane port conflict)
const FASTAPI_PORT = process.env.FASTAPI_PORT ? parseInt(process.env.FASTAPI_PORT, 10) : 8001;
const FASTAPI_TARGET = process.env.FASTAPI_URL || `http://127.0.0.1:${FASTAPI_PORT}`;

// Enable CORS
app.use(cors());

// Configure Reverse Proxy for all /api/* routes to FastAPI
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

// Mount reverse proxy for /api routes before body parsers
app.use(apiProxy);

// Body parsing for non-proxied routes
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

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
    gateway: 'Express Proxy',
    proxy_target: FASTAPI_TARGET,
    timestamp: new Date().toISOString(),
    uptime_seconds: process.uptime(),
  });
});

// Start Background FastAPI process if not already managed
let fastApiProcess: ChildProcess | null = null;

function ensureFastApiProcess() {
  const req = http.get(`${FASTAPI_TARGET}/api/health`, (res) => {
    if (res.statusCode === 200) {
      console.log(`[FastAPI Gateway] FastAPI service is already alive and responsive at ${FASTAPI_TARGET}`);
    } else {
      spawnFastApi();
    }
  });

  req.on('error', () => {
    spawnFastApi();
  });
}

function spawnFastApi() {
  console.log(`[FastAPI Gateway] Launching FastAPI backend process on port ${FASTAPI_PORT}...`);
  fastApiProcess = spawn(
    'python3',
    ['-m', 'uvicorn', 'app.main:app', '--app-dir', 'backend', '--host', '127.0.0.1', '--port', FASTAPI_PORT.toString(), '--reload'],
    {
      cwd: __dirname,
      env: {
        ...process.env,
        PYTHONPATH: path.join(__dirname, 'backend'),
      },
      stdio: 'inherit',
    }
  );

  fastApiProcess.on('error', (err) => {
    console.error('[FastAPI Gateway] Failed to start FastAPI process:', err);
  });

  fastApiProcess.on('exit', (code, signal) => {
    console.log(`[FastAPI Gateway] FastAPI process exited with code ${code}, signal ${signal}`);
  });
}

// Clean up child process on exit
process.on('SIGTERM', () => {
  if (fastApiProcess) {
    fastApiProcess.kill('SIGTERM');
  }
  process.exit(0);
});

process.on('SIGINT', () => {
  if (fastApiProcess) {
    fastApiProcess.kill('SIGINT');
  }
  process.exit(0);
});

// Start Express Server
app.listen(PORT, HOST, () => {
  console.log(`[Nexus Tower] Express Gateway listening at http://${HOST}:${PORT}`);
  console.log(`[Nexus Tower] Proxying /api/* -> ${FASTAPI_TARGET}`);
  ensureFastApiProcess();
});
