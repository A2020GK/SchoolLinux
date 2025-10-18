import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter, Route, Routes } from 'react-router'
import { Layout } from './Layout.tsx'
import { Home } from './Home.tsx'
import { Config } from './Config.tsx'
import { StatusProvider } from './StatusContext.tsx'

export const apiAddr = `${location.hostname}:${import.meta.env.VITE_BACKEND_SERVER_PORT}`
export const apiBase = `http://${apiAddr}`;

createRoot(document.body).render(
    <StrictMode>
        <BrowserRouter>
            <StatusProvider>
                <Layout>
                    <Routes>
                        <Route path="/" Component={Home} />
                        <Route path="/config" Component={Config} />
                    </Routes>
                </Layout>
            </StatusProvider>
        </BrowserRouter>
    </StrictMode>,
)