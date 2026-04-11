const CHATGPT_WEB_URL = 'https://chat.openai.com';
const CHATGPT_API_URL = 'https://chat.openai.com/backend-api';

class ChatGPTService {
    constructor() {
        this.conversationContext = new Map();
    }

    async createConversation(sessionToken) {
        const response = await fetch(`${CHATGPT_API_URL}/conversation`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${sessionToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conversation_mode: { kind: 'single' },
                force_nulligen: false,
            }),
        });

        if (!response.ok) {
            throw new Error(`Failed to create conversation: ${response.status}`);
        }

        const data = await response.json();
        return data.id;
    }

    async sendMessage(sessionToken, message, conversationId = null, model = 'gpt-3.5-turbo') {
        const convId = conversationId || await this.createConversation(sessionToken);

        const body = {
            conversation_id: convId,
            parent_message_id: this.conversationContext.get(convId) || '',
            model,
            messages: [
                {
                    id: convId,
                    role: 'user',
                    content: {
                        content_type: 'text',
                        parts: [message],
                    },
                },
            ],
            timezone_offset: 0,
        };

        const response = await fetch(`${CHATGPT_API_URL}/conversation/talk`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${sessionToken}`,
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`ChatGPT API error: ${response.status} - ${error}`);
        }

        const text = await response.text();
        const lines = text.split('\n').filter(line => line.startsWith('data: '));
        
        let lastMessage = '';
        for (const line of lines) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            try {
                const json = JSON.parse(data);
                if (json.message && json.message.content) {
                    lastMessage = json.message.content.parts[0];
                    this.conversationContext.set(convId, json.message.id);
                }
            } catch (e) {
                // Continue parsing
            }
        }

        return {
            message: lastMessage,
            conversationId: convId,
            model: model,
        };
    }

    async chatComplete(sessionToken, messages, model = 'gpt-3.5-turbo') {
        const lastMessage = messages[messages.length - 1]?.content || '';
        
        const result = await this.sendMessage(sessionToken, lastMessage, null, model);
        
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
                id: 'gpt-3.5-turbo',
                name: 'GPT-3.5 Turbo',
                provider: 'chatgpt',
            },
            {
                id: 'gpt-4',
                name: 'GPT-4',
                provider: 'chatgpt',
            },
        ];
    }
}

export default new ChatGPTService();
