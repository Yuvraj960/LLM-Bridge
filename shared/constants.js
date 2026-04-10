export const APP_NAME = 'LLM Bridge';
export const APP_VERSION = '1.0.0';

export const API_SERVER_DEFAULTS = {
    HOST: 'localhost',
    PORT: 11434,
};

export const PROVIDERS = {
    CHATGPT: 'chatgpt',
    CLAUDE: 'claude',
};

export const CHATGPT_MODELS = [
    'gpt-5',
];

export const CLAUDE_MODELS = [
    'claude-4.5-haiku',
    'claude-4.5-sonnet',
    'claude-4.5-opus',
];

export const QUOTA_LIMITS = {
    chatgpt: {
        messagesPerHour: 40,
        warningThreshold: 32,
    },
    claude: {
        messagesPerHour: 50,
        warningThreshold: 40,
    },
};
