import { useAsync } from "../lib/hooks";
import { api } from "../api/client";

export function ProviderBadge() {
  const { data } = useAsync(() => api.config(), []);
  const mode = data?.provider_mode ?? "…";
  const cls =
    mode === "azure" ? "badge-info" : mode === "local" ? "badge-accent" : "badge-neutral";
  const simulated = mode === "mock";
  return (
    <span className={`badge ${cls}`} title={simulated ? "Simulated data" : "Live provider"}>
      <span className="dot" />
      {mode}
      {simulated ? " · simulated" : ""}
    </span>
  );
}
