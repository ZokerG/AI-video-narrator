"use client";

import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface DashboardLayoutProps {
    children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
    return (
        <div className="h-screen flex flex-col overflow-hidden bg-gray-50">
            {/* Fixed Header */}
            <Header />

            {/* Main Content Area with Sidebar */}
            <div className="flex flex-1 overflow-hidden">
                {/* Fixed Sidebar */}
                <Sidebar />

                {/* Scrollable Main Content */}
                <main className="flex-1 overflow-y-auto p-8">
                    {children}
                </main>
            </div>
        </div>
    );
}
