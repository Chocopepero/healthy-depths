export default function TriageBadge({ triage }) {
  if (!triage) return null;

  const config = {
    URGENT: {
      emoji: "🔴",
      label: "URGENT — Seek emergency care now",
      border: "border-red-500/40",
      bg: "bg-red-950/40",
      text: "text-red-300",
      glow: "shadow-[0_0_24px_rgba(239,68,68,0.2)]",
    },
    SOON: {
      emoji: "🟡",
      label: "SOON — Schedule care within 1–3 days",
      border: "border-yellow-500/40",
      bg: "bg-yellow-950/40",
      text: "text-yellow-300",
      glow: "shadow-[0_0_24px_rgba(234,179,8,0.15)]",
    },
    HOME: {
      emoji: "🟢",
      label: "HOME — Manageable at home",
      border: "border-emerald-500/40",
      bg: "bg-emerald-950/40",
      text: "text-emerald-300",
      glow: "shadow-[0_0_24px_rgba(16,185,129,0.15)]",
    },
  };

  const c = config[triage.level] ?? config.SOON;

  return (
    <div className={`animate-surface-up rounded-2xl border p-5 ${c.border} ${c.bg} ${c.glow}`}>
      <div className="flex items-center gap-3 mb-3">
        <span className="text-2xl">{c.emoji}</span>
        <span className={`font-mono text-sm font-semibold tracking-widest uppercase ${c.text}`}>
          {c.label}
        </span>
      </div>
      <p className="text-slate-300 text-sm leading-relaxed">{triage.explanation}</p>
    </div>
  );
}
