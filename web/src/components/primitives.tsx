import type { ReactNode } from "react";
import type { FieldStatus, EvidenceItem } from "../api/client";
import {
  AudioIcon,
  DocIcon,
  FormIcon,
  ImageIcon,
  TextIcon,
  VideoIcon,
} from "./icons";

export function StatusBadge({ status }: { status: FieldStatus }) {
  const map: Record<FieldStatus, { cls: string; label: string }> = {
    accepted: { cls: "badge-success", label: "Accepted" },
    review: { cls: "badge-warning", label: "Review" },
    missing: { cls: "badge-neutral", label: "Missing" },
    conflict: { cls: "badge-danger", label: "Conflict" },
  };
  const { cls, label } = map[status];
  return (
    <span className={`badge ${cls}`}>
      <span className="dot" />
      {label}
    </span>
  );
}

export function RiskBadge({ risk }: { risk: "normal" | "safety" | "fraud" }) {
  if (risk === "safety")
    return <span className="badge badge-danger">Safety-critical</span>;
  if (risk === "fraud")
    return <span className="badge badge-warning">Fraud review</span>;
  return <span className="badge badge-neutral">Standard</span>;
}

export function ConfidenceBar({ value }: { value: number | null }) {
  if (value == null) {
    return <span className="faint mono">n/a</span>;
  }
  const pct = Math.round(value * 100);
  const color =
    value >= 0.85 ? "var(--success)" : value >= 0.6 ? "var(--warning)" : "var(--danger)";
  return (
    <div className="conf">
      <div className="conf-track">
        <div className="conf-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="conf-val">{value.toFixed(2)}</span>
    </div>
  );
}

const MODALITY_ICON = {
  document: DocIcon,
  image: ImageIcon,
  audio: AudioIcon,
  video: VideoIcon,
  form: FormIcon,
  text: TextIcon,
  file: DocIcon,
} as const;

export function ModalityChip({ item }: { item: EvidenceItem }) {
  const Icon = MODALITY_ICON[item.modality] ?? DocIcon;
  return (
    <span className="chip">
      <Icon />
      {item.label}
    </span>
  );
}

export function PageHead({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="page-head row between wrap" style={{ alignItems: "flex-start" }}>
      <div>
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {actions}
    </div>
  );
}

export function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div className="center-state">
      <span className="spinner" />
      {label}…
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="center-state">
      <span className="badge badge-danger">Error</span>
      <span className="muted mono">{message}</span>
    </div>
  );
}

export function LangBadge({ lang }: { lang: string | null }) {
  if (!lang) return null;
  return <span className="badge badge-neutral">{lang.toUpperCase()}</span>;
}
