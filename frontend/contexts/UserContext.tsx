import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { UserResponse } from "../types/user";
import { getCurrentUser } from "../api/user";
import { onSocketEvent } from "../api/socket";
import { toError } from "../helpers/error";
import { frontendEnv, getMockUserResponse } from "../config/env";

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

    const fetchUser = useCallback(async () => {
        if (frontendEnv.mockPreview.enabled) {
            setLoading(false);
            setError(null);
            setUser(getMockUserResponse());
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const response = await getCurrentUser();
            setUser(response);
        } catch (err) {
            setError(toError(err));
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUser();

        if (frontendEnv.mockPreview.enabled) {
            return;
        }

        const unsubscribeKicked = onSocketEvent("kicked", (payload) => {
            setUser((prevUser) => {
                if (!prevUser?.user) {
                    return prevUser;
                }

                return {
                    ...prevUser,
                    user: {
                        ...prevUser.user,
                        kicked: payload.kicked,
                    },
                };
            });
        });

        const unsubscribeUserUpdate = onSocketEvent("user_update", (userPayload) => {
            setUser((prevUser) => {
                if (!prevUser || prevUser.isTeacher || !prevUser.user) {
                    return prevUser;
                }

                return {
                    ...prevUser,
                    user: userPayload,
                };
            });
        });

        return () => {
            unsubscribeKicked();
            unsubscribeUserUpdate();
        };
    }, [fetchUser]);

    const value: UserContextValue = useMemo(() => ({
        user,
        loading,
        error,
        refetch: fetchUser,
    }), [error, fetchUser, loading, user]);

    return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export const useUser = (): UserContextValue => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error("useUser must be used within UserProvider");
    }
    return context;
};
