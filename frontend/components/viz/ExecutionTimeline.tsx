"use client";

import { useKavach } from "@/lib/store";
import { cn } from "@/lib/utils";
import { Check, Loader2, AlertTriangle, Circle } from "lucide-react";

const agentColor: Record<string, string> = {
  "Security Agent": "text-info",
  "Router Agent": "text-signal",
  "Model Router": "text-signal",
  Planner: "text-ink",
  "Document Agent": "text-info",
  "Vision Agent": "text-caution",
  "Knowledge Agent": "text-signal",
  "Reasoning Agent": "text-signal",
  "Verification Agent": "text-verified",
  "Deliverable Agent": "text-verified",
};

export function ExecutionTimeline() {
  const steps = useKavach((s) => s.steps);
  const phase = useKavach((s) => s.phase);

  return (
    <ol className="relative space-y-0">
      {/* rail */}
      <span className="absolute left-[13px] top-2 bottom-2 w-px bg-line" aria-hidden />
      {steps.map((step, i) => {
        const done = step.status === "done";
        const active = step.status === "active";
        const warn = step.status === "warn";
        return (
          <li key={step.id} className="relative flex gap-3 py-2 pl-0">
            <span
              className={cn(
                "relative z-10 grid h-7 w-7 shrink-0 place-items-center rounded-full border transition-colors",
                active && "border-signal bg-signal/15 text-signal",
                done && "border-verified/60 bg-verified/10 text-verified",
                warn && "border-caution/60 bg-caution/10 text-caution",
                !active && !done && !warn && "border-line bg-surface text-ink-faint",
              )}
            >
              {active ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : done ? (
                <Check className="h-3.5 w-3.5" />
              ) : warn ? (
                <AlertTriangle className="h-3.5 w-3.5" />
              ) : (
                <Circle className="h-2 w-2" />
              )}
            </span>
            <div
              className={cn(
                "min-w-0 flex-1 rounded-[3px] border px-3 py-2 transition-all",
                active ? "border-signal/40 bg-signal/[0.06]" : "border-transparent",
                (done || warn) && "opacity-100",
                !active && !done && !warn && phase !== "idle" && "opacity-45",
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={cn("font-mono text-2xs uppercase tracking-wider", agentColor[step.agent] || "text-ink-muted")}>
                    {step.agent}
                  </span>
                  {active && (
                    <span className="relative h-1 w-10 overflow-hidden rounded-full bg-surface-inset">
                      <span className="absolute inset-y-0 w-1/3 animate-pulseline rounded-full bg-signal" />
                    </span>
                  )}
                </div>
                <span className="font-mono text-2xs text-ink-faint">{(step.durationMs / 1000).toFixed(1)}s</span>
              </div>
              <p className="mt-0.5 text-sm text-ink">{step.label}</p>
              {(active || done || warn) && (
                <p className={cn("mt-0.5 font-mono text-2xs", warn ? "text-caution" : "text-ink-muted")}>
                  {step.detail}
                </p>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
