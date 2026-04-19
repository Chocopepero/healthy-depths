import { useChat } from "./hooks/useChat";
import ChatInterface from "./components/ChatInterface";
import ClinicalSummary from "./components/ClinicalSummary";
import TriageBadge from "./components/TriageBadge";
import MedInteractionCard from "./components/MedInteractionCard";
import ClinicCard from "./components/ClinicCard";

function StagePill({ stage }) {
  const labels = {
    INTAKE: "Intake",
    SUMMARY: "Summary",
    TRIAGE: "Triage",
    GUIDANCE: "Guidance",
    COMPLETE: "Complete",
  };
  const order = ["INTAKE", "SUMMARY", "TRIAGE", "GUIDANCE", "COMPLETE"];
  const currentIdx = order.indexOf(stage);

  return (
    <div className="flex items-center gap-1.5">
      {order.map((s, i) => (
        <div key={s} className="flex items-center gap-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${
              i <= currentIdx
                ? "bg-cyan-bio w-6"
                : "bg-slate-700 w-3"
            }`}
          />
          {i === currentIdx && (
            <span className="font-mono text-xs text-cyan-bio/70 hidden sm:inline">
              {labels[s]}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const {
    history,
    isLoading,
    error,
    stage,
    clinicalSummary,
    triage,
    drugInteractions,
    clinics,
    send,
    reset,
  } = useChat();

  const hasSidebar = clinicalSummary || triage || drugInteractions || clinics;

  return (
    <div className="depth-bg min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-cyan-bio/10 bg-navy-950/80 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-8 h-8 rounded-lg bg-teal-ocean/30 border border-cyan-bio/30 flex items-center justify-center">
                <span className="font-display text-cyan-bio text-sm font-bold">D</span>
              </div>
              <div className="absolute inset-0 rounded-lg border border-cyan-bio/20 animate-ping opacity-40" />
            </div>
            <div>
              <h1 className="font-display text-lg text-slate-100 leading-none">Depth</h1>
              <p className="font-mono text-xs text-slate-500 leading-none mt-0.5">
                Navigate what's beneath the surface
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <StagePill stage={stage} />
            {history.length > 0 && (
              <button
                onClick={reset}
                className="font-mono text-xs text-slate-500 hover:text-slate-300 transition-colors border border-slate-700/50 hover:border-slate-600 px-3 py-1.5 rounded-lg"
              >
                New session
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-4 flex gap-4">
        {/* Chat column */}
        <div
          className={`depth-card flex flex-col transition-all duration-500 ${
            hasSidebar ? "w-full lg:w-[480px] shrink-0" : "w-full max-w-2xl mx-auto"
          }`}
          style={{ height: "calc(100vh - 120px)" }}
        >
          <ChatInterface
            history={history}
            isLoading={isLoading}
            error={error}
            onSend={send}
          />
        </div>

        {/* Sidebar — surfaces as data arrives */}
        {hasSidebar && (
          <div className="flex-1 min-w-0 space-y-4 overflow-y-auto pb-4">
            {triage && <TriageBadge triage={triage} />}
            {clinicalSummary && <ClinicalSummary summary={clinicalSummary} />}
            {drugInteractions && drugInteractions.length > 0 && (
              <MedInteractionCard interactions={drugInteractions} />
            )}
            {clinics && clinics.length > 0 && (
              <div className="animate-surface-up rounded-2xl border border-cyan-bio/15 bg-navy-800 overflow-hidden">
                <div className="flex items-center gap-2 px-5 py-3 border-b border-cyan-bio/10 bg-navy-900/60">
                  <span className="text-base">🏥</span>
                  <span className="font-mono text-xs tracking-widest uppercase text-cyan-bio/70">
                    Nearby Free & Low-Cost Clinics
                  </span>
                </div>
                <div className="p-4 space-y-3">
                  {clinics.map((clinic, i) => (
                    <ClinicCard key={i} clinic={clinic} index={i} />
                  ))}
                </div>
                <div className="px-5 py-3 border-t border-cyan-bio/10 bg-navy-900/40">
                  <span className="font-mono text-xs text-slate-500">
                    Source: HRSA Federally Qualified Health Centers · Sliding scale fees
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-cyan-bio/5 py-3">
        <p className="text-center font-mono text-xs text-slate-600">
          Depth does not diagnose or prescribe. It prepares patients and informs decisions. Always consult a licensed medical professional.
        </p>
      </footer>
    </div>
  );
}
