import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';
import type { ChatMessage } from '@/types';
import SocraticProbeCard from './SocraticProbeCard';

function parseInlineContent(text: string): string {
  return text
    // Match inline code blocks, reducing vertical padding to fix line-height
    .replace(/`([^`]+)`/g, '<code class="px-1.5 py-[1px] rounded bg-[var(--surface-2)] border border-[var(--surface-border)] text-[var(--accent-amber)] text-xs font-mono">$1</code>')
    // Bold matching
    .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold text-[var(--text-primary)]">$1</strong>')
    // Italic matching: Use lookarounds to ensure we only match underscores surrounded by boundaries, NOT inside variable names like code_challenge
    .replace(/(?<!\w)_([a-zA-Z0-9 ]+?)_(?!\w)/g, '<em class="italic text-[var(--text-secondary)]">$1</em>')
    .replace(/\n/g, '<br/>');
}

function renderMarkdown(content: string) {
  if (!content) return '';

  // 1. Strip legacy concatenated Socratic probe text and hr line
  let cleaned = content
    .replace(/\n*---\s*\n\*\*[\s\S]*?\*\*$/gi, '')
    .trim();

  // 2. Collapse excessive whitespace / multi-newlines down to clean double newlines
  cleaned = cleaned.replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n');

  // 3. Extract code blocks to avoid corrupting their internal formatting
  const codeBlocks: string[] = [];
  cleaned = cleaned.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
    const idx = codeBlocks.length;
    codeBlocks.push(
      `<pre class="my-3 p-3.5 rounded-xl bg-[var(--surface-2)] border border-[var(--surface-border)] overflow-x-auto"><code class="language-${lang || 'text'} text-xs font-mono text-[var(--accent-amber)] leading-relaxed">${code.replace(/</g, '&lt;')}</code></pre>`
    );
    return `__CODE_BLOCK_${idx}__`;
  });

  // 4. Split into paragraph blocks
  const blocks = cleaned.split(/\n\n+/);

  const formattedBlocks = blocks.map((block) => {
    let text = block.trim();
    if (!text) return '';

    if (text.startsWith('__CODE_BLOCK_')) {
      const match = text.match(/__CODE_BLOCK_(\d+)__/);
      if (match) {
        const idx = parseInt(match[1], 10);
        return codeBlocks[idx] || '';
      }
    }

    // Handle Headings
    if (/^#\s+(.+)$/.test(text)) {
      const h1Text = text.replace(/^#\s+/, '');
      return `<h1 class="text-xl font-bold tracking-tight text-[var(--text-primary)] mt-4 mb-2 border-b border-[var(--surface-border)] pb-1">${parseInlineContent(h1Text)}</h1>`;
    }
    if (/^##\s+(.+)$/.test(text)) {
      const h2Text = text.replace(/^##\s+/, '');
      return `<h2 class="text-lg font-bold tracking-tight text-[var(--accent-amber)] mt-3.5 mb-2">${parseInlineContent(h2Text)}</h2>`;
    }
    if (/^###\s+(.+)$/.test(text)) {
      const h3Text = text.replace(/^###\s+/, '');
      return `<h3 class="text-base font-semibold text-[var(--text-primary)] mt-3 mb-1.5">${parseInlineContent(h3Text)}</h3>`;
    }

    // Handle Bulleted Lists (- or *)
    if (/^[-*]\s+/m.test(text)) {
      const items = text.split(/\n/);
      const listItems = items
        .map((item) => {
          const cleanItem = item.replace(/^[-*]\s+/, '').trim();
          if (!cleanItem) return '';
          return `<li class="flex items-start gap-2.5 mb-1.5 text-[14.5px] leading-relaxed text-[var(--text-primary)]"><span class="text-[var(--accent-amber)] font-bold mt-1 text-xs">•</span><span>${parseInlineContent(cleanItem)}</span></li>`;
        })
        .join('');
      return `<ul class="my-2.5 space-y-1 pl-1">${listItems}</ul>`;
    }

    // Handle Numbered Lists (1. , 2. )
    if (/^\d+\.\s+/m.test(text)) {
      const items = text.split(/\n/);
      const listItems = items
        .map((item, idx) => {
          const cleanItem = item.replace(/^\d+\.\s+/, '').trim();
          if (!cleanItem) return '';
          return `<li class="flex items-start gap-2.5 mb-1.5 text-[14.5px] leading-relaxed text-[var(--text-primary)]"><span class="font-mono text-[var(--accent-amber)] font-bold text-xs mt-0.5">${idx + 1}.</span><span>${parseInlineContent(cleanItem)}</span></li>`;
        })
        .join('');
      return `<ol class="my-2.5 space-y-1 pl-1">${listItems}</ol>`;
    }

    // Handle Note Callout Boxes (*Note:* or Note:)
    if (text.startsWith('*Note:') || text.startsWith('_Note:') || text.startsWith('Note:')) {
      return `<div class="my-3.5 p-3.5 rounded-xl border-l-4 border-[var(--accent-amber)] bg-[var(--surface-2)] text-xs text-[var(--text-secondary)] font-mono leading-relaxed shadow-sm">${parseInlineContent(text)}</div>`;
    }

    // Default Paragraph
    return `<p class="mb-3.5 leading-relaxed text-[14.5px] font-normal text-[var(--text-primary)] tracking-normal">${parseInlineContent(text)}</p>`;
  });

  return formattedBlocks.join('');
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className="max-w-[85%] rounded-2xl px-4 py-3 border shadow-sm"
        style={{
          background: isUser
            ? 'var(--surface-2)'
            : 'var(--surface-1)',
          borderColor: 'var(--surface-border)',
          borderWidth: '1px',
        }}
      >
        <div className="flex items-center gap-2 mb-1.5">
          <span
            className="text-xs font-bold uppercase tracking-wider"
            style={{
              color: isUser ? 'var(--accent-amber)' : 'var(--accent-violet)',
            }}
          >
            {isUser ? 'YOU' : 'AGENT 4 (Teacher)'}
          </span>
        </div>
        {isUser ? (
          <p className="text-sm leading-relaxed font-medium text-primary-c">
            {msg.content}
          </p>
        ) : (
          <div
            className="editorial-prose text-base text-primary-c"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
          />
        )}
        {!isUser && msg.probe_question && (
          <SocraticProbeCard
            question={msg.probe_question}
            targetConcept={msg.probe_target_concept || undefined}
          />
        )}
      </div>
    </motion.div>
  );
}

export default function ChatTerminal() {
  const messages = useSyntapseStore((s) => s.messages);
  const isAgentThinking = useSyntapseStore((s) => s.isAgentThinking);
  const chatInput = useSyntapseStore((s) => s.chatInput);
  const setChatInput = useSyntapseStore((s) => s.setChatInput);
  const sendChatMessage = useSyntapseStore((s) => s.sendChatMessage);
  const statusMessage = useSyntapseStore((s) => s.statusMessage);
  const telemetrySteps = useSyntapseStore((s) => s.telemetrySteps);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;

    const lastMsg = messages[messages.length - 1];
    const isUserLast = lastMsg && lastMsg.role === 'user';

    const scroll = () => {
      const isNearBottom = container.scrollHeight - container.clientHeight - container.scrollTop < 250;
      if (isNearBottom || isUserLast) {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: isUserLast ? 'auto' : 'smooth',
        });
      }
    };

    if (isUserLast) {
      scroll();
    } else {
      const timer = setTimeout(scroll, 80);
      return () => clearTimeout(timer);
    }
  }, [messages, isAgentThinking, telemetrySteps]);

  const handleSend = () => {
    if (chatInput.trim().length === 0 || isAgentThinking) return;
    sendChatMessage(chatInput.trim());
  };

  return (
    <div
      className="flex flex-col h-full"
      style={{ background: 'var(--surface-0)' }}
    >
      {/* Chat Stream */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto chat-scroll px-4 py-4"
      >
        {messages.length === 0 && !isAgentThinking && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <p className="text-primary-c font-medium text-sm">
              The chamber is open. Ask a question to begin your Socratic exploration.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} />
        ))}

        {/* Agent Thinking Indicator */}
        <AnimatePresence>
          {isAgentThinking && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex justify-start mb-4"
            >
              <div
                className="rounded-2xl px-4 py-3 max-w-[85%] border"
                style={{
                  background: 'var(--surface-1)',
                  borderColor: 'var(--surface-border)',
                  borderWidth: '1px',
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-c">
                    AGENT 4 (Teacher)
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          delay: i * 0.2,
                        }}
                        className="w-2 h-2 rounded-full bg-amber-c"
                      />
                    ))}
                  </div>
                  <span className="text-xs text-secondary-c font-medium">
                    {statusMessage}
                  </span>
                </div>
                {telemetrySteps.length > 0 && (
                  <div className="mt-3 space-y-1">
                    {telemetrySteps.map((step, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-2 text-xs text-muted-c"
                      >
                        <span className="font-mono text-amber-c font-semibold">
                          {step.agent}
                        </span>
                        <span>{step.label}</span>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Terminal Input */}
      <div
        className="border-t p-3"
        style={{ borderColor: 'var(--surface-border)' }}
      >
        <div
          className="flex items-end gap-2 rounded-xl px-3.5 py-2.5 border shadow-sm transition-all duration-300 focus-within:border-amber-c focus-within:ring-2 focus-within:ring-amber-500/20"
          style={{
            background: 'var(--surface-1)',
            borderColor: 'var(--surface-border)',
            borderWidth: '1px',
          }}
        >
          <span className="text-amber-c font-mono text-base font-bold pb-1">{'>'}</span>
          <textarea
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Type response or question…"
            rows={1}
            className="flex-1 bg-transparent text-sm text-primary-c font-medium placeholder:text-muted-c focus:outline-none resize-none py-1.5 max-h-32 transition-colors"
          />
          <button
            onClick={handleSend}
            disabled={chatInput.trim().length === 0 || isAgentThinking}
            className="p-2.5 rounded-xl transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed border hover:scale-105 active:scale-95 shadow-sm flex items-center justify-center"
            style={{
              background: 'var(--text-primary)',
              color: 'var(--surface-0)',
              borderColor: 'var(--surface-border)',
            }}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[11px] text-muted-c mt-1.5 px-1 font-mono">
          Enter to send, Shift + Enter for new line
        </p>
      </div>
    </div>
  );
}

