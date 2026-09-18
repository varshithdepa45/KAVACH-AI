import { Panel, PanelHeader, PageTitle, StatusPill } from "@/components/ui";
import { BoundaryDiagram } from "@/components/viz/BoundaryDiagram";
import { AuditLogPanel } from "@/components/viz/AuditLogPanel";
import { securityControls } from "@/lib/data";
import { ShieldCheck, Lock, Wifi, HardDrive, KeyRound, ScrollText, Users, Box, CheckCircle2 } from "lucide-react";

const controlIcon: Record<string, React.ReactNode> = {
  "Air-Gapped": <Wifi className="h-4 w-4" />,
  "External API": <Lock className="h-4 w-4" />,
  "Internet Access": <Wifi className="h-4 w-4" />,
  "Data Residency": <HardDrive className="h-4 w-4" />,
  "Encryption at Rest": <KeyRound className="h-4 w-4" />,
  "Audit Logging": <ScrollText className="h-4 w-4" />,
  RBAC: <Users className="h-4 w-4" />,
  "Sandbox Isolation": <Box className="h-4 w-4" />,
};

export default function SecurityPage() {
  return (
    <div>
      <PageTitle eyebrow="Sovereignty & Compliance" title="Security Center">
        <StatusPill tone="verified" pulse>
          Posture: Secure
        </StatusPill>
      </PageTitle>

      {/* control grid */}
      <div className="mb-3 grid grid-cols-2 gap-3 md:grid-cols-4">
        {securityControls.map((c) => (
          <Panel key={c.name}>
            <div className="p-4">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-verified">{controlIcon[c.name] ?? <ShieldCheck className="h-4 w-4" />}</span>
                <CheckCircle2 className="h-4 w-4 text-verified" />
              </div>
              <div className="eyebrow mb-1">{c.name}</div>
              <div className="font-display text-base font-bold text-verified">{c.state}</div>
            </div>
          </Panel>
        ))}
      </div>

      <div className="grid gap-3 lg:grid-cols-[1.4fr_1fr]">
        {/* boundary */}
        <Panel>
          <PanelHeader title="Data Boundary" sub="Physical & logical containment" right={<StatusPill tone="danger" dot={false}>Egress Denied</StatusPill>} />
          <div className="p-4">
            <BoundaryDiagram />
            <pre className="mt-3 overflow-x-auto rounded-[3px] border border-line bg-surface-inset p-3 font-mono text-2xs leading-relaxed text-ink-muted">
{`┌───────────────────────────────────────────────┐
│            ORGANIZATION NETWORK               │
│                                               │
│   Documents → KAVACH → Local Models           │
│                   ↓                           │
│               Local RAG                        │
│                   ↓                           │
│              Deliverables                      │
│                                               │
│          🚫  INTERNET / CLOUD  🚫             │
└───────────────────────────────────────────────┘`}
            </pre>
          </div>
        </Panel>

        {/* audit log (live when the backend is reachable) */}
        <AuditLogPanel />
      </div>
    </div>
  );
}
