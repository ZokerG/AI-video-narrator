"use client";

import { Bell, CreditCard, LogOut, User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function Header() {
    const { user, logout } = useAuth();
    const router = useRouter();
    const [showUserMenu, setShowUserMenu] = useState(false);

    const handleLogout = () => {
        logout();
        router.push("/login");
    };

    // Get user initials
    const getInitials = (email: string) => {
        return email
            .split("@")[0]
            .substring(0, 2)
            .toUpperCase();
    };

    return (
        <header className="w-full border-b border-gray-200 bg-white flex-shrink-0">
            <div className="flex h-16 items-center px-6">
                {/* Logo */}
                <div className="flex items-center gap-2 font-bold text-xl">
                    <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center text-white">
                        🎬
                    </div>
                    <span className="text-gray-900">AI Video Narrator</span>
                </div>

                {/* Spacer */}
                <div className="flex-1" />

                {/* Right Side */}
                <div className="flex items-center gap-4">
                    {/* Credits */}
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
                        <CreditCard className="h-4 w-4 text-gray-600" />
                        <span className="text-sm font-medium text-gray-900">
                            {user?.credits || 0} Credits
                        </span>
                    </div>

                    {/* Notifications */}
                    <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
                        <Bell className="h-5 w-5 text-gray-600" />
                        <span className="absolute top-1 right-1 h-2 w-2 bg-primary-600 rounded-full"></span>
                    </button>

                    {/* User Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setShowUserMenu(!showUserMenu)}
                            className="flex items-center gap-2 p-1 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            <div className="h-8 w-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                                {user?.email ? getInitials(user.email) : "??"}
                            </div>
                        </button>

                        {/* Dropdown Menu */}
                        {showUserMenu && (
                            <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border-2 border-gray-200 py-2 z-50">
                                {/* User Info */}
                                <div className="px-4 py-3 border-b border-gray-100">
                                    <p className="text-sm font-semibold text-gray-900">
                                        {user?.email}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">
                                        {user?.credits} credits remaining
                                    </p>
                                </div>

                                {/* Menu Items */}
                                <div className="py-1">
                                    <button
                                        onClick={() => {
                                            setShowUserMenu(false);
                                            router.push("/settings");
                                        }}
                                        className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
                                    >
                                        <User className="h-4 w-4" />
                                        Account Settings
                                    </button>
                                    <button
                                        onClick={handleLogout}
                                        className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-3"
                                    >
                                        <LogOut className="h-4 w-4" />
                                        Sign Out
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}
