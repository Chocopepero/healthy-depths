export default function MedInteractionCard({ summary, sources }) {
  if (!summary) return null;

  return (
    <div className="animate-surface-up rounded-2xl border border-yellow-500/20 bg-navy-800 overflow-hidden">
      <div className="flex items-center gap-2 px-5 py-3 border-b border-yellow-500/10 bg-navy-900/60">
        <span className="text-base">⚠️</span>
        <span className="font-mono text-xs tracking-widest uppercase text-yellow-400/80">
          Medication Flags
        </span>
      </div>

      <div className="px-5 py-4 text-sm text-slate-300 leading-relaxed">
        {summary}
      </div>

      <div className="px-5 py-3 border-t border-yellow-500/10 bg-navy-900/40 space-y-1.5">
        {sources && sources.length > 0 ? (
          <>
            <p className="font-mono text-xs text-slate-500">Learn more:</p>
            {sources.map((s, i) => (
              <a
                key={i}
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block font-mono text-xs text-cyan-bio/70 hover:text-cyan-bio truncate transition-colors"
              >
                {s.title}
              </a>
            ))}
          </>
        ) : (
          <span className="font-mono text-xs text-slate-500">Source: OpenFDA adverse event database</span>
        )}
      </div>
    </div>
  );
}
