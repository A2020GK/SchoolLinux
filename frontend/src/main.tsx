import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css";
import 'react-data-grid/lib/styles.css';
import { App } from "./App.tsx"
import { InfoProvider } from "./info.tsx"

createRoot(document.body).render(
    <StrictMode>
        <InfoProvider>
            <App />
        </InfoProvider>
    </StrictMode>,
)
