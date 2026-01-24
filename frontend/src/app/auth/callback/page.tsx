"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import axios from "axios";
import { API_BASE_URL } from "@/lib/api";

function CallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        const token = searchParams.get("token");
        if (token) {
            // Save token
            localStorage.setItem("auth_token", token);

            // Fetch user data directly
            axios.get(`${API_BASE_URL}/auth/me`, {
                headers: { Authorization: `Bearer ${token}` }
            })
                .then(response => {
                    // Save user data
                    localStorage.setItem("auth_user", JSON.stringify(response.data));
                    // Hard redirect to ensure context reload
                    window.location.href = "/";
                })
                .catch(error => {
                    console.error("Failed to fetch user", error);
                    router.push("/login?error=auth_failed");
                });
        } else {
            router.push("/login?error=oauth_failed");
        }
    }, [searchParams, router]);

    return (
        <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">Completing authentication...</p>
        </div>
    );
}

export default function AuthCallbackPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <Suspense fallback={
                <div className="text-center">
                    <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-4" />
                    <p className="text-gray-600 font-medium">Loading...</p>
                </div>
            }>
                <CallbackContent />
            </Suspense>
        </div>
    );
}
