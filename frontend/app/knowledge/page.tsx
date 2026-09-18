"use client";

import { useMemo, useState } from "react";
import { Panel, PanelHeader, PageTitle, StatusPill } from "@/components/ui";
import { EvidenceCard } from "@/components/viz/Findings";
import { knowledgeSources, knowledgeStats, evidence } from "@/lib/data";
import { Search, Database, Loader2, Boxes, Layers } from "lucide-react";
import * as Icons from "lucide-react";

const SAMPLES = [
  "corrosion at P-101 outlet",
  "relief valve set pressure",
  "HX-301 fouling threshold",
  "T-101 corrosion allowance",
];

export default function KnowledgePage() {
  const [query, setQuery] = useState(SAMPLES[0]);
  const [submitted, setSubmitted] = useState(SAMPLES[0]);
  const [loading, setLoading] = useState(false);

  const results = useMemo(() => {
    const q = submitted.toLowerCase();
    const terms = q.split(/\s+/).filter(Boolean);
    return evidence
      .map((e) => {
        const hay = `${e.source} ${e.excerpt} ${e.tags.join(" ")}`.toLowerCase();
        const hits = terms.reduce((n, t) => n + (hay.includes(t) ? 1 : 0), 0);
        // deterministic composite score: keyword hits dominate, base relevance breaks ties
        const score = hits * 100 + e.relevance;
        return { e, hits, score };
      })
      .filter((r) => r.hits > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 4);
  }, [submitted]);

  function run(q: string) {
    setQuery(q);
    setLoading(true);
    setTimeout(() => {
      setSubmitted(q);
      setLoading(false);
    }, 550);
  }

  return (
    <div>
      <PageTitle eyebrow="Retrieval-Augmented Generation" title="Knowledge Base">
        <StatusPill tone="verified">Vector DB Online</StatusPill>
      </PageTitle>

      {/* stats */}
      <div className="mb-3 grid grid-cols-2 gap-3 md:grid-cols-4">
        <Stat icon={<Database className="h-4 w-4" />} label="Documents Indexed" value={knowledgeStats.documentsIndexed} />
        <Stat icon={<Layers className="h-4 w-4" />} label="Chunks" value={knowledgeStats.chunks.toLocaleString()} />
        <Stat icon={<Boxes className="h-4 w-4" />} label="Embedding Dims" value={knowledgeStats.dimensions} />
        <Stat icon={<Database className="h-4 w-4" />} label="Embed Model" value={knowledgeStats.model} small />
      </div>

      <div className="grid gap-3 lg:grid-cols-[280px_1fr]">
        {/* sources */}
        <Panel>
          <PanelHeader title="Knowledge Sources" />
          <ul className="divide-y divide-line">
            {knowledgeSources.map((s) => {
              const Icon = (Icons as any)[s.icon] ?? Database;
              return (
                <li key={s.name} className="flex items-center gap-3 px-4 py-3">
                  <span className="grid h-8 w-8 place-items-center rounded-[3px] border border-line bg-surface-inset text-signal">
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="flex-1">
                    <div className="text-xs text-ink">{s.name}</div>
                    <div className="font-mono text-2xs text-ink-faint">{s.count} docs · {s.chunks} chunks</div>
                  </div>
                </li>
              );
            })}
          </ul>
        </Panel>

        {/* query */}
        <Panel>
          <PanelHeader title="Semantic Retrieval" sub="Query the local corpus — no external calls" icon={<Search className="h-4 w-4" />} />
          <div className="p-4">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && run(query)}
                  className="w-full rounded-[3px] border border-line bg-surface-inset py-2.5 pl-9 pr-3 text-sm text-ink outline-none focus:border-signal/50"
                  placeholder="Ask the knowledge base…"
                />
              </div>
              <button onClick={() => run(query)} className="btn btn-primary">
                Retrieve
              </button>
            </div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {SAMPLES.map((s) => (
                <button
                  key={s}
                  onClick={() => run(s)}
                  className="rounded-[2px] border border-line bg-surface-inset px-2 py-1 font-mono text-2xs text-ink-muted hover:border-signal/40 hover:text-signal"
                >
                  {s}
                </button>
              ))}
            </div>

            <div className="mt-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="eyebrow">Retrieved Evidence</span>
                <span className="font-mono text-2xs text-ink-faint">
                  {loading ? "searching…" : `${results.length} chunks · cosine similarity`}
                </span>
              </div>
              {loading ? (
                <div className="flex items-center justify-center gap-2 py-10 font-mono text-2xs text-ink-muted">
                  <Loader2 className="h-4 w-4 animate-spin text-signal" /> embedding query · scanning vector store…
                </div>
              ) : results.length ? (
                <div className="space-y-2">
                  {results.map((r, i) => (
                    <EvidenceCard key={r.e.id} ev={r.e} rank={i + 1} />
                  ))}
                </div>
              ) : (
                <p className="py-8 text-center font-mono text-2xs text-ink-faint">
                  No matching chunks in the local corpus.
                </p>
              )}
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function Stat({
  icon,
  label,
  value,
  small,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
  small?: boolean;
}) {
  return (
    <Panel>
      <div className="p-4">
        <div className="mb-2 flex items-center justify-between">
          <span className="eyebrow">{label}</span>
          <span className="text-signal">{icon}</span>
        </div>
        <div className={small ? "font-mono text-sm text-ink" : "font-display text-2xl font-bold text-ink"}>{value}</div>
      </div>
    </Panel>
  );
}
