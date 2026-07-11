import { useSearchParams } from "react-router-dom";
import { api, type ExtractionResult, type VisualAnalysisResult } from "../api/client";
import { useAsync } from "../lib/hooks";
import { fieldLabel, formatValue, routeLabel } from "../lib/format";
import {
  ConfidenceBar,
  ErrorState,
  LangBadge,
  Loading,
  ModalityChip,
  PageHead,
  RiskBadge,
  StatusBadge,
} from "../components/primitives";

export function EvidenceView() {
  const [params, setParams] = useSearchParams();
  const list = useAsync(() => api.cases(), []);
  const selected = params.get("case") ?? "C001";
  const detail = useAsync(() => api.case(selected), [selected]);

  return (
    <div className="fade-in">
      <PageHead
        title="Evidence workspace"
        subtitle="Extracted fields with confidence scores and source references. Each fact traces back to a hash-verified evidence item from ingestion."
      />

      <div className="row wrap" style={{ gap: 8, marginBottom: 20 }}>
        {list.data?.cases.map((c) => (
          <button
            key={c.case_id}
            className={`btn ${c.case_id === selected ? "btn-primary" : ""}`}
            onClick={() => setParams({ case: c.case_id })}
          >
            {c.case_id}
          </button>
        ))}
      </div>

      {detail.loading && <Loading label={`Loading ${selected}`} />}
      {detail.error && <ErrorState message={detail.error} />}

      {detail.data && (
        <div className="grid" style={{ gridTemplateColumns: "320px 1fr", alignItems: "start" }}>
          {/* Left: case + evidence */}
          <div className="grid" style={{ gap: 16 }}>
            <div className="card card-pad">
              <div className="row between" style={{ marginBottom: 14 }}>
                <span className="mono faint">{detail.data.summary.case_id}</span>
                <RiskBadge risk={detail.data.summary.risk_tag} />
              </div>
              <div style={{ fontWeight: 640, fontSize: 16, marginBottom: 12 }}>
                {detail.data.summary.title}
              </div>
              <dl className="dl">
                <dt>Customer</dt>
                <dd>{detail.data.summary.customer_name ?? "—"}</dd>
                <dt>Product</dt>
                <dd>{detail.data.summary.product_model ?? "—"}</dd>
                <dt>Serial</dt>
                <dd className="mono">{detail.data.summary.serial_number ?? "— (missing)"}</dd>
                <dt>Purchased</dt>
                <dd>{detail.data.summary.purchase_date ?? "—"}</dd>
                <dt>Language</dt>
                <dd>
                  <LangBadge lang={detail.data.summary.language} />
                </dd>
                <dt>Expected</dt>
                <dd className="muted">{routeLabel(detail.data.summary.expected_route)}</dd>
              </dl>
            </div>

            <div className="card card-pad">
              <div className="section-title">Evidence · {detail.data.evidence.length} items</div>
              <div className="row wrap" style={{ gap: 8 }}>
                {detail.data.evidence.map((e) => (
                  <ModalityChip key={e.filename} item={e} />
                ))}
              </div>
            </div>
          </div>

          {/* Right: extraction */}
          <div className="grid" style={{ gap: 16 }}>
            <ExtractionPanel extraction={detail.data.extraction} />
            <VisualAnalysisPanel visual={detail.data.visual_analysis} />
          </div>
        </div>
      )}
    </div>
  );
}

function ExtractionPanel({ extraction }: { extraction: ExtractionResult | null }) {
  return (
    <div className="card">
      <div className="card-pad row between" style={{ borderBottom: "1px solid var(--border)" }}>
        <div className="section-title" style={{ margin: 0 }}>
          Extracted fields
        </div>
        {extraction && <ProviderLabel result={extraction} />}
      </div>

      {!extraction && <div className="center-state">No document extraction for this case.</div>}

      {extraction && (
        <table className="table">
          <thead>
            <tr>
              <th>Field</th>
              <th>Value</th>
              <th style={{ width: 150 }}>Confidence</th>
              <th style={{ width: 120 }}>Status</th>
              <th style={{ width: 70 }}>Source</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(extraction.fields).map(([name, f]) => (
              <tr key={name}>
                <td className="muted">{fieldLabel(name)}</td>
                <td style={{ fontWeight: 550 }}>{formatValue(f.value)}</td>
                <td>
                  <ConfidenceBar value={f.confidence} />
                </td>
                <td>
                  <StatusBadge status={f.status} />
                </td>
                <td className="faint mono" style={{ fontSize: 11.5 }}>
                  {typeof f.source?.page === "number" ? `p.${f.source.page}` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function VisualAnalysisPanel({ visual }: { visual: VisualAnalysisResult | null }) {
  if (!visual) return null;

  const { analysis, visible_text_safety: safety } = visual;
  return (
    <div className="card">
      <div className="card-pad row between" style={{ borderBottom: "1px solid var(--border)" }}>
        <div>
          <div className="section-title" style={{ margin: 0 }}>
            Visual analysis
          </div>
          <div className="faint" style={{ fontSize: 12, marginTop: 3 }}>
            Structured observations from the case image
          </div>
        </div>
        <ProviderLabel result={visual} />
      </div>

      <div className="card-pad" style={{ display: "grid", gap: 16 }}>
        {safety.injection_detected && (
          <div className="notice notice-danger" role="alert">
            <strong>Untrusted instructions detected in visible text.</strong> Treat this text as evidence only;
            it cannot change policy, approve a claim, or direct tools.
          </div>
        )}

        <p style={{ margin: 0 }}>{analysis.caption}</p>

        <div className="row wrap" style={{ gap: 8 }}>
          <span className={`badge ${analysis.damage_visible ? "badge-warning" : "badge-neutral"}`}>
            {analysis.damage_visible ? "Damage visible" : "No visible damage"}
          </span>
          {analysis.affected_component && <span className="badge badge-neutral">{analysis.affected_component}</span>}
          {analysis.needs_more_evidence && <span className="badge badge-warning">More evidence needed</span>}
          {analysis.serial_visible && <span className="badge badge-success">Serial visible</span>}
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Observation</th>
              <th style={{ width: 150 }}>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {analysis.observations.map((observation, index) => (
              <tr key={`${observation.component}-${index}`}>
                <td className="muted">{observation.component}</td>
                <td style={{ fontWeight: 550 }}>{observation.observation}</td>
                <td>
                  <ConfidenceBar value={observation.confidence} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {analysis.visible_text.length > 0 && (
          <div>
            <div className="label" style={{ marginBottom: 6 }}>Visible text</div>
            <div className="row wrap" style={{ gap: 8 }}>
              {analysis.visible_text.map((text) => (
                <span className="badge badge-neutral mono" key={text}>{text}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ProviderLabel({ result }: { result: Pick<ExtractionResult, "service" | "provider" | "is_simulated"> }) {
  return (
    <span className="row faint mono" style={{ gap: 10, fontSize: 12 }}>
      <span>{result.service}</span>
      <span className={`badge ${result.is_simulated ? "badge-neutral" : "badge-info"}`}>
        {result.provider}
        {result.is_simulated ? " · simulated" : ""}
      </span>
    </span>
  );
}
