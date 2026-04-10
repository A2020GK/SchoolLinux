import React, { createContext, useContext, useEffect, useState } from "react";
import type { UsersMap } from "../types/user";
import { getAllUsers } from "../api/user";
import { onSocketEvent } from "../api/socket";

export interface UsersContextValue {
    users: UsersMap | null;
    loading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
}

const UsersContext = createContext<UsersContextValue | undefined>(undefined);

export const UsersProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [users, setUsers] = useState<UsersMap | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getAllUsers();
            setUsers(response);
        } catch (err) {
            setError(err instanceof Error ? err : new Error(String(err)));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();

        // Subscribe to users_update socket events
        const unsubscribe = onSocketEvent("users_update", (usersPayload) => {
            setUsers(usersPayload as UsersMap);
        });

        return () => unsubscribe();
    }, []);

    const value: UsersContextValue = {
        users,
        loading,
        error,
        refetch: fetchUsers,
    };

    return <UsersContext.Provider value={value}>{children}</UsersContext.Provider>;
};

export const useUsers = (): UsersContextValue => {
    const context = useContext(UsersContext);
    if (!context) {
        throw new Error("useUsers must be used within UsersProvider");
    }
    return context;
};
