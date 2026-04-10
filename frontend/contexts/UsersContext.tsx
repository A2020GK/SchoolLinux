import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { UsersMap } from "../types/user";
import { getAllUsers } from "../api/user";
import { onSocketEvent } from "../api/socket";
import { toError } from "../helpers/error";
import { frontendEnv } from "../config/env";

export interface UsersContextValue {
    users: UsersMap | null;
    loading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
    updateUserKicked: (ip: string, kicked: boolean) => void;
}

const UsersContext = createContext<UsersContextValue | undefined>(undefined);

export const UsersProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [users, setUsers] = useState<UsersMap | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchUsers = useCallback(async () => {
        if (frontendEnv.mockPreview.enabled) {
            setLoading(false);
            setError(null);
            setUsers(frontendEnv.mockPreview.users);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const response = await getAllUsers();
            setUsers(response);
        } catch (err) {
            setError(toError(err));
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUsers();

        if (frontendEnv.mockPreview.enabled) {
            return;
        }

        // Subscribe to users_update socket events
        const unsubscribe = onSocketEvent("users_update", (usersPayload) => {
            setUsers(usersPayload as UsersMap);
        });

        return () => unsubscribe();
    }, []);

    const handleUpdateUserKicked = useCallback((ip: string, kicked: boolean) => {
        setUsers((prevUsers) => {
            if (!prevUsers) return prevUsers;
            return {
                ...prevUsers,
                [ip]: {
                    ...prevUsers[ip],
                    kicked,
                },
            };
        });
    }, []);

    const value: UsersContextValue = useMemo(() => ({
        users,
        loading,
        error,
        refetch: fetchUsers,
        updateUserKicked: handleUpdateUserKicked,
    }), [error, fetchUsers, handleUpdateUserKicked, loading, users]);

    return <UsersContext.Provider value={value}>{children}</UsersContext.Provider>;
};

export const useUsers = (): UsersContextValue => {
    const context = useContext(UsersContext);
    if (!context) {
        throw new Error("useUsers must be used within UsersProvider");
    }
    return context;
};
