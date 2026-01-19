"use client";

import { useState } from "react";
import { Loader2, CheckCircle, XCircle, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

interface SocialConnectionCardProps {
    platform: "facebook" | "instagram" | "tiktok";
    isConnected: boolean;
    username?: string;
    onConnect: () => void;
    onDisconnect: () => void;
    isLoading?: boolean;
}

const platforms = {
    facebook: {
        name: "Facebook",
        color: "bg-[#1877F2]",
        description: "Publica en Páginas de Facebook",
        icon: (className: string) => (
            <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M14 13.5h2.5l1-4H14v-2c0-1.03 0-2 2-2h1.5v-3.75c-0.25-0.03-1.12-0.109-2.125-0.109-2.1 0-3.54 1.28-3.54 3.635v2.245h-2.375v4h2.375v9.925h4v-9.925z" /></svg>
        )
    },
    instagram: {
        name: "Instagram",
        color: "bg-gradient-to-tr from-[#FFDC80] via-[#FD1D1D] to-[#833AB4]",
        description: "Publica Reels y Posts",
        icon: (className: string) => (
            <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584 0.012 4.85 0.070 3.252 0.148 4.771 1.691 4.919 4.919 0.058 1.265 0.069 1.645 0.069 4.849 0 3.205-0.012 3.584-0.069 4.849-0.149 3.225-1.664 4.771-4.919 4.919-1.266 0.058-1.644 0.070-4.85 0.070-3.204 0-3.584-0.012-4.849-0.070-3.26-0.149-4.771-1.699-4.919-4.92-0.058-1.265-0.070-1.644-0.070-4.849 0-3.204 0.013-3.583 0.070-4.849 0.149-3.227 1.664-4.771 4.919-4.919 1.266-0.057 1.645-0.069 4.849-0.069zM12 0c-3.262 0-3.67 0.014-4.949 0.072-4.358 0.2-6.78 2.618-6.98 6.98-0.059 1.278-0.073 1.687-0.073 4.948 0 3.261 0.014 3.668 0.072 4.948 0.2 4.358 2.618 6.78 6.98 6.98 1.281 0.058 1.689 0.072 4.948 0.072 3.259 0 3.668-0.014 4.948-0.072 4.354-0.2 6.782-2.618 6.979-6.98 0.059-1.28 0.073-1.687 0.073-4.948 0-3.259-0.014-3.667-0.072-4.948-0.197-4.354-2.617-6.78-6.979-6.98-1.281-0.059-1.69-0.072-4.949-0.072zM12 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zM12 16c-2.209 0-4-1.791-4-4s1.791-4 4-4 4 1.791 4 4-1.791 4-4 4zM18.406 4.155c-0.75 0-1.36 0.609-1.36 1.36 0 0.75 0.61 1.36 1.36 1.36 0.75 0 1.36-0.61 1.36-1.36 0-0.751-0.61-1.36-1.36-1.36z" /></svg>
        )
    },
    tiktok: {
        name: "TikTok",
        color: "bg-[#000000]",
        description: "Publica en tu perfil",
        icon: (className: string) => (
            <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M12.525 2.103c-0.108 1.91 0.65 3.655 1.786 5.011 0.941 1.121 2.376 1.83 3.966 1.83v2.75c-0.902-0.114-1.764-0.428-2.548-0.895-0.916-0.547-1.703-1.314-2.288-2.235v10.597c0 3.86-3.14 6.999-7 6.999-3.86 0-7-3.14-7-6.999 0-3.86 3.14-7 7-7 0.449 0 0.887 0.042 1.312 0.122v3.056c-0.4-0.117-0.824-0.18-1.263-0.18-2.318 0-4.197 1.879-4.197 4.197 0 2.318 1.879 4.197 4.197 4.197 2.318 0 4.197-1.879 4.197-4.197v-17.251h3.988z" /></svg>
        )
    }
};

export function SocialConnectionCard({
    platform,
    isConnected,
    username,
    onConnect,
    onDisconnect,
    isLoading
}: SocialConnectionCardProps) {
    const p = platforms[platform];

    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col h-full transition-all hover:shadow-md">
            {/* Header */}
            <div className={cn("h-2 w-full", p.color)}></div>

            <div className="p-6 flex flex-col flex-1">
                <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className={cn("p-2 rounded-lg text-white", p.color)}>
                            {p.icon("w-6 h-6")}
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-900">{p.name}</h3>
                            <p className="text-sm text-gray-500">{p.description}</p>
                        </div>
                    </div>
                    {isConnected && (
                        <div className="text-green-500 bg-green-50 p-1 rounded-full">
                            <CheckCircle className="w-5 h-5" />
                        </div>
                    )}
                </div>

                <div className="flex-1">
                    {isConnected ? (
                        <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700 mb-4 border border-gray-100 flex items-center gap-2">
                            <span className="font-medium">Connected as:</span>
                            <span className="text-black font-semibold truncate">{username || "Unknown"}</span>
                        </div>
                    ) : (
                        <p className="text-sm text-gray-500 mb-4">
                            Connect your account to automatically publish your videos.
                        </p>
                    )}
                </div>

                <button
                    onClick={isConnected ? onDisconnect : onConnect}
                    disabled={isLoading}
                    className={cn(
                        "w-full py-2.5 px-4 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition-colors",
                        isLoading && "opacity-70 cursor-not-allowed",
                        isConnected
                            ? "border border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-red-500 hover:border-red-200"
                            : "bg-black text-white hover:bg-gray-800"
                    )}
                >
                    {isLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : isConnected ? (
                        <>Disconnect</>
                    ) : (
                        <>Connect {p.name}</>
                    )}
                </button>
            </div>
        </div>
    );
}
