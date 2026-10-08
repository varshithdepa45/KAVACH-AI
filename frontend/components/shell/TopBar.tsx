"use client";

import { useRouter } from "next/navigation";
import { useKavach } from "@/lib/store";
import { StatusPill } from "@/components/ui";
import { Play, Square, WifiOff, Cpu, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

export function TopBar() {
  const router = useRouter();
  const phase = useKavach((s) => s.phase);
  const startRun = useKavach((s) => s.startRun);
  const reset = useKavach((s) => s.reset);
  const [clock, setClock] = useState("--:--:--");

  useEffect(() => {
    const tick = () =>
      setClock(
        new Date().toLocaleTimeString("en-GB", { hour12: false }) + " IST",
      );
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const running = phase === "running";

  function launchDemo() {
    if (running) {
      reset();
      return;
    }
    startRun({ demo: true });
    router.push("/workbench");
  }

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-line bg-canvas/85 px-2 backdrop-blur sm:px-3 md:px-5">
      <div className="flex min-w-0 items-center gap-2 overflow-hidden">
        <StatusPill tone="verified" pulse>
          Air-Gapped
        </StatusPill>
        <StatusPill tone="signal" className="hidden sm:inline-flex">
          <Cpu className="h-3 w-3" /> Local Inference
        </StatusPill>
        <StatusPill tone="info" className="hidden md:inline-flex">
          <Lock className="h-3 w-3" /> Data Sovereignty Active
        </StatusPill>
        <span className="ml-2 hidden items-center gap-1.5 font-mono text-2xs text-ink-faint lg:inline-flex">
          <WifiOff className="h-3 w-3 text-danger" /> egress denied
        </span>
      </div>

      <div className="flex items-center gap-4">
        <span className="hidden font-mono text-2xs text-ink-faint sm:inline">
          {clock}
        </span>
        <button
          onClick={launchDemo}
          className={cn(
            "btn",
            running ? "btn-danger" : "btn-primary",
            "shadow-glow",
          )}
        >
          {running ? (
            <>
              <Square className="h-3.5 w-3.5" /> Stop Demo
            </>
          ) : (
            <>
              <Play className="h-3.5 w-3.5" /> Start Judge Demo
            </>
          )}
        </button>
      </div>
    </header>
  );
}
