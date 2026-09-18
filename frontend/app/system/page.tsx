"use client";

import { useEffect, useState } from "react";
import { Panel, PanelHeader, PageTitle, StatusPill, Meter, SourceChip } from "@/components/ui";
import { BackendStatus } from "@/components/viz/BackendStatus";
import { systemStatus } from "@/lib/data";
import { useLive, fetchSystem } from "@/lib/live";
import { clamp } from "@/lib/utils";
import { Cpu, MemoryStick, Server, Gauge, Activity, ShieldCheck } from "lucide-react";

export default function SystemPage() {
  const [gpu, setGpu] = useState(systemStatus.gpu);
  const [cpu, setCpu] = useState(systemStatus.cpu);
  const [ram, setRam] = useState(systemStatus.ram);
  const [spark, setSpark] = useState<number[]>(Array.from({ length: 40 }, (_, i) => 60 + Math.sin(i / 3) * 12));
  const { data: live, source } = useLive(fetchSystem, {
    gpu: systemStatus.gpu,
    vramUsedPct: 44,
    services: systemStatus.services.map((s) => ({ name: s.name, detail: s.detail, status: s.status })),
  });
  const services = live.services;

  useEffect(() => {
    const id = setInterval(() => {
      setGpu((g) => clamp(g + (Math.random() * 8 - 4), 62, 92));
      setCpu((c) => clamp(c + (Math.random() * 6 - 3), 22, 55));
      setRam((r) => clamp(r + (Math.random() * 4 - 2), 55, 74));
      setSpark((s) => [...s.slice(1), clamp(s[s.length - 1] + (Math.random() * 16 - 8), 40, 95)]);
    }, 1200);
    return () => clearInterval(id);
  }, []);

  const vramUsed = ((gpu / 100) * systemStatus.vramTotal).toFixed(1);

  return (
    <div>
      <PageTitle eyebrow="On-Premise Appliance" title="System">
        <BackendStatus />
      </PageTitle>

      <div className="grid gap-3 lg:grid-cols-3">
        {/* GPU */}
        <Panel className="lg:col-span-2">
          <PanelHeader title="Local GPU" sub={systemStatus.gpuModel} icon={<Gauge className="h-4 w-4" />} right={<span className="font-mono text-2xs text-signal">{gpu.toFixed(0)}% util</span>} />
          <div className="p-4">
            {/* sparkline */}
            <svg viewBox="0 0 200 44" className="mb-4 h-16 w-full" preserveAspectRatio="none">
              <defs>
                <linearGradient id="sp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3DD4C0" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#3DD4C0" stopOpacity="0" />
                </linearGradient>
              </defs>
              <polyline
                points={spark.map((v, i) => `${(i / (spark.length - 1)) * 200},${44 - (v / 100) * 44}`).join(" ")}
                fill="none"
                stroke="#3DD4C0"
                strokeWidth="1.5"
              />
              <polygon
                points={`0,44 ${spark.map((v, i) => `${(i / (spark.length - 1)) * 200},${44 - (v / 100) * 44}`).join(" ")} 200,44`}
                fill="url(#sp)"
              />
            </svg>
            <div className="grid grid-cols-3 gap-4">
              <Gauge2 label="GPU Utilisation" value={gpu} unit="%" icon={<Gauge className="h-4 w-4" />} />
              <Gauge2 label="CPU" value={cpu} unit="%" icon={<Cpu className="h-4 w-4" />} />
              <Gauge2 label="System RAM" value={ram} unit="%" icon={<MemoryStick className="h-4 w-4" />} />
            </div>
            <div className="mt-4 rounded-[3px] border border-line bg-surface-inset px-3 py-2">
              <div className="mb-1 flex items-center justify-between font-mono text-2xs text-ink-muted">
                <span>VRAM (model weights + KV cache)</span>
                <span className="text-ink">{vramUsed} / {systemStatus.vramTotal} GB</span>
              </div>
              <Meter value={(Number(vramUsed) / systemStatus.vramTotal) * 100} />
            </div>
          </div>
        </Panel>

        {/* services */}
        <Panel>
          <PanelHeader
            title="Services"
            icon={<Server className="h-4 w-4" />}
            right={<SourceChip source={source} />}
          />
          <ul className="divide-y divide-line">
            {services.map((s) => (
              <li key={s.name} className="flex items-center gap-3 px-4 py-2.5">
                <span
                  className={`led animate-blip ${
                    s.status === "AIR-GAPPED" ? "bg-caution" : s.status === "SECURE" ? "bg-info" : "bg-verified"
                  }`}
                />
                <div className="flex-1">
                  <div className="font-mono text-xs text-ink">{s.name}</div>
                  <div className="font-mono text-2xs text-ink-faint">{s.detail}</div>
                </div>
                <StatusPill
                  tone={s.status === "AIR-GAPPED" ? "caution" : s.status === "SECURE" ? "info" : "verified"}
                  dot={false}
                >
                  {s.status}
                </StatusPill>
              </li>
            ))}
          </ul>
        </Panel>
      </div>

      {/* deployment note */}
      <Panel className="mt-3">
        <PanelHeader title="Deployment" sub="This is a demonstration prototype" icon={<ShieldCheck className="h-4 w-4" />} />
        <div className="grid gap-4 p-4 md:grid-cols-2">
          <div>
            <div className="eyebrow mb-2">Inference Mode</div>
            <p className="text-xs leading-relaxed text-ink-muted">
              The prototype ships with a <span className="text-signal">Mock Local Inference</span> provider so the full
              workflow runs deterministically with no GPU. The provider interface (<span className="font-mono text-ink">generate · analyze_image · embed · health_check</span>)
              is drop-in replaceable with Ollama, llama.cpp or vLLM adapters — nothing above the provider layer changes.
            </p>
          </div>
          <div>
            <div className="eyebrow mb-2">Sovereignty Guarantees</div>
            <ul className="space-y-1 font-mono text-2xs text-ink-muted">
              <li className="text-verified">✓ KAVACH_MODE=airgapped — external providers disabled</li>
              <li className="text-verified">✓ No OpenAI / Anthropic / Gemini / cloud APIs</li>
              <li className="text-verified">✓ Documents, embeddings & outputs stay on-premise</li>
              <li className="text-verified">✓ Every action written to a local audit log</li>
            </ul>
          </div>
        </div>
      </Panel>
    </div>
  );
}

function Gauge2({ label, value, unit, icon }: { label: string; value: number; unit: string; icon: React.ReactNode }) {
  return (
    <div className="rounded-[3px] border border-line bg-surface-inset p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="eyebrow">{label}</span>
        <span className="text-signal">{icon}</span>
      </div>
      <div className="mb-2 font-display text-2xl font-bold text-ink">
        {value.toFixed(0)}
        <span className="text-sm text-ink-muted">{unit}</span>
      </div>
      <Meter value={value} tone={value > 85 ? "caution" : "signal"} />
    </div>
  );
}
