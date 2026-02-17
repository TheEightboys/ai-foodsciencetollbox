/**
 * Application Entry Point
 * 
 * Initializes the React application and mounts it to the DOM.
 * This is the first file executed when the application loads.
 */

import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

// Pre-warm the backend on app load so Render wakes up immediately
// This runs silently — if it fails, no user impact
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
if (API_BASE) {
  fetch(`${API_BASE.replace(/\/+$/, '')}/api/health/`, { method: 'HEAD', mode: 'cors' }).catch(() => {});
  // Keep the backend alive by pinging every 10 minutes
  setInterval(() => {
    fetch(`${API_BASE.replace(/\/+$/, '')}/api/health/`, { method: 'HEAD', mode: 'cors' }).catch(() => {});
  }, 10 * 60 * 1000);
}

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found. Ensure <div id='root'></div> exists in index.html");
}

createRoot(rootElement).render(<App />);
