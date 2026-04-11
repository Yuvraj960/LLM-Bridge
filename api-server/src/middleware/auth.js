import { apiKeysDb } from '../database/db.js';

/**
 * Middleware to validate API key from Authorization header
 * Expected format: Authorization: Bearer <uuid-api-key>
 */
export async function authMiddleware(req, res, next) {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
            error: {
                message: 'Missing or invalid Authorization header',
                type: 'invalid_request_error',
                param: null,
                code: 'missing_authorization',
            },
        });
    }

    const apiKey = authHeader.slice(7);

    if (!apiKey) {
        return res.status(401).json({
            error: {
                message: 'Missing API key',
                type: 'invalid_request_error',
                param: null,
                code: 'missing_api_key',
            },
        });
    }

    const keyData = apiKeysDb.findByKey(apiKey);

    if (!keyData) {
        return res.status(401).json({
            error: {
                message: 'Invalid API key',
                type: 'invalid_request_error',
                param: null,
                code: 'invalid_api_key',
            },
        });
    }

    apiKeysDb.updateLastUsed(apiKey);

    req.apiKey = apiKey;
    req.accountId = keyData.account_id;
    req.account = {
        id: keyData.account_id,
        provider: keyData.provider,
        sessionToken: keyData.session_token,
        refreshToken: keyData.refresh_token,
        accessToken: keyData.access_token,
        expiresAt: keyData.expires_at,
    };

    next();
}

/**
 * Optional middleware to validate X-Account-ID header
 * Allows switching between accounts when using a single API key
 */
export async function accountSwitchMiddleware(req, res, next) {
    const accountIdHeader = req.headers['x-account-id'];

    if (accountIdHeader) {
        const { accountsDb } = await import('../database/db.js');
        const account = accountsDb.findById(accountIdHeader);

        if (!account) {
            return res.status(400).json({
                error: {
                    message: 'Invalid X-Account-ID',
                    type: 'invalid_request_error',
                    param: 'X-Account-ID',
                    code: 'invalid_account_id',
                },
            });
        }

        if (account.id !== req.accountId) {
            return res.status(403).json({
                error: {
                    message: 'Account ID mismatch - API key is linked to a different account',
                    type: 'invalid_request_error',
                    param: 'X-Account-ID',
                    code: 'account_mismatch',
                },
            });
        }

        req.account = {
            id: account.id,
            provider: account.provider,
            sessionToken: account.session_token,
            refreshToken: account.refresh_token,
            accessToken: account.access_token,
            expiresAt: account.expires_at,
        };
    }

    next();
}
