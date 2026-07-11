import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { IntakeView } from "./views/IntakeView";
import { EvidenceView } from "./views/EvidenceView";
import { ApprovalView, KnowledgeView, OpsView } from "./views/PhaseShell";
import "./styles/global.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/intake" replace /> },
      { path: "intake", element: <IntakeView /> },
      { path: "evidence", element: <EvidenceView /> },
      { path: "knowledge", element: <KnowledgeView /> },
      { path: "approval", element: <ApprovalView /> },
      { path: "ops", element: <OpsView /> },
      { path: "*", element: <Navigate to="/intake" replace /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
