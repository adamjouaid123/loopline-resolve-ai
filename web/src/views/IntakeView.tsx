import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAsync } from "../lib/hooks";
import { routeLabel } from "../lib/format";
import {
  ConfidenceBar,
  ErrorState,
  LangBadge,
  Loading,
  PageHead,
  RiskBadge,
} from "../components/primitives";
import { ArrowIcon } from "../components/icons";

export function IntakeView() {
  const { data, loading, error } = useAsync(() => api.cases(), []);

  return (
    <div className="fade-in">
      <PageHead
        title="Claim intake"
        subtitle="Every warranty claim enters here with its form details and multimodal evidence. These six synthetic cases drive the whole pipeline end-to-end."
        actions={<button className="btn btn-primary">+ New claim</button>}
      />

      {loading && <Loading label="Loading claims" />}
      {error && <ErrorState message={error} />}

      {data && (
        <div className="grid grid-auto">
          {data.cases.map((c) => (
            <Link key={c.case_id} to={`/evidence?case=${c.case_id}`} className="card card-hover card-pad">
              <div className="row between" style={{ marginBottom: 12 }}>
                <span className="mono faint">{c.case_id}</span>
                <RiskBadge risk={c.risk_tag} />
              </div>
              <div style={{ fontWeight: 620, fontSize: 15, marginBottom: 4 }}>{c.title}</div>
              <p className="muted" style={{ margin: "0 0 16px", fontSize: 13, minHeight: 38 }}>
                {c.issue}
              </p>

              <div className="dl" style={{ gridTemplateColumns: "88px 1fr", fontSize: 12.5 }}>
                <dt>Customer</dt>
                <dd>{c.customer_name ?? "—"}</dd>
                <dt>Product</dt>
                <dd>{c.product_model ?? "—"}</dd>
              </div>

              <div className="row between wrap" style={{ marginTop: 16, gap: 8 }}>
                <span className="row" style={{ gap: 8 }}>
                  <LangBadge lang={c.language} />
                  <span className="badge badge-neutral">{c.evidence_count} evidence</span>
                </span>
                <span className="row faint" style={{ gap: 6, fontSize: 12 }}>
                  {routeLabel(c.expected_route)}
                  <ArrowIcon style={{ width: 15, height: 15 }} />
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {data && (
        <div className="card card-pad" style={{ marginTop: 22 }}>
          <div className="section-title">Portfolio metrics</div>
          <div className="grid grid-3">
            <Stat label="Active claims" value={data.cases.length} sub="synthetic cases" />
            <Stat
              label="Evidence items"
              value={data.cases.reduce((n, c) => n + c.evidence_count, 0)}
              sub="across all cases"
            />
            <Stat
              label="Languages"
              value={new Set(data.cases.map((c) => c.language).filter(Boolean)).size}
              sub="EN · FR · mixed"
            />
          </div>
        </div>
      )}
      <ConfidenceLegend />
    </div>
  );
}

function Stat({ label, value, sub }: { label: string; value: number | string; sub: string }) {
  return (
    <div className="stat">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      <div className="sub">{sub}</div>
    </div>
  );
}

function ConfidenceLegend() {
  return (
    <div className="row wrap faint" style={{ gap: 18, marginTop: 22, fontSize: 12 }}>
      <span className="row" style={{ gap: 8 }}>
        Confidence bands:
      </span>
      <span className="row" style={{ gap: 8, width: 160 }}>
        <ConfidenceBar value={0.96} /> accepted ≥ 0.85
      </span>
      <span className="row" style={{ gap: 8, width: 160 }}>
        <ConfidenceBar value={0.72} /> review 0.60–0.85
      </span>
      <span className="row" style={{ gap: 8, width: 160 }}>
        <ConfidenceBar value={0.4} /> unreliable &lt; 0.60
      </span>
    </div>
  );
}
