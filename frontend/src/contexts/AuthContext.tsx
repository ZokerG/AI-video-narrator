"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

interface User {
    id: number;
    email: string;
    credits: number;
    created_at: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
    error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = "http://localhost:8000";

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Load token and user from localStorage on mount
    useEffect(() => {
        const storedToken = localStorage.getItem("auth_token");
        const storedUser = localStorage.getItem("auth_user");

        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        }
        setIsLoading(false);
    }, []);

    const login = async (email: string, password: string) => {
        try {
            setError(null);
            setIsLoading(true);

            const response = await axios.post(`${API_URL}/auth/login`, {
                email,
                password,
            });

            const { access_token, user: userData } = response.data;

            // Store in localStorage
            localStorage.setItem("auth_token", access_token);
            localStorage.setItem("auth_user", JSON.stringify(userData));

            setToken(access_token);
            setUser(userData);
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

            const { access_token, user: userData } = response.data;

            // Store in localStorage
            localStorage.setItem("auth_token", access_token);
            localStorage.setItem("auth_user", JSON.stringify(userData));

            setToken(access_token);
            setUser(userData);
        } catch (err: any) {
            const message = err.response?.data?.detail || "Registration failed";
            setError(message);
            throw new Error(message);
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{ user, token, login, register, logout, isLoading, error }}
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
