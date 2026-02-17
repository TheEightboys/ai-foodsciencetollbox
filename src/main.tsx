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
  const healthUrl = `${API_BASE.replace(/\/+$/, '')}/api/health/`;
  // Use no-cors mode for silent pings — we don't need to read the response,
  // we just need to trigger the request so Render wakes up
  fetch(healthUrl, { method: 'GET', mode: 'no-cors' }).catch(() => {});
  // Keep the backend alive by pinging every 5 minutes
  setInterval(() => {
    fetch(healthUrl, { method: 'GET', mode: 'no-cors' }).catch(() => {});
  }, 5 * 60 * 1000);
}

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found. Ensure <div id='root'></div> exists in index.html");
}

createRoot(rootElement).render(<App />);
