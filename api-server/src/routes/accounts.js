import { Router } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { accountsDb, apiKeysDb } from '../database/db.js';

const router = Router();

/**
 * GET /v1/accounts
 * List all registered accounts
 */
router.get('/', (req, res) => {
    try {
        const accounts = accountsDb.findAll();
        
        const formattedAccounts = accounts.map(account => ({
            id: account.id,
            provider: account.provider,
            email: account.email,
            messages_used: account.messages_used,
            tokens_used: account.tokens_used,
            created_at: account.created_at,
            last_used: account.last_used,
        }));

        res.json({
            data: formattedAccounts,
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
 * POST /v1/accounts
 * Register a new account
 */
router.post('/', (req, res) => {
    try {
        const { provider, email, session_token, refresh_token, access_token, expires_at } = req.body;

        if (!provider) {
            return res.status(400).json({
                error: {
                    message: 'provider is required',
                    type: 'invalid_request_error',
                    param: 'provider',
                    code: 'missing_parameter',
                },
            });
        }

        if (!session_token) {
            return res.status(400).json({
                error: {
                    message: 'session_token is required',
                    type: 'invalid_request_error',
                    param: 'session_token',
                    code: 'missing_parameter',
                },
            });
        }

        const account = {
            id: uuidv4(),
            provider,
            email: email || null,
            session_token,
            refresh_token: refresh_token || null,
            access_token: access_token || null,
            expires_at: expires_at || null,
            created_at: Date.now(),
            last_used: Date.now(),
        };

        accountsDb.create(account);

        res.status(201).json({
            id: account.id,
            provider: account.provider,
            email: account.email,
            created_at: account.created_at,
            object: 'account',
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
 * GET /v1/accounts/:id
 * Get account details
 */
router.get('/:id', (req, res) => {
    try {
        const account = accountsDb.findById(req.params.id);

        if (!account) {
            return res.status(404).json({
                error: {
                    message: 'Account not found',
                    type: 'invalid_request_error',
                    param: 'id',
                    code: 'not_found',
                },
            });
        }

        res.json({
            id: account.id,
            provider: account.provider,
            email: account.email,
            messages_used: account.messages_used,
            tokens_used: account.tokens_used,
            created_at: account.created_at,
            last_used: account.last_used,
            object: 'account',
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
 * PUT /v1/accounts/:id
 * Update account tokens/session
 */
router.put('/:id', (req, res) => {
    try {
        const { session_token, refresh_token, access_token, expires_at } = req.body;
        const account = accountsDb.findById(req.params.id);

        if (!account) {
            return res.status(404).json({
                error: {
                    message: 'Account not found',
                    type: 'invalid_request_error',
                    param: 'id',
                    code: 'not_found',
                },
            });
        }

        const updateData = { last_used: Date.now() };

        if (session_token) updateData.session_token = session_token;
        if (refresh_token) updateData.refresh_token = refresh_token;
        if (access_token) updateData.access_token = access_token;
        if (expires_at) updateData.expires_at = expires_at;

        accountsDb.update(req.params.id, updateData);

        res.json({
            id: account.id,
            provider: account.provider,
            email: account.email,
            updated: true,
            object: 'account',
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
 * DELETE /v1/accounts/:id
 * Remove/deactivate an account
 */
router.delete('/:id', (req, res) => {
    try {
        const account = accountsDb.findById(req.params.id);

        if (!account) {
            return res.status(404).json({
                error: {
                    message: 'Account not found',
                    type: 'invalid_request_error',
                    param: 'id',
                    code: 'not_found',
                },
            });
        }

        accountsDb.delete(req.params.id);

        res.json({
            id: req.params.id,
            deleted: true,
            object: 'account',
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
 * GET /v1/accounts/:id/quota
 * Get quota status for an account
 */
router.get('/:id/quota', (req, res) => {
    try {
        const account = accountsDb.findById(req.params.id);

        if (!account) {
            return res.status(404).json({
                error: {
                    message: 'Account not found',
                    type: 'invalid_request_error',
                    param: 'id',
                    code: 'not_found',
                },
            });
        }

        const quotaInfo = {
            account_id: account.id,
            provider: account.provider,
            messages_used: account.messages_used,
            tokens_used: account.tokens_used,
            status: 'active',
        };

        if (account.provider === 'chatgpt') {
            quotaInfo.limits = {
                messages_per_hour: 40,
                messages_warning_threshold: 32,
            };
        } else if (account.provider === 'claude') {
            quotaInfo.limits = {
                messages_per_hour: 50,
                messages_warning_threshold: 40,
            };
        }

        const warningThreshold = quotaInfo.limits?.messages_warning_threshold || 32;
        if (account.messages_used >= warningThreshold) {
            quotaInfo.warning = `Approaching limit: ${account.messages_used}/${quotaInfo.limits.messages_per_hour} messages used`;
        }

        res.json(quotaInfo);
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
