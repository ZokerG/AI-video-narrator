"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { SocialConnectionCard } from "@/components/social/ConnectionCard";
import { useAuth } from "@/contexts/AuthContext";
import axios from "axios";

// Configurar URL base si no está globalmente
const API_URL = "http://localhost:8000";

interface SocialAccount {
    id: number;
    platform: "facebook" | "instagram" | "tiktok";
    username: string;
    created_at: string;
}

export default function ConnectionsPage() {
    const { token, user } = useAuth();
    const [accounts, setAccounts] = useState<SocialAccount[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [actionLoading, setActionLoading] = useState<string | null>(null);

    // Fetch Connected Accounts
    useEffect(() => {
        if (!token) return;

        const fetchAccounts = async () => {
            try {
                const response = await axios.get(`${API_URL}/social/accounts`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setAccounts(response.data.accounts);
            } catch (error) {
                console.error("Error fetching social accounts:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchAccounts();
    }, [token]);

    const handleConnect = async (platform: string) => {
        if (!token) return;
        setActionLoading(platform);

        try {
            // Get OAuth URL from backend
            const response = await axios.get(`${API_URL}/auth/${platform}/login`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            const { url } = response.data;
            if (url) {
                // Redirect user to OAuth provider
                window.location.href = url;
            }
        } catch (error) {
            console.error(`Error initiating ${platform} connection:`, error);
            alert(`Failed to connect to ${platform}`);
            setActionLoading(null);
        }
    };

    const handleDisconnect = async (accountId: number) => {
        if (!token || !confirm("Are you sure you want to disconnect this account?")) return;

        try {
            // TODO: Implement disconnect endpoint in backend (it was in plan but not api.py yet)
            // For now just simulate filtering from UI or show alert
            alert("Disconnect endpoint not implemented yet in backend.");
        } catch (error) {
            console.error("Error disconnecting account:", error);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-5xl mx-auto space-y-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Connected Accounts</h1>
                    <p className="text-gray-500 mt-1">
                        Connect your social media profiles to automatically publish your AI-generated videos.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Facebook */}
                    <SocialConnectionCard
                        platform="facebook"
                        isConnected={accounts.some(a => a.platform === "facebook")}
                        username={accounts.find(a => a.platform === "facebook")?.username}
                        onConnect={() => handleConnect("facebook")}
                        onDisconnect={() => handleDisconnect(accounts.find(a => a.platform === "facebook")!.id)}
                        isLoading={actionLoading === "facebook" || loading}
                    />

                    {/* Instagram */}
                    <SocialConnectionCard
                        platform="instagram"
                        isConnected={accounts.some(a => a.platform === "instagram")}
                        username={accounts.find(a => a.platform === "instagram")?.username}
                        onConnect={() => handleConnect("instagram")}
                        onDisconnect={() => handleDisconnect(accounts.find(a => a.platform === "instagram")!.id)}
                        isLoading={actionLoading === "instagram" || loading}
                    />

                    {/* TikTok */}
                    <SocialConnectionCard
                        platform="tiktok"
                        isConnected={accounts.some(a => a.platform === "tiktok")}
                        username={accounts.find(a => a.platform === "tiktok")?.username}
                        onConnect={() => handleConnect("tiktok")}
                        onDisconnect={() => handleDisconnect(accounts.find(a => a.platform === "tiktok")!.id)}
                        isLoading={actionLoading === "tiktok" || loading}
                    />
                </div>

                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-800 flex gap-3 items-start">
                    <div className="mt-0.5">ℹ️</div>
                    <div>
                        <p className="font-semibold mb-1">About Permissions</p>
                        <p>
                            We only request the minimum permissions necessary to publish videos on your behalf.
                            We will never post anything without your explicit approval for each video.
                        </p>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
