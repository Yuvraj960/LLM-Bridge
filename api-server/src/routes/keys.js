import { Router } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { accountsDb, apiKeysDb } from '../database/db.js';

const router = Router();

/**
 * GET /v1/keys
 * List all API keys (requires admin/master key or returns all)
 */
router.get('/', (req, res) => {
    try {
        const keys = apiKeysDb.findAll();

        const formattedKeys = keys.map(key => ({
            key: key.key,
            account_id: key.account_id,
            label: key.label,
            provider: key.provider,
            created_at: key.created_at,
            last_used: key.last_used,
            is_active: !!key.is_active,
            object: 'api_key',
        }));

        res.json({
            data: formattedKeys,
            object: 'list',
        });
    } catch (error) {
        res.status(500).json({
            error: {
                message: error.message,
                type: 'server_error',
                code: 'internal_error',
            },
        });
    }
});

/**
 * POST /v1/keys
 * Generate a new API key for an account
 * Body: { account_id: string, label?: string }
 */
router.post('/', (req, res) => {
    try {
        const { account_id, label } = req.body;

        if (!account_id) {
            return res.status(400).json({
                error: {
                    message: 'account_id is required',
                    type: 'invalid_request_error',
                    param: 'account_id',
                    code: 'missing_parameter',
                },
            });
        }

        const account = accountsDb.findById(account_id);
        if (!account) {
            return res.status(404).json({
                error: {
                    message: 'Account not found',
                    type: 'invalid_request_error',
                    param: 'account_id',
                    code: 'not_found',
                },
            });
        }

        const apiKey = uuidv4();

        const keyData = {
            key: apiKey,
            account_id,
            label: label || null,
            created_at: Date.now(),
            is_active: 1,
        };

        apiKeysDb.create(keyData);

        res.status(201).json({
            key: apiKey,
            account_id: account_id,
            label: keyData.label,
            created_at: keyData.created_at,
            object: 'api_key',
        });
    } catch (error) {
        res.status(500).json({
            error: {
                message: error.message,
                type: 'server_error',
                code: 'internal_error',
            },
        });
    }
});

/**
 * GET /v1/keys/:key
 * Get API key details
 */
router.get('/:key', (req, res) => {
    try {
        const keyData = apiKeysDb.findByKey(req.params.key);

        if (!keyData) {
            return res.status(404).json({
                error: {
                    message: 'API key not found',
                    type: 'invalid_request_error',
                    param: 'key',
                    code: 'not_found',
                },
            });
        }

        res.json({
            key: keyData.key,
            account_id: keyData.account_id,
            provider: keyData.provider,
            created_at: keyData.created_at,
            last_used: keyData.last_used,
            is_active: !!keyData.is_active,
            object: 'api_key',
        });
    } catch (error) {
        res.status(500).json({
            error: {
                message: error.message,
                type: 'server_error',
                code: 'internal_error',
            },
        });
    }
});

/**
 * DELETE /v1/keys/:key
 * Revoke an API key
 */
router.delete('/:key', (req, res) => {
    try {
        const keyData = apiKeysDb.findByKey(req.params.key);

        if (!keyData) {
            return res.status(404).json({
                error: {
                    message: 'API key not found',
                    type: 'invalid_request_error',
                    param: 'key',
                    code: 'not_found',
                },
            });
        }

        apiKeysDb.delete(req.params.key);

        res.json({
            key: req.params.key,
            deleted: true,
            object: 'api_key',
        });
    } catch (error) {
        res.status(500).json({
            error: {
                message: error.message,
                type: 'server_error',
                code: 'internal_error',
            },
        });
    }
});

export default router;
