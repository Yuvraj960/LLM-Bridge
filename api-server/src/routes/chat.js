import { Router } from 'express';
import { accountsDb } from '../database/db.js';
import ChatGPTService from '../services/chatgpt.js';
import ClaudeService from '../services/claude.js';

const router = Router();
const chatGptService = ChatGPTService;
const claudeService = ClaudeService;

/**
 * POST /v1/chat/completions
 * OpenAI-compatible chat completion endpoint
 */
router.post('/', async (req, res) => {
    try {
        const { messages, model, temperature, max_tokens, stream, ...extra } = req.body;
        const account = req.account;

        if (!messages || !Array.isArray(messages) || messages.length === 0) {
            return res.status(400).json({
                error: {
                    message: 'messages is required and must be a non-empty array',
                    type: 'invalid_request_error',
                    param: 'messages',
                    code: 'missing_parameter',
                },
            });
        }

        let service;
        let actualModel = model;

        if (account.provider === 'chatgpt') {
            service = chatGptService;
            actualModel = model || 'gpt-3.5-turbo';
        } else if (account.provider === 'claude') {
            service = claudeService;
            actualModel = model || 'claude-3-haiku-20240307';
        } else {
            return res.status(400).json({
                error: {
                    message: `Unknown provider: ${account.provider}`,
                    type: 'invalid_request_error',
                    param: 'provider',
                    code: 'invalid_provider',
                },
            });
        }

        const result = await service.chatComplete(account.sessionToken, messages, actualModel);

        accountsDb.incrementUsage(account.id, 1, result.usage.total_tokens);

        res.json(result);
    } catch (error) {
        console.error('Chat completion error:', error);
        
        res.status(500).json({
            error: {
                message: error.message || 'Internal server error',
                type: 'server_error',
                code: 'internal_error',
            },
        });
    }
});

export default router;
