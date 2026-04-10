import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
    faRightToBracket,
    faComputer,
    faUser,
    faGear,
} from "@fortawesome/free-solid-svg-icons";
import "../styles/student.css";

interface StudentLoginFormProps {
    onLoginSubmit: (pcName: string, name: string) => void;
    isLoading: boolean;
}

export const StudentLoginForm = ({ onLoginSubmit, isLoading }: StudentLoginFormProps) => {
    const [pcName, setPcName] = useState("");
    const [name, setName] = useState("");

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (pcName.trim() && name.trim()) {
            onLoginSubmit(pcName, name);
        }
    };

    return (
        <main className="student-view login-view">
            <div className="content">
                <h1>
                    <FontAwesomeIcon icon={faRightToBracket} /> Регистрация
                </h1>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="pc">
                            <FontAwesomeIcon icon={faComputer} /> Номер компьютера
                        </label>
                        <details>
                            <summary>Рекомендуемый формат</summary>
                            <p>
                                <i>Формат: &lt;номер кабинета&gt;-&lt;номер компьютера&gt;, пример: 403-1</i>
                            </p>
                        </details>
                        <input
                            id="pc"
                            type="text"
                            value={pcName}
                            onChange={(e) => setPcName(e.target.value)}
                            placeholder="Номер компьютера"
                            disabled={isLoading}
                            required
                        />
                    </div>

                    <hr />

                    <div className="form-group">
                        <label htmlFor="name">
                            <FontAwesomeIcon icon={faUser} /> Полное имя
                        </label>
                        <details>
                            <summary>Рекомендуемый формат</summary>
                            <p>
                                <i>Формат: &lt;Имя&gt; &lt;Фамилия&gt;, пример: Тест Тестовский</i>
                            </p>
                            <p>
                                <i>При работе в команде из нескольких человек указывайте имена и фамилии через запятую</i>
                            </p>
                        </details>
                        <input
                            id="name"
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Полное имя"
                            disabled={isLoading}
                            required
                        />
                    </div>

                    <button type="submit" disabled={isLoading}>
                        <FontAwesomeIcon icon={faRightToBracket} /> Подключиться
                    </button>

                    {isLoading && (
                        <p className="loading-text">
                            <FontAwesomeIcon icon={faGear} className="spinner" /> Ваш компьютер проверяется, пожалуйста подождите...
                        </p>
                    )}

                    <p className="disclaimer">
                        <i><small>Вы можете быть дисквалифицированы за грубое несоответствие данных формату/некорректные данные</small></i>
                    </p>
                </form>
            </div>
        </main>
    );
};
