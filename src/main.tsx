/**
 * Application Entry Point
 * 
 * Initializes the React application and mounts it to the DOM.
 * This is the first file executed when the application loads.
 */

import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found. Ensure <div id='root'></div> exists in index.html");
}

createRoot(rootElement).render(<App />);
