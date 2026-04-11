import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

import chatRoutes from './routes/chat.js';
import keysRoutes from './routes/keys.js';
import accountsRoutes from './routes/accounts.js';
import { authMiddleware, accountSwitchMiddleware } from './middleware/auth.js';
import ChatGPTService from './services/chatgpt.js';
import ClaudeService from './services/claude.js';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 11434;
const HOST = process.env.HOST || 'localhost';

const app = express();

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: Date.now() });
});

app.use('/v1/models', (req, res) => {
    const chatgptModels = ChatGPTService.getAvailableModels();
    const claudeModels = ClaudeService.getAvailableModels();
    
    res.json({
        data: [...chatgptModels, ...claudeModels].map(model => ({
            id: model.id,
            object: 'model',
            created: Date.now(),
            owned_by: model.provider,
            provider: model.provider,
        })),
        object: 'list',
    });
});

app.use('/v1/keys', keysRoutes);

app.use('/v1/accounts', accountsRoutes);

app.use('/v1/chat/completions', authMiddleware, accountSwitchMiddleware, chatRoutes);

app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
        error: {
            message: 'Internal server error',
            type: 'server_error',
            code: 'internal_error',
        },
    });
});

app.listen(PORT, HOST, () => {
    console.log(`
╔══════════════════════════════════════════════════════════════╗
║                   LLM Bridge API Server                      ║
╠══════════════════════════════════════════════════════════════╣
║  Server running at: http://${HOST}:${PORT}                   ║
║                                                              ║
║  Endpoints:                                                  ║
║    GET  /health              - Health check                  ║
║    GET  /v1/models           - List available models         ║
║    POST /v1/chat/completions - Chat completion (requires key)║
║    POST /v1/keys             - Generate API key              ║
║    GET  /v1/keys             - List API keys                 ║
║    GET  /v1/accounts         - List accounts                 ║
║    POST /v1/accounts         - Register account              ║
║    GET  /v1/accounts/:id/quota - Get quota status            ║
║                                                              ║
║  Usage:                                                      ║
║    curl -H "Authorization: Bearer <key>" \\                  ║
║         -H "X-Account-ID: <account-id>" \\                   ║
║         -X POST http://${HOST}:${PORT}/v1/chat/completions   ║
║         -d '{"messages":[{"role":"user","content":"Hi"}]}'   ║
╚══════════════════════════════════════════════════════════════╝
    `);
});

export default app;
