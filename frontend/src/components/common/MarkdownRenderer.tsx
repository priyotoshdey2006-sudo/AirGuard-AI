import React from 'react';

interface Props {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<Props> = ({ content, className = '' }) => {
  // Normalize line endings and split by double line breaks into logical blocks
  const normalized = content.replace(/\r\n/g, '\n');
  const blocks = normalized.split(/\n\s*\n/);

  return (
    <div className={`space-y-2.5 text-xs leading-relaxed ${className}`}>
      {blocks.map((block, bIdx) => {
        const trimmed = block.trim();
        if (!trimmed) return null;

        // Heading 4: ####
        if (trimmed.startsWith('#### ')) {
          return (
            <h5 key={bIdx} className="font-bold text-slate-100 text-xs mt-2 mb-1 tracking-tight">
              {renderInline(trimmed.slice(5))}
            </h5>
          );
        }

        // Heading 3: ###
        if (trimmed.startsWith('### ')) {
          return (
            <h4 key={bIdx} className="font-bold text-emerald-300 text-xs mt-2.5 mb-1 tracking-tight">
              {renderInline(trimmed.slice(4))}
            </h4>
          );
        }

        // Heading 2 or 1: ## or #
        if (trimmed.startsWith('## ') || trimmed.startsWith('# ')) {
          return (
            <h3 key={bIdx} className="font-bold text-emerald-400 text-sm mt-3 mb-1.5 tracking-tight">
              {renderInline(trimmed.replace(/^#+\s*/, ''))}
            </h3>
          );
        }

        // Blockquotes
        if (trimmed.startsWith('> ')) {
          return (
            <blockquote
              key={bIdx}
              className="border-l-2 border-emerald-400/60 pl-3 py-1 italic text-slate-300/90 bg-emerald-500/5 rounded-r"
            >
              {renderInline(trimmed.replace(/^>\s*/, ''))}
            </blockquote>
          );
        }

        // Check if block consists of list items
        const rawLines = trimmed.split('\n').map((l) => l.trim()).filter(Boolean);
        const isBulletList = rawLines.every((l) => l.startsWith('* ') || l.startsWith('- '));
        const isNumberedList = rawLines.every((l) => /^\d+\.\s/.test(l));

        if (isBulletList) {
          return (
            <ul key={bIdx} className="space-y-1.5 my-1.5 pl-4 list-disc list-outside text-slate-200">
              {rawLines.map((line, lIdx) => (
                <li key={lIdx} className="pl-0.5 leading-relaxed">
                  {renderInline(line.replace(/^[\*\-]\s+/, ''))}
                </li>
              ))}
            </ul>
          );
        }

        if (isNumberedList) {
          return (
            <ol key={bIdx} className="space-y-1.5 my-1.5 pl-4 list-decimal list-outside text-slate-200">
              {rawLines.map((line, lIdx) => (
                <li key={lIdx} className="pl-0.5 leading-relaxed">
                  {renderInline(line.replace(/^\d+\.\s+/, ''))}
                </li>
              ))}
            </ol>
          );
        }

        // Regular paragraph with soft line breaks
        return (
          <p key={bIdx} className="text-slate-200 leading-relaxed">
            {rawLines.map((line, lIdx) => (
              <React.Fragment key={lIdx}>
                {lIdx > 0 && <br />}
                {renderInline(line)}
              </React.Fragment>
            ))}
          </p>
        );
      })}
    </div>
  );
};

// Parse inline tokens: bold (**text**), italic (*text* or _text_), code (`text`)
function renderInline(text: string): React.ReactNode {
  // Regex capturing bold (**...**), code (`...`), or italic (*...* / _..._)
  const regex = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*|_[^_]+_)/g;
  const parts = text.split(regex);

  return parts.map((part, index) => {
    if (!part) return null;

    // Bold: **text**
    if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
      return (
        <strong key={index} className="font-bold text-white tracking-wide">
          {part.slice(2, -2)}
        </strong>
      );
    }

    // Inline Code: `code`
    if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
      return (
        <code
          key={index}
          className="px-1.5 py-0.5 rounded bg-white/10 text-cyan-300 font-mono text-[11px] border border-white/10"
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    // Italic: *text* or _text_
    if (
      (part.startsWith('*') && part.endsWith('*') && part.length >= 2) ||
      (part.startsWith('_') && part.endsWith('_') && part.length >= 2)
    ) {
      return (
        <em key={index} className="italic text-slate-300">
          {part.slice(1, -1)}
        </em>
      );
    }

    // Plain text segment
    return <span key={index}>{part}</span>;
  });
}
