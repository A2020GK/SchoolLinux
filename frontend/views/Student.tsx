import { useState } from "react";
import { useUser } from "../contexts/UserContext";
import { deleteCurrentUser, registerUser } from "../api/user";
import { StudentLoginForm } from "./StudentLoginForm";
import { StudentContent } from "./StudentContent";
import { notifyError } from "../helpers/notify";

export const Student = () => {
    const { user, refetch } = useUser();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleLogin = async (pcName: string, name: string) => {
        setIsLoading(true);
        setError(null);
        try {
            await registerUser({ pcName, name });
            // Refetch user data after registration
            await refetch();
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Ошибка при регистрации";
            setError(errorMsg);
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogout = async () => {
        const confirmed = window.confirm("Выйти из игры и удалить ваши данные на сервере?");
        if (!confirmed) {
            return;
        }

        try {
            await deleteCurrentUser();
            await refetch();
        } catch (err) {
            notifyError("Не удалось выйти и удалить данные");
            console.error(err);
        }
    };

    // Show form if not logged in (user is null or doesn't have user data)
    if (user === null || !user.user) {
        return (
            <>
                <StudentLoginForm 
                    onLoginSubmit={handleLogin} 
                    isLoading={isLoading}
                />
                {error && <div className="error-banner">{error}</div>}
            </>
        );
    }

    // Show content if logged in
    return (
        <StudentContent 
            user={user.user} 
            onLogout={handleLogout}
        />
    );
};
