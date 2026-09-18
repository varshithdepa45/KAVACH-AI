import Link from "next/link";
import { notFound } from "next/navigation";
import { Panel, PanelHeader, StatusPill, KeyVal } from "@/components/ui";
import { FindingCard } from "@/components/viz/Findings";
import { runs, getFinding, primaryRunSteps } from "@/lib/data";
import { ArrowLeft, Check, FileOutput, Clock } from "lucide-react";

export function generateStaticParams() {
  return runs.map((r) => ({ id: r.id }));
}

export default function RunDetail({ params }: { params: { id: string } }) {
  const run = runs.find((r) => r.id === params.id);
  if (!run) notFound();

  const steps = run.steps.length ? run.steps : primaryRunSteps.map((s) => ({ ...s, status: "done" as const }));
  const findings = run.findingIds.map(getFinding).filter(Boolean);

  const statusTone =
    run.status === "COMPLETED" ? "verified" : run.status === "REVIEW" ? "caution" : "signal";

  return (
    <div>
      <div className="mb-5">
        <Link href="/runs" className="mb-3 inline-flex items-center gap-1.5 font-mono text-2xs text-ink-muted hover:text-signal">
          <ArrowLeft className="h-3.5 w-3.5" /> Agent Runs
        </Link>
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="eyebrow mb-1">{run.id}</p>
            <h1 className="font-display text-2xl font-semibold text-ink">{run.task}</h1>
          </div>
          <StatusPill tone={statusTone as any}>{run.status}</StatusPill>
        </div>
      </div>

      <div className="grid gap-3 lg:grid-cols-[300px_1fr]">
        {/* meta */}
        <div className="space-y-3">
          <Panel>
            <PanelHeader title="Run Metadata" icon={<Clock className="h-4 w-4" />} />
            <div className="px-4 py-3">
              <KeyVal k="Agent" v={run.agent} />
              <KeyVal k="Model" v={run.model} />
              <KeyVal k="Start" v={run.startTime} />
              <KeyVal k="Duration" v={`${(run.durationMs / 1000).toFixed(1)}s`} />
              <KeyVal k="Verification" v={`${run.verification}%`} />
              <KeyVal k="Evidence-backed" v={run.evidenceBacked} />
              <KeyVal k="Needs review" v={run.needsReview} />
            </div>
          </Panel>
          {run.deliverableId && (
            <Panel>
              <div className="p-4">
                <Link href="/deliverables" className="btn btn-primary w-full">
                  <FileOutput className="h-3.5 w-3.5" /> View Deliverable
                </Link>
              </div>
            </Panel>
          )}
        </div>

        {/* trace */}
        <div className="space-y-3">
          <Panel>
            <PanelHeader title="Execution Trace" sub={`${steps.length} steps`} />
            <div className="p-4">
              <ol className="relative space-y-0">
                <span className="absolute left-[13px] top-2 bottom-2 w-px bg-line" aria-hidden />
                {steps.map((s) => (
                  <li key={s.id} className="relative flex gap-3 py-1.5">
                    <span className="relative z-10 grid h-7 w-7 shrink-0 place-items-center rounded-full border border-verified/60 bg-verified/10 text-verified">
                      <Check className="h-3.5 w-3.5" />
                    </span>
                    <div className="flex-1 rounded-[3px] border border-transparent px-3 py-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-2xs uppercase tracking-wider text-signal">{s.agent}</span>
                        <span className="font-mono text-2xs text-ink-faint">{(s.durationMs / 1000).toFixed(1)}s</span>
                      </div>
                      <p className="text-sm text-ink">{s.label}</p>
                      <p className="font-mono text-2xs text-ink-muted">{s.detail}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          </Panel>

          {findings.length > 0 && (
            <Panel>
              <PanelHeader title="Findings" sub={`${findings.length} findings · evidence-backed`} />
              <div className="space-y-2.5 p-4">
                {findings.map((f) => (
                  <FindingCard key={f!.id} finding={f!} />
                ))}
              </div>
            </Panel>
          )}
        </div>
      </div>
    </div>
  );
}
