import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { App } from "./App"
import { UserProvider } from "./contexts/UserContext"
import { GameProvider } from "./contexts/GameContext"
import { UsersProvider } from "./contexts/UsersContext"
import { ExtendedGameProvider } from "./contexts/ExtendedGameContext"
import "./index.css";

createRoot(document.body).render(
    <StrictMode>
        <UserProvider>
            <GameProvider>
                <UsersProvider>
                    <ExtendedGameProvider>
                        <App />
                    </ExtendedGameProvider>
                </UsersProvider>
            </GameProvider>
        </UserProvider>
    </StrictMode>,
)
