export default function ClinicCard({ clinic, index }) {
  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    clinic.address
  )}`;

  return (
    <div
      className="animate-surface-up rounded-xl border border-cyan-bio/15 bg-navy-800 p-4"
      style={{ animationDelay: `${index * 120}ms` }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-slate-100 text-sm leading-snug mb-1 truncate">
            {clinic.name}
          </p>
          <p className="text-slate-400 text-xs leading-relaxed">{clinic.address}</p>
          {clinic.phone && (
            <a
              href={`tel:${clinic.phone}`}
              className="text-cyan-bio/70 text-xs hover:text-cyan-bio transition-colors mt-1 inline-block"
            >
              {clinic.phone}
            </a>
          )}
        </div>
        {clinic.distance != null && (
          <span className="shrink-0 font-mono text-xs text-cyan-bio/60 mt-0.5">
            {clinic.distance.toFixed(1)} mi
          </span>
        )}
      </div>

      <div className="flex gap-2 mt-3">
        <a
          href={mapsUrl}
          target="_blank"
          rel="noreferrer"
          className="flex-1 text-center text-xs font-medium py-1.5 rounded-lg bg-teal-ocean/30 hover:bg-teal-ocean/50 text-cyan-bio/80 hover:text-cyan-bio transition-colors border border-cyan-bio/10"
        >
          Get Directions
        </a>
        {clinic.website && (
          <a
            href={clinic.website}
            target="_blank"
            rel="noreferrer"
            className="flex-1 text-center text-xs font-medium py-1.5 rounded-lg bg-navy-700 hover:bg-navy-600 text-slate-300 hover:text-slate-100 transition-colors border border-slate-700/50"
          >
            Website
          </a>
        )}
      </div>
    </div>
  );
}
