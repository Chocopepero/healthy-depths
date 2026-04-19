export default function MedInteractionCard({ interactions }) {
  if (!interactions || interactions.length === 0) return null;

  const severityColor = {
    HIGH: "text-red-400 border-red-500/30 bg-red-950/30",
    MEDIUM: "text-yellow-400 border-yellow-500/30 bg-yellow-950/30",
    LOW: "text-blue-400 border-blue-500/30 bg-blue-950/30",
  };

  return (
    <div className="animate-surface-up rounded-2xl border border-yellow-500/20 bg-navy-800 overflow-hidden">
      <div className="flex items-center gap-2 px-5 py-3 border-b border-yellow-500/10 bg-navy-900/60">
        <span className="text-base">⚠️</span>
        <span className="font-mono text-xs tracking-widest uppercase text-yellow-400/80">
          Medication Flags
        </span>
      </div>

      <div className="p-4 space-y-3">
        {interactions.map((item, i) => (
          <div
            key={i}
            className={`rounded-xl border px-4 py-3 text-sm ${
              severityColor[item.severity] ?? severityColor.MEDIUM
            }`}
          >
            <div className="font-semibold mb-1 capitalize">{item.drug}</div>
            <div className="text-slate-300 text-xs leading-relaxed">{item.warning}</div>
          </div>
        ))}
      </div>

      <div className="px-5 py-3 border-t border-yellow-500/10 bg-navy-900/40">
        <span className="font-mono text-xs text-slate-500">
          Source: OpenFDA adverse event database
        </span>
      </div>
    </div>
  );
}
