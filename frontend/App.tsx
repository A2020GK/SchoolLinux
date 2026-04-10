import { useUser } from "./contexts/UserContext";
import { Teacher } from "./views/Teacher";
import { Student } from "./views/Student";
import { Footer } from "./Footer";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleNotch } from "@fortawesome/free-solid-svg-icons";
import { faLinux } from "@fortawesome/free-brands-svg-icons";
import "./App.css";

export const App = () => {
    const { user, loading: userLoading } = useUser();

    const isTeacher = user?.isTeacher ?? false;
    const isLoading = userLoading;

    return (
        <>
            <header>
                <h1>
                    <FontAwesomeIcon icon={faLinux} /> School Linux
                </h1>
            </header>

            {isLoading ? (
                <main className="loading-view">
                    <div className="loading-spinner">
                        <FontAwesomeIcon icon={faCircleNotch} className="spinner" />
                        <p>Загрузка...</p>
                    </div>
                </main>
            ) : isTeacher ? (
                <Teacher />
            ) : (
                <Student />
            )}

            <Footer />
        </>
    );
};