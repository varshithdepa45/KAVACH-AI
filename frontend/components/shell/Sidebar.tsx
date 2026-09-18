"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { nav } from "./nav";
import { cn } from "@/lib/utils";
import { systemStatus } from "@/lib/data";
import { ShieldHalf } from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-[236px] flex-col border-r border-line bg-surface/80 backdrop-blur">
      {/* Brand */}
      <div className="flex items-center gap-3 border-b border-line px-4 py-4">
        <div className="relative grid h-9 w-9 place-items-center rounded-[3px] border border-signal/40 bg-signal/10">
          <ShieldHalf className="h-5 w-5 text-signal" />
          <span className="absolute -right-1 -top-1 h-2 w-2 animate-blip rounded-full bg-signal shadow-glow" />
        </div>
        <div className="leading-tight">
          <div className="font-display text-base font-bold tracking-wide text-ink">
            KAVACH<span className="text-signal"> AI</span>
          </div>
          <div className="font-mono text-2xs uppercase tracking-[0.16em] text-ink-faint">
            Sovereign Workbench
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 py-3">
        <p className="eyebrow px-2 pb-2">Console</p>
        <ul className="space-y-0.5">
          {nav.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "group flex items-center gap-3 rounded-[3px] border border-transparent px-2.5 py-2 transition-colors",
                    active
                      ? "border-signal/30 bg-signal/10 text-ink"
                      : "text-ink-muted hover:bg-surface-raised hover:text-ink",
                  )}
                >
                  <Icon className={cn("h-4 w-4", active ? "text-signal" : "text-ink-faint group-hover:text-ink-muted")} />
                  <span className="flex-1 text-sm">{item.label}</span>
                  <span
                    className={cn(
                      "font-mono text-2xs",
                      active ? "text-signal" : "text-ink-faint/60",
                    )}
                  >
                    {item.code}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Live system rail */}
      <div className="border-t border-line px-3 py-3">
        <div className="mb-2 flex items-center justify-between">
          <span className="eyebrow">Appliance</span>
          <span className="pill border-signal/40 bg-signal/10 text-signal">
            <span className="led animate-blip bg-signal" />
            LIVE
          </span>
        </div>
        <div className="mb-2">
          <div className="mb-1 flex items-center justify-between font-mono text-2xs text-ink-muted">
            <span>LOCAL GPU</span>
            <span className="text-ink">{systemStatus.gpu}%</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-inset">
            <div className="h-full rounded-full bg-signal" style={{ width: `${systemStatus.gpu}%` }} />
          </div>
          <div className="mt-1 font-mono text-2xs text-ink-faint">
            VRAM {systemStatus.vramUsed} / {systemStatus.vramTotal} GB
          </div>
        </div>
        <ul className="grid grid-cols-2 gap-1">
          {systemStatus.services.slice(0, 8).map((s) => (
            <li key={s.name} className="flex items-center gap-1.5 font-mono text-2xs text-ink-muted">
              <span
                className={cn(
                  "led",
                  s.status === "AIR-GAPPED" ? "bg-caution" : "bg-verified",
                )}
              />
              <span className="truncate" title={`${s.name} · ${s.detail}`}>
                {s.name}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
