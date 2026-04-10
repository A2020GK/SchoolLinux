import { useState } from "react";
import { useUser } from "../contexts/UserContext";
import { registerUser } from "../api/user";
import { StudentLoginForm } from "./StudentLoginForm";
import { StudentContent } from "./StudentContent";

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
        // TODO: Implement logout endpoint in backend
        // For now, just trigger a refetch
        await refetch();
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
