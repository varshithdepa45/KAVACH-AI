import Link from "next/link";
import { Panel, PanelHeader, PageTitle, StatusPill, Meter } from "@/components/ui";
import { BoundaryDiagram } from "@/components/viz/BoundaryDiagram";
import { ArchitectureFlow } from "@/components/viz/ArchitectureFlow";
import { TasksTrendChart, ModelUsageChart } from "@/components/viz/Charts";
import { overviewMetrics, runs, FACILITY, UNIT } from "@/lib/data";
import {
  FileStack,
  Cpu,
  ShieldOff,
  BadgeCheck,
  Zap,
  ArrowUpRight,
  Activity,
} from "lucide-react";

export default function OverviewPage() {
  return (
    <div>
      <PageTitle eyebrow={`${FACILITY} · ${UNIT}`} title="Operations Overview">
        <div className="flex items-center gap-2">
          <StatusPill tone="verified" pulse>
            All Systems Nominal
          </StatusPill>
        </div>
      </PageTitle>

      {/* Metric row */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <Metric icon={<FileStack className="h-4 w-4" />} label="Documents Processed" value={overviewMetrics.documentsProcessed} tone="signal" />
        <Metric icon={<Zap className="h-4 w-4" />} label="AI Tasks Executed" value={overviewMetrics.tasksExecuted} tone="signal" />
        <Metric icon={<Cpu className="h-4 w-4" />} label="Local Inference" value={overviewMetrics.localInference} tone="verified" />
        <Metric icon={<ShieldOff className="h-4 w-4" />} label="External Data Transfers" value={overviewMetrics.externalTransfers} tone="danger" emphasize />
        <Metric icon={<BadgeCheck className="h-4 w-4" />} label="Verification Rate" value={`${overviewMetrics.verificationRate}%`} tone="verified" />
      </div>

      <div className="mt-3 grid gap-3 lg:grid-cols-3">
        {/* Boundary diagram — signature */}
        <Panel className="lg:col-span-2">
          <PanelHeader
            title="Data Boundary"
            sub="Every byte of processing is contained on-premise"
            right={<StatusPill tone="danger" dot={false}>Cloud Egress Blocked</StatusPill>}
          />
          <div className="p-4">
            <BoundaryDiagram />
            <div className="mt-3 flex items-center justify-center gap-2 rounded-[3px] border border-signal/25 bg-signal/[0.06] py-2.5">
              <ShieldOff className="h-4 w-4 text-signal" />
              <span className="font-mono text-xs uppercase tracking-[0.15em] text-signal">
                Data never leaves this environment
              </span>
            </div>
          </div>
        </Panel>

        {/* Architecture flow */}
        <Panel>
          <PanelHeader title="Processing Pipeline" sub="Request → deliverable, fully local" />
          <div className="p-4">
            <ArchitectureFlow />
          </div>
        </Panel>
      </div>

      <div className="mt-3 grid gap-3 lg:grid-cols-3">
        <Panel>
          <PanelHeader title="Task Throughput" sub="Local inference · last 7 days" />
          <div className="p-4">
            <TasksTrendChart />
          </div>
        </Panel>
        <Panel>
          <PanelHeader title="Model Utilisation" sub="Runs routed per local model" />
          <div className="p-4">
            <ModelUsageChart />
          </div>
        </Panel>
        <Panel>
          <PanelHeader
            title="Recent Runs"
            icon={<Activity className="h-4 w-4" />}
            right={
              <Link href="/runs" className="font-mono text-2xs text-signal hover:text-signal-glow">
                view all →
              </Link>
            }
          />
          <ul className="divide-y divide-line">
            {runs.slice(0, 4).map((r) => (
              <li key={r.id}>
                <Link href={`/runs/${r.id}`} className="flex items-center gap-3 px-4 py-2.5 hover:bg-surface-raised">
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs text-ink">{r.task}</div>
                    <div className="font-mono text-2xs text-ink-faint">{r.id} · {r.model}</div>
                  </div>
                  <RunBadge status={r.status} />
                  <ArrowUpRight className="h-3.5 w-3.5 text-ink-faint" />
                </Link>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
  tone,
  emphasize,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
  tone: "signal" | "verified" | "danger";
  emphasize?: boolean;
}) {
  const toneText =
    tone === "verified" ? "text-verified" : tone === "danger" ? "text-danger" : "text-signal";
  return (
    <Panel className={emphasize ? "relative overflow-hidden" : ""}>
      {emphasize && (
        <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-danger to-transparent" />
      )}
      <div className="p-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="eyebrow">{label}</span>
          <span className={toneText}>{icon}</span>
        </div>
        <div className={`font-display text-3xl font-bold tracking-tight ${emphasize ? "text-danger" : "text-ink"}`}>
          {value}
        </div>
        {emphasize && (
          <div className="mt-1 font-mono text-2xs uppercase tracking-widest text-danger/80">
            zero · guaranteed
          </div>
        )}
      </div>
    </Panel>
  );
}

function RunBadge({ status }: { status: string }) {
  const map: Record<string, "verified" | "signal" | "caution" | "muted"> = {
    COMPLETED: "verified",
    RUNNING: "signal",
    REVIEW: "caution",
    QUEUED: "muted",
    FAILED: "muted",
  };
  return (
    <StatusPill tone={map[status] || "muted"} dot={false} className="hidden sm:inline-flex">
      {status}
    </StatusPill>
  );
}
