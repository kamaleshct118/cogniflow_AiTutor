import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';
import { useSyntapseStore } from '@/store/useSyntapseStore';

function renderMarkdown(content: string) {
  const html = content
    .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
      return `<pre><code class="language-${lang || 'text'}">${code.replace(/</g, '&lt;')}</code></pre>`;
    })
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/_([^_]+)_/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
  return html;
}

export default function LessonCanvas() {
  const messages = useSyntapseStore((s) => s.messages);
  const topicName = useSyntapseStore((s) => s.topicName);

  const aiMessages = useMemo(
    () => messages.filter((m) => m.role === 'ai'),
    [messages],
  );

  const latestLesson = aiMessages[aiMessages.length - 1];

  return (
    <div
      className="h-full flex flex-col"
      style={{ background: 'var(--surface-1)' }}
    >
      <div
        className="border-b px-5 py-3 flex items-center gap-2"
        style={{ borderColor: 'var(--surface-border)' }}
      >
        <BookOpen className="w-4 h-4 text-amber-c" />
        <span className="text-sm font-semibold text-primary-c font-serif">
          Lesson Canvas
        </span>
        <span className="ml-auto text-xs text-secondary-c font-mono font-medium">
          {topicName}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto chat-scroll px-6 py-6">
        {!latestLesson && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div
              className="w-14 h-14 rounded-2xl border flex items-center justify-center mb-4 shadow-sm"
              style={{
                background: 'var(--surface-1)',
                borderColor: 'var(--surface-border)',
                borderWidth: '1px',
              }}
            >
              <BookOpen className="w-7 h-7 text-amber-c" />
            </div>
            <p className="text-primary-c font-serif font-medium text-sm max-w-sm leading-relaxed">
              Your lesson will appear here. Ask a question in the chat terminal
              to generate your first Socratic lesson.
            </p>
          </div>
        )}

        {latestLesson && (
          <motion.div
            key={latestLesson.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="editorial-prose max-w-none text-primary-c"
            dangerouslySetInnerHTML={{
              __html: renderMarkdown(latestLesson.content),
            }}
          />
        )}
      </div>
    </div>
  );
}

