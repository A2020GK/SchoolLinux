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
import { checkGame } from "../api/game";
import { useUser } from "../contexts/UserContext";
import { notifyError, notifyInfo } from "../helpers/notify";
import "../styles/student.css";

interface StudentContentProps {
    user: SafeUserData;
    onLogout: () => void;
}

export const StudentContent = ({ user, onLogout }: StudentContentProps) => {
    const { game, gameState, loading } = useGame();
    const { refetch: refetchUser } = useUser();
    const [submission, setSubmission] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const handleSubmission = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!game) return;
        if (game.stringSubmission && !submission.trim()) return;
        if (user.kicked) {
            notifyInfo("Вы были отключены преподавателем");
            return;
        }
        if (gameState !== "running") {
            notifyInfo("Сейчас проверка недоступна: игра не запущена");
            return;
        }

        setSubmitting(true);
        try {
            await checkGame(game.stringSubmission ? submission.trim() : "");
            await refetchUser();
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

                {game && (
                    <p className="required-score-info">Требуемый счёт: {game.requiredUserScore}</p>
                )}

                {game ? (
                    <div className="game-section">
                        <h3>{game.name}</h3>
                        <p>{game.description}</p>

                        <form onSubmit={handleSubmission} className="submission-form">
                            {game.stringSubmission ? (
                                <>
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
                                            disabled={submitting || loading || gameState !== "running" || user.kicked}
                                            required
                                        />
                                        <button type="submit" disabled={submitting || loading || gameState !== "running" || user.kicked}>
                                            <FontAwesomeIcon icon={faArrowUpFromBracket} /> Проверить
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <p className="info-text">Проверка выполняется через SSH</p>
                                    <button type="submit" disabled={submitting || loading || gameState !== "running" || user.kicked}>
                                        <FontAwesomeIcon icon={faArrowUpFromBracket} /> Проверить
                                    </button>
                                </>
                            )}
                        </form>

                        {user.kicked && (
                            <p className="info-text">Ваш доступ временно ограничен преподавателем</p>
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
