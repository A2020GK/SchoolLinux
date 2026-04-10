import React, { createContext, useContext, useEffect, useState } from "react";
import type { UserResponse } from "../types/user";
import { getCurrentUser } from "../api/user";

export interface UserContextValue {
    user: UserResponse | null;
    loading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
}

const UserContext = createContext<UserContextValue | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<UserResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchUser = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getCurrentUser();
            setUser(response);
        } catch (err) {
            setError(err instanceof Error ? err : new Error(String(err)));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUser();
    }, []);

    const value: UserContextValue = {
        user,
        loading,
        error,
        refetch: fetchUser,
    };

    return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export const useUser = (): UserContextValue => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error("useUser must be used within UserProvider");
    }
    return context;
};
