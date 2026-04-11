const CLAUDE_WEB_URL = 'https://claude.ai';
const CLAUDE_API_URL = 'https://claude.ai/api';

class ClaudeService {
    constructor() {
        this.conversationContext = new Map();
    }

    async createConversation(sessionKey, model = 'claude-3-haiku-20240307') {
        const response = await fetch(`${CLAUDE_API_URL}/conversation`, {
            method: 'POST',
            headers: {
                'Cookie': `sessionKey=${sessionKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model,
            }),
        });

        if (!response.ok) {
            throw new Error(`Failed to create conversation: ${response.status}`);
        }

        const data = await response.json();
        return data.uuid;
    }

    async sendMessage(sessionKey, message, conversationId = null, model = 'claude-3-haiku-20240307') {
        if (!conversationId) {
            conversationId = await this.createConversation(sessionKey, model);
        }

        const response = await fetch(`${CLAUDE_API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Cookie': `sessionKey=${sessionKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: message,
                conversation_uuid: conversationId,
                model,
                stream: false,
            }),
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Claude API error: ${response.status} - ${error}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(`Claude API error: ${data.error.message}`);
        }

        const assistantMessage = data.completion || '';
        
        if (data.chat_history_id) {
            this.conversationContext.set(conversationId, data.chat_history_id);
        }

        return {
            message: assistantMessage,
            conversationId: conversationId,
            model: model,
        };
    }

    async chatComplete(sessionKey, messages, model = 'claude-3-haiku-20240307') {
        const lastMessage = messages[messages.length - 1]?.content || '';
        
        const result = await this.sendMessage(sessionKey, lastMessage, null, model);
        
        const usage = this.estimateTokens(lastMessage, result.message);

        return {
            id: `chatcmpl-${Date.now()}`,
            object: 'chat.completion',
            created: Date.now(),
            model: model,
            choices: [
                {
                    index: 0,
                    message: {
                        role: 'assistant',
                        content: result.message,
                    },
                    finish_reason: 'stop',
                }
            ],
            usage: {
                prompt_tokens: usage.prompt,
                completion_tokens: usage.completion,
                total_tokens: usage.total,
            },
        };
    }

    estimateTokens(prompt, completion) {
        const promptWords = prompt.split(/\s+/).length;
        const completionWords = completion.split(/\s+/).length;
        
        return {
            prompt: Math.ceil(promptWords * 1.3),
            completion: Math.ceil(completionWords * 1.3),
            total: Math.ceil((promptWords + completionWords) * 1.3),
        };
    }

    clearConversation(conversationId) {
        if (conversationId) {
            this.conversationContext.delete(conversationId);
        }
    }

    getAvailableModels() {
        return [
            {
                id: 'claude-3-haiku-20240307',
                name: 'Claude 3 Haiku',
                provider: 'claude',
            },
            {
                id: 'claude-3-sonnet-20240229',
                name: 'Claude 3 Sonnet',
                provider: 'claude',
            },
            {
                id: 'claude-3-opus-20240229',
                name: 'Claude 3 Opus',
                provider: 'claude',
            },
        ];
    }
}

export default new ClaudeService();
