import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
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
          <div className="card">
            <div className="card-pad row between" style={{ borderBottom: "1px solid var(--border)" }}>
              <div className="section-title" style={{ margin: 0 }}>
                Extracted fields
              </div>
              {detail.data.extraction && (
                <span className="row faint mono" style={{ gap: 10, fontSize: 12 }}>
                  <span>{detail.data.extraction.service}</span>
                  <span className={`badge ${detail.data.extraction.is_simulated ? "badge-neutral" : "badge-info"}`}>
                    {detail.data.extraction.provider}
                    {detail.data.extraction.is_simulated ? " · simulated" : ""}
                  </span>
                </span>
              )}
            </div>

            {!detail.data.extraction && (
              <div className="center-state">No document extraction for this case.</div>
            )}

            {detail.data.extraction && (
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
                  {Object.entries(detail.data.extraction.fields).map(([name, f]) => (
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
        </div>
      )}
    </div>
  );
}
