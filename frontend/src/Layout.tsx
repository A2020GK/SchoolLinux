import { Link } from "react-router";

export const Layout = ({ children }: { children: React.ReactNode }) => <>

    <header>
        <h1><Link to="/">School Linux</Link></h1>
    </header>

    <main>
        <div className="content">
            {children}
        </div>
    </main>

    <footer>

    </footer>

</>