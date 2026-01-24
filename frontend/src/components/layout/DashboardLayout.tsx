"use client";

import { useState } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface DashboardLayoutProps {
    children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="h-screen flex flex-col overflow-hidden bg-gray-50">
            {/* Fixed Header */}
            <Header onMenuClick={() => setSidebarOpen(true)} />

            {/* Main Content Area with Sidebar */}
            <div className="flex flex-1 overflow-hidden relative">
                {/* Responsive Sidebar */}
                <Sidebar
                    isOpen={sidebarOpen}
                    onClose={() => setSidebarOpen(false)}
                />

                {/* Scrollable Main Content */}
                <main className="flex-1 overflow-y-auto p-4 md:p-8 w-full">
                    {children}
                </main>
            </div>
        </div>
    );
}
