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

export interface CaseDetail {
  summary: CaseSummary;
  intake: Record<string, unknown> | null;
  evidence: EvidenceItem[];
  extraction: ExtractionResult | null;
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
