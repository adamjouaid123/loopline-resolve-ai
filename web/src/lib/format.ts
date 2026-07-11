export function routeLabel(route: string): string {
  return route
    .split("_")
    .join(" ")
    .replace(/^\w/, (c) => c.toUpperCase());
}

export function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return String(value);
  return String(value);
}

export function fieldLabel(name: string): string {
  return name
    .split("_")
    .join(" ")
    .replace(/^\w/, (c) => c.toUpperCase());
}
