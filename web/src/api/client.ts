// Typed client for the LoopLine Resolve API. In dev, Vite proxies /api and
// /health to the FastAPI backend on :8000 (see vite.config.ts).

export interface AppConfig {
  provider_mode: "azure" | "local" | "mock";
  app_env: string;
  search_index_name: string;
  features: {
    image_generation: boolean;
    video_generation: boolean;
  };
}

export interface CaseSummary {
  case_id: string;
  title: string;
  expected_route: string;
  risk_tag: "normal" | "safety" | "fraud";
  customer_name: string | null;
  product_model: string | null;
  serial_number: string | null;
  issue: string | null;
  language: string | null;
  purchase_date: string | null;
  evidence_count: number;
}

export interface EvidenceItem {
  filename: string;
  label: string;
  modality: "document" | "image" | "audio" | "video" | "form" | "text" | "file";
  sha256: string;
  synthetic: boolean;
}

export type FieldStatus = "accepted" | "review" | "missing" | "conflict";

export interface ExtractionField {
  value: unknown;
  confidence: number | null;
  status: FieldStatus;
  source: Record<string, unknown>;
}

export interface ExtractionResult {
  evidence_id: string;
  provider: string;
  is_simulated: boolean;
  service: string;
  model_or_operation: string;
  fields: Record<string, ExtractionField>;
}

export interface VisualObservation {
  component: string;
  observation: string;
  confidence: number;
}

export interface VisualAnalysisResult {
  evidence_id: string;
  provider: string;
  is_simulated: boolean;
  service: string;
  model_or_operation: string;
  analysis: {
    caption: string;
    alt_text: string;
    observations: VisualObservation[];
    regions: string[];
    visible_text: string[];
    needs_more_evidence: boolean;
    damage_visible: boolean;
    affected_component: string | null;
    serial_visible: boolean;
  };
  visible_text_safety: {
    injection_detected: boolean;
    matched_text: string[];
  };
}

export interface CaseDetail {
  summary: CaseSummary;
  intake: Record<string, unknown> | null;
  evidence: EvidenceItem[];
  extraction: ExtractionResult | null;
  visual_analysis: VisualAnalysisResult | null;
}

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: { Accept: "application/json" } });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} for ${url}`);
  }
  return (await res.json()) as T;
}

export const api = {
  config: () => getJSON<AppConfig>("/api/config"),
  cases: () => getJSON<{ cases: CaseSummary[] }>("/api/cases"),
  case: (id: string) => getJSON<CaseDetail>(`/api/cases/${id}`),
};
