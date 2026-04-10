import { useState } from "react";
import type { SafeUserData } from "../types/user";
import { useGame } from "../contexts/GameContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
    faComputer,
    faUser,
    faGem,
    faArrowUpFromBracket,
    faRightFromBracket,
} from "@fortawesome/free-solid-svg-icons";
import { notifyError, notifyInfo } from "../helpers/notify";
import "../styles/student.css";

interface StudentContentProps {
    user: SafeUserData;
    onLogout: () => void;
}

export const StudentContent = ({ user, onLogout }: StudentContentProps) => {
    const { game, loading } = useGame();
    const [submission, setSubmission] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const handleSubmission = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!game?.stringSubmission || !submission.trim()) return;

        setSubmitting(true);
        try {
            // TODO: Implement submission endpoint when available in backend
            // For now, just show the submission UI
            console.log("Submission:", submission);
            notifyInfo("Игра еще не реализована полностью");
        } catch (error) {
            notifyError("Ошибка при отправке");
            console.error(error);
        } finally {
            setSubmitting(false);
            setSubmission("");
        }
    };

    return (
        <main className="student-view content-view">
            <div className="content">
                <h1>
                    <FontAwesomeIcon icon={faComputer} /> {user.pcName}
                </h1>
                <h2>
                    <FontAwesomeIcon icon={faUser} /> {user.name}
                </h2>

                <div className="score-section">
                    <div className="score-display">
                        <FontAwesomeIcon icon={faGem} />
                        <span className="score-value">{user.score}</span>
                    </div>
                </div>

                {game ? (
                    <div className="game-section">
                        <h3>{game.name}</h3>
                        <p>{game.description}</p>

                        {game.stringSubmission ? (
                            <form onSubmit={handleSubmission} className="submission-form">
                                <label htmlFor="answer">
                                    <FontAwesomeIcon icon={faGem} /> Ответ:
                                </label>
                                <div className="form-row">
                                    <input
                                        id="answer"
                                        type="text"
                                        value={submission}
                                        onChange={(e) => setSubmission(e.target.value)}
                                        placeholder="Введите ответ"
                                        disabled={submitting || loading}
                                        required
                                    />
                                    <button type="submit" disabled={submitting || loading}>
                                        <FontAwesomeIcon icon={faArrowUpFromBracket} /> Отправить
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <p className="info-text">Проверка выполняется автоматически через SSH</p>
                        )}
                    </div>
                ) : (
                    <p className="info-text">Игра не выбрана. Ожидайте...</p>
                )}

                <button onClick={onLogout} className="logout-btn">
                    <FontAwesomeIcon icon={faRightFromBracket} /> Выйти
                </button>
            </div>
        </main>
    );
};
