"use client";

import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";

interface User {
    id: number;
    email: string;
    credits: number;
    plan?: string;
    created_at: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string) => Promise<void>;
    logout: () => void;
    refreshUser: () => Promise<void>;
    isLoading: boolean;
    error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

import { API_BASE_URL } from "@/lib/api";

const API_URL = API_BASE_URL;

// Token refresh before expiration (refresh 2 min before expiry)
const REFRESH_BEFORE_EXPIRY_MS = 2 * 60 * 1000;

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const refreshTimerRef = useRef<NodeJS.Timeout | null>(null);

    // Store tokens in localStorage
    const saveTokens = (accessToken: string, refreshToken: string, expiresIn: number) => {
        localStorage.setItem("auth_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);
        // Store expiry time (current time + expires_in seconds)
        const expiryTime = Date.now() + expiresIn * 1000;
        localStorage.setItem("token_expiry", expiryTime.toString());
    };

    // Refresh tokens using refresh token
    const refreshTokens = useCallback(async () => {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
            logout();
            return false;
        }

        try {
            console.log("[Auth] Refreshing tokens...");
            const response = await axios.post(`${API_URL}/auth/refresh`, {
                refresh_token: refreshToken
            });

            const { access_token, refresh_token: newRefreshToken, expires_in } = response.data;

            saveTokens(access_token, newRefreshToken, expires_in);
            setToken(access_token);

            // Schedule next refresh
            scheduleTokenRefresh(expires_in);

            console.log("[Auth] ✅ Tokens refreshed successfully");
            return true;
        } catch (err) {
            console.error("[Auth] ❌ Token refresh failed, logging out");
            logout();
            return false;
        }
    }, []);

    // Schedule automatic refresh before token expires
    const scheduleTokenRefresh = useCallback((expiresInSeconds: number) => {
        // Clear any existing timer
        if (refreshTimerRef.current) {
            clearTimeout(refreshTimerRef.current);
        }

        // Calculate when to refresh (2 min before expiry)
        const refreshTime = (expiresInSeconds * 1000) - REFRESH_BEFORE_EXPIRY_MS;

        if (refreshTime > 0) {
            console.log(`[Auth] Scheduling token refresh in ${Math.round(refreshTime / 1000)}s`);
            refreshTimerRef.current = setTimeout(() => {
                refreshTokens();
            }, refreshTime);
        }
    }, [refreshTokens]);

    // Load token and user from localStorage on mount
    useEffect(() => {
        const storedToken = localStorage.getItem("auth_token");
        const storedUser = localStorage.getItem("auth_user");
        const tokenExpiry = localStorage.getItem("token_expiry");

        if (storedToken && storedUser) {
            // Check if token is expired
            if (tokenExpiry && Date.now() > parseInt(tokenExpiry)) {
                // Token expired, try to refresh
                console.log("[Auth] Token expired, attempting refresh...");
                refreshTokens().then((success) => {
                    if (success) {
                        setUser(JSON.parse(storedUser));
                    }
                    setIsLoading(false);
                });
            } else if (tokenExpiry) {
                // Token still valid
                setToken(storedToken);
                setUser(JSON.parse(storedUser));

                // Schedule refresh based on remaining time
                const remainingMs = parseInt(tokenExpiry) - Date.now();
                scheduleTokenRefresh(remainingMs / 1000);
                setIsLoading(false);
            } else {
                // No expiry info, use token as-is
                setToken(storedToken);
                setUser(JSON.parse(storedUser));
                setIsLoading(false);
            }
        } else {
            setIsLoading(false);
        }

        // Cleanup timer on unmount
        return () => {
            if (refreshTimerRef.current) {
                clearTimeout(refreshTimerRef.current);
            }
        };
    }, [refreshTokens, scheduleTokenRefresh]);

    const refreshUser = async () => {
        if (!token) return;
        try {
            const response = await axios.get(`${API_URL}/auth/me`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUser(response.data);
            localStorage.setItem("auth_user", JSON.stringify(response.data));
        } catch (error) {
            console.error("Failed to refresh user data", error);
        }
    };

    const login = async (email: string, password: string) => {
        try {
            setError(null);
            setIsLoading(true);

            const response = await axios.post(`${API_URL}/auth/login`, {
                email,
                password,
            });

            const { access_token, refresh_token, expires_in, user: userData } = response.data;

            // Store tokens
            saveTokens(access_token, refresh_token, expires_in);
            localStorage.setItem("auth_user", JSON.stringify(userData));

            setToken(access_token);
            setUser(userData);

            // Schedule auto-refresh
            scheduleTokenRefresh(expires_in);
        } catch (err: any) {
            const message = err.response?.data?.detail || "Login failed";
            setError(message);
            throw new Error(message);
        } finally {
            setIsLoading(false);
        }
    };

    const register = async (email: string, password: string) => {
        try {
            setError(null);
            setIsLoading(true);

            const response = await axios.post(`${API_URL}/auth/register`, {
                email,
                password,
            });

            const { access_token, refresh_token, expires_in, user: userData } = response.data;

            // Store tokens
            saveTokens(access_token, refresh_token, expires_in);
            localStorage.setItem("auth_user", JSON.stringify(userData));

            setToken(access_token);
            setUser(userData);

            // Schedule auto-refresh
            scheduleTokenRefresh(expires_in);
        } catch (err: any) {
            const message = err.response?.data?.detail || "Registration failed";
            setError(message);
            throw new Error(message);
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        // Clear refresh timer
        if (refreshTimerRef.current) {
            clearTimeout(refreshTimerRef.current);
        }
        // Remove all auth data
        localStorage.removeItem("auth_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("token_expiry");
        localStorage.removeItem("auth_user");
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{ user, token, login, register, logout, refreshUser, isLoading, error }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
