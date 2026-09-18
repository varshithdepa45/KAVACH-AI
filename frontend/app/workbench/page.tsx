"use client";

import { useState } from "react";
import { Panel, PanelHeader, PageTitle, StatusPill, Tag } from "@/components/ui";
import { ExecutionTimeline } from "@/components/viz/ExecutionTimeline";
import { FindingCard } from "@/components/viz/Findings";
import { ReportView } from "@/components/viz/ReportView";
import { PidViewer } from "@/components/viz/PidViewer";
import { useKavach } from "@/lib/store";
import { documents, findings, DEMO_TASK, formatBytes } from "@/lib/data";
import {
  Play,
  RotateCcw,
  FileText,
  Cpu,
  ListChecks,
  Terminal,
  ShieldCheck,
  FileOutput,
  Lock,
} from "lucide-react";
import { cn } from "@/lib/utils";

const PLAN = [
  "Parse inspection report (OCR + layout)",
  "Analyze P&ID regions (vision model)",
  "Retrieve equipment information (RAG)",
  "Cross-reference findings with manual & calcs",
  "Verify each finding against source evidence",
  "Generate engineering review report",
];

export default function WorkbenchPage() {
  const [task, setTask] = useState(DEMO_TASK);
  const [tab, setTab] = useState<"pipeline" | "pid">("pipeline");
  const phase = useKavach((s) => s.phase);
  const startRun = useKavach((s) => s.startRun);
  const reset = useKavach((s) => s.reset);
  const progress = useKavach((s) => s.progress);
  const logLines = useKavach((s) => s.logLines);
  const showReport = useKavach((s) => s.showReport);
  const openReport = useKavach((s) => s.openReport);
  const closeReport = useKavach((s) => s.closeReport);

  const started = phase !== "idle";
  const finished = phase === "review" || phase === "complete";
  const needsReview = findings.filter((f) => !f.verified || f.reviewState === "needs-review");

  return (
    <div>
      <PageTitle eyebrow="Agentic Workspace" title="Workbench">
        <StatusPill tone={finished ? "verified" : phase === "running" ? "signal" : "muted"} pulse={phase === "running"}>
          {phase === "idle" ? "Ready" : phase === "running" ? `Executing · ${progress}%` : "Awaiting Review"}
        </StatusPill>
      </PageTitle>

      <div className="grid gap-3 lg:grid-cols-[300px_1fr]">
        {/* PROJECT CONTEXT */}
        <div className="space-y-3">
          <Panel>
            <PanelHeader title="Project Context" sub="Unit 4 Inspection" icon={<FileText className="h-4 w-4" />} />
            <ul className="divide-y divide-line">
              {documents.map((d) => (
                <li key={d.id} className="px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-2xs text-ink-faint">{d.type}</span>
                    <span className="flex-1 truncate text-xs text-ink">{d.name}</span>
                  </div>
                  <div className="mt-1.5 flex items-center justify-between">
                    <StatusPill
                      tone={d.classification === "CONFIDENTIAL" || d.classification === "RESTRICTED" ? "danger" : "info"}
                      dot={false}
                    >
                      {d.classification}
                    </StatusPill>
                    <span className="font-mono text-2xs text-ink-faint">{formatBytes(d.sizeBytes)}</span>
                  </div>
                  <div className="mt-1.5 flex items-center gap-2 font-mono text-2xs text-verified">
                    <span>OCR ✓</span>
                    <span>EMB ✓</span>
                    <span>IDX ✓</span>
                  </div>
                </li>
              ))}
            </ul>
            <div className="flex items-center gap-1.5 border-t border-line px-3 py-2 font-mono text-2xs text-ink-muted">
              <Lock className="h-3 w-3 text-signal" /> local only · no external upload
            </div>
          </Panel>
        </div>

        {/* MAIN */}
        <div className="space-y-3">
          {/* Tab bar */}
          <div className="flex items-center gap-1 border-b border-line">
            {([
              ["pipeline", "Agent Pipeline"],
              ["pid", "P&ID Analysis"],
            ] as const).map(([key, label]) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={cn(
                  "-mb-px border-b-2 px-3 py-2 font-mono text-2xs uppercase tracking-[0.08em] transition-colors",
                  tab === key
                    ? "border-signal text-signal"
                    : "border-transparent text-ink-muted hover:text-ink",
                )}
              >
                {label}
              </button>
            ))}
          </div>

          {tab === "pid" ? (
            <>
              <Panel>
                <PanelHeader
                  title="Multimodal P&ID Analysis"
                  sub="Vision model · region detection linked to corpus evidence"
                  icon={<FileText className="h-4 w-4" />}
                />
                <div className="p-4">
                  <PidViewer />
                </div>
              </Panel>
            </>
          ) : (
          <>
          {/* Task input */}
          <Panel>
            <PanelHeader title="What would you like KAVACH to do?" sub="Natural-language task · routed to local agents" />
            <div className="p-4">
              <textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                rows={3}
                className="w-full resize-none rounded-[3px] border border-line bg-surface-inset px-3 py-2.5 text-sm text-ink outline-none placeholder:text-ink-faint focus:border-signal/50"
                placeholder="e.g. Review the inspection report against the P&ID and generate an engineering review report."
              />
              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {documents.slice(0, 3).map((d) => (
                    <span key={d.id} className="font-mono text-2xs text-ink-faint">
                      + {d.name}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  {started && (
                    <button onClick={reset} className="btn btn-ghost">
                      <RotateCcw className="h-3.5 w-3.5" /> Reset
                    </button>
                  )}
                  <button
                    onClick={() => startRun()}
                    disabled={phase === "running"}
                    className="btn btn-primary shadow-glow"
                  >
                    <Play className="h-3.5 w-3.5" /> Run KAVACH
                  </button>
                </div>
              </div>
            </div>
          </Panel>

          {!started && (
            <Panel className="grid-bg">
              <div className="flex flex-col items-center justify-center gap-2 px-6 py-14 text-center">
                <ShieldCheck className="h-8 w-8 text-signal/60" />
                <p className="font-display text-sm text-ink">Agent pipeline idle</p>
                <p className="max-w-md text-xs text-ink-muted">
                  Press <span className="font-mono text-signal">Run KAVACH</span> to route this task through the security,
                  classification, planning, analysis, retrieval, reasoning, verification and deliverable agents — all
                  locally.
                </p>
              </div>
            </Panel>
          )}

          {started && (
            <>
              {/* Classification + routing + plan */}
              <div className="grid gap-3 md:grid-cols-3">
                <StepCard step="01" title="Task Classification" icon={<ListChecks className="h-4 w-4" />}>
                  <div className="text-sm text-ink">Industrial Document Analysis</div>
                  <div className="mt-1 font-mono text-2xs text-ink-muted">multimodal · confidential</div>
                </StepCard>
                <StepCard step="02" title="Model Routing" icon={<Cpu className="h-4 w-4" />}>
                  <div className="flex flex-wrap gap-1">
                    <Tag>Qwen2-VL-7B</Tag>
                    <Tag>Qwen3-4B</Tag>
                  </div>
                  <div className="mt-1.5 font-mono text-2xs text-ink-muted">vision + reasoning selected</div>
                </StepCard>
                <StepCard step="03" title="Execution Plan" icon={<ListChecks className="h-4 w-4" />}>
                  <ol className="space-y-0.5">
                    {PLAN.map((p, i) => (
                      <li key={i} className="flex gap-1.5 text-2xs text-ink-muted">
                        <span className="font-mono text-signal">{i + 1}.</span>
                        {p}
                      </li>
                    ))}
                  </ol>
                </StepCard>
              </div>

              {/* Execution + console */}
              <div className="grid gap-3 lg:grid-cols-[1fr_360px]">
                <Panel>
                  <PanelHeader
                    title="Agent Execution"
                    sub="Live pipeline trace"
                    right={
                      <span className="font-mono text-2xs text-ink-faint">
                        {progress}% · {phase === "running" ? "running" : "complete"}
                      </span>
                    }
                  />
                  <div className="p-4">
                    <ExecutionTimeline />
                  </div>
                </Panel>
                <Panel className="flex flex-col">
                  <PanelHeader title="Local Inference Console" icon={<Terminal className="h-4 w-4" />} />
                  <div className="flex-1 overflow-y-auto p-3">
                    <pre className="whitespace-pre-wrap font-mono text-2xs leading-relaxed text-ink-muted">
                      {logLines.join("\n")}
                      {phase === "running" && <span className="animate-blip text-signal">▊</span>}
                    </pre>
                  </div>
                </Panel>
              </div>

              {/* Verification + findings */}
              {finished && (
                <>
                  <Panel className="animate-fadein">
                    <PanelHeader
                      title="Verification"
                      sub="Evidence cross-check by the Verification Agent"
                      right={<StatusPill tone="verified">Verified 94%</StatusPill>}
                    />
                    <div className="grid gap-3 p-4 sm:grid-cols-4">
                      <VStat label="Verification Score" value="94%" tone="text-verified" />
                      <VStat label="Evidence-Backed" value="8 / 9" tone="text-signal" />
                      <VStat label="Needs Human Review" value="1" tone="text-caution" />
                      <div className="flex items-center">
                        <button onClick={openReport} className="btn btn-primary w-full shadow-glow">
                          <FileOutput className="h-3.5 w-3.5" /> Open Engineering Review
                        </button>
                      </div>
                    </div>
                  </Panel>

                  <Panel className="animate-fadein">
                    <PanelHeader
                      title="Human Review Required"
                      sub="AI recommends · Engineer approves"
                      right={<StatusPill tone="caution" dot={false}>{needsReview.length} pending</StatusPill>}
                    />
                    <div className="space-y-2.5 p-4">
                      {needsReview.map((f) => (
                        <FindingCard key={f.id} finding={f} showReview />
                      ))}
                    </div>
                  </Panel>
                </>
              )}
            </>
          )}
          </>
          )}
        </div>
      </div>

      {/* Report modal */}
      {showReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-canvas/80 p-4 backdrop-blur-sm" onClick={closeReport}>
          <div
            className="panel-raised h-[88vh] w-full max-w-4xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <ReportView onClose={closeReport} />
          </div>
        </div>
      )}
    </div>
  );
}

function StepCard({
  step,
  title,
  icon,
  children,
}: {
  step: string;
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Panel className="animate-fadein">
      <div className="flex items-center gap-2 border-b border-line px-3 py-2">
        <span className="font-mono text-2xs text-signal">{step}</span>
        <span className="text-signal">{icon}</span>
        <span className="font-display text-xs font-semibold uppercase tracking-wide text-ink">{title}</span>
      </div>
      <div className="p-3">{children}</div>
    </Panel>
  );
}

function VStat({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className="rounded-[3px] border border-line bg-surface-inset p-3">
      <div className="eyebrow mb-1">{label}</div>
      <div className={cn("font-display text-2xl font-bold", tone)}>{value}</div>
    </div>
  );
}
