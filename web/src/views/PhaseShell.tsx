import type { ReactNode } from "react";
import { PageHead } from "../components/primitives";
import { SparkIcon } from "../components/icons";

export function PhaseShell({
  title,
  subtitle,
  phase,
  children,
}: {
  title: string;
  subtitle: string;
  phase: string;
  children?: ReactNode;
}) {
  return (
    <div className="fade-in">
      <PageHead title={title} subtitle={subtitle} />
      <div className="placeholder">
        <span className="placeholder-icon">
          <SparkIcon width={24} height={24} />
        </span>
        <h3>Arrives in Phase {phase}</h3>
        <p>
          The UI for this view is designed and in place. Its backend isn&apos;t built yet — this
          screen is deliberately a labeled shell rather than fabricated data, matching the
          project&apos;s &ldquo;real schema, honest state&rdquo; principle.
        </p>
        {children}
      </div>
    </div>
  );
}

export function KnowledgeView() {
  return (
    <PhaseShell
      title="Knowledge & recommendation"
      subtitle="Ask policy questions, inspect retrieved chunks and citations, then run the agentic resolution workflow with evidence-based reasons."
      phase="9 & 10"
    >
      <div className="row wrap" style={{ gap: 8, justifyContent: "center" }}>
        <span className="badge badge-neutral">Hybrid retrieval</span>
        <span className="badge badge-neutral">Grounded citations</span>
        <span className="badge badge-neutral">Required abstention</span>
      </div>
    </PhaseShell>
  );
}

export function ApprovalView() {
  return (
    <PhaseShell
      title="Supervisor approval"
      subtitle="Approve, reject, or return a proposal. Consequential actions require comments; translated text and audio responses generate only after approval."
      phase="10 & 11"
    >
      <div className="row wrap" style={{ gap: 8, justifyContent: "center" }}>
        <span className="badge badge-success">Human-in-the-loop</span>
        <span className="badge badge-neutral">Immutable audit</span>
        <span className="badge badge-neutral">No autonomous approval</span>
      </div>
    </PhaseShell>
  );
}

export function OpsView() {
  return (
    <PhaseShell
      title="Evaluation & operations"
      subtitle="Groundedness, relevance, citation validity, tool accuracy, safety pass rate, latency, token use, and errors — with the active provider surfaced per result."
      phase="12 & 13"
    >
      <div className="row wrap" style={{ gap: 8, justifyContent: "center" }}>
        <span className="badge badge-neutral">Release gates</span>
        <span className="badge badge-neutral">Regression suite</span>
        <span className="badge badge-neutral">Tracing &amp; telemetry</span>
      </div>
    </PhaseShell>
  );
}
