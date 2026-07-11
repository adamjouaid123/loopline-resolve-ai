import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import {
  ApprovalIcon,
  EvidenceIcon,
  IntakeIcon,
  KnowledgeIcon,
  MenuIcon,
  MoonIcon,
  OpsIcon,
  SunIcon,
} from "./icons";
import { ProviderBadge } from "./ProviderBadge";
import { useTheme } from "../lib/hooks";

const NAV = [
  { to: "/intake", label: "Claim intake", Icon: IntakeIcon, phase: null },
  { to: "/evidence", label: "Evidence workspace", Icon: EvidenceIcon, phase: null },
  { to: "/knowledge", label: "Knowledge & RAG", Icon: KnowledgeIcon, phase: "9" },
  { to: "/approval", label: "Supervisor approval", Icon: ApprovalIcon, phase: "10" },
  { to: "/ops", label: "Evaluation & ops", Icon: OpsIcon, phase: "12" },
];

export function AppShell() {
  const [theme, toggleTheme] = useTheme();
  const [open, setOpen] = useState(false);

  return (
    <div className="app">
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="brand">
          <span className="brand-mark">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.1" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 12a8 8 0 1 1 8 8" />
              <path d="M12 8v4l3 2" />
            </svg>
          </span>
          <div>
            <div className="brand-name">LoopLine Resolve</div>
            <div className="brand-sub">Warranty copilot</div>
          </div>
        </div>

        <div className="nav-section">Workspace</div>
        {NAV.map(({ to, label, Icon, phase }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            onClick={() => setOpen(false)}
          >
            <Icon />
            {label}
            {phase && <span className="badge badge-neutral badge-mini">P{phase}</span>}
          </NavLink>
        ))}

        <div className="sidebar-foot">
          <div className="row between">
            <span className="faint" style={{ fontSize: 12 }}>
              Provider
            </span>
            <ProviderBadge />
          </div>
          <button className="btn btn-ghost row between" onClick={toggleTheme} style={{ width: "100%" }}>
            <span className="row" style={{ gap: 8 }}>
              {theme === "dark" ? <MoonIcon /> : <SunIcon />}
              {theme === "dark" ? "Dark" : "Light"} theme
            </span>
            <span className="faint" style={{ fontSize: 11 }}>
              toggle
            </span>
          </button>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <button
            className="btn btn-icon btn-ghost"
            onClick={() => setOpen((o) => !o)}
            aria-label="Toggle navigation"
            style={{ display: "none" }}
            data-mobile-toggle
          >
            <MenuIcon />
          </button>
          <h1>LoopLine Resolve AI</h1>
          <span className="crumb">Multimodal warranty-claims &amp; repair copilot</span>
          <div className="topbar-spacer" />
          <button className="btn btn-icon" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "dark" ? <SunIcon /> : <MoonIcon />}
          </button>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
