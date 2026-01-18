"use client";

import { Home, Plus, FolderOpen, Settings, Mic, CreditCard, HelpCircle, Video } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navigation = [
    { name: "Dashboard", href: "/", icon: Home },
    { name: "New Video", href: "/new", icon: Plus },
    { name: "My Videos", href: "/videos", icon: Video },
    { name: "Voices", href: "/voices", icon: Mic },
    { name: "Settings", href: "/settings", icon: Settings },
    { name: "Billing", href: "/billing", icon: CreditCard },
    { name: "Help", href: "/help", icon: HelpCircle },
];

import { useAuth } from "@/contexts/AuthContext";

export function Sidebar() {
    const pathname = usePathname();
    const { user } = useAuth();

    return (
        <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all",
                                isActive
                                    ? "bg-primary-600 text-white shadow-md hover:bg-primary-700"
                                    : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                            )}
                        >
                            <Icon className="h-5 w-5 flex-shrink-0" />
                            <span>{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Usage Meter - Sticky at bottom */}
            <div className="p-4 border-t border-gray-200 bg-white">
                <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600 font-medium uppercase tracking-wider">
                            {user?.plan || "Free"} Plan
                        </span>
                        <span className="text-primary-700 font-bold bg-primary-50 px-2 py-0.5 rounded-md">
                            {user?.credits || 0} Credits
                        </span>
                    </div>

                    {/* Visual Meter (assuming 100 is base/max for now) */}
                    <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                            className="bg-gradient-to-r from-primary-500 to-primary-600 h-full rounded-full transition-all duration-500 ease-out"
                            style={{ width: `${Math.min((user?.credits || 0), 100)}%` }}
                        ></div>
                    </div>

                    <div className="text-xs text-center text-gray-500">
                        {user?.credits && user.credits < 20 ? (
                            <span className="text-red-500 font-medium">Low balance!</span>
                        ) : (
                            <span>{(user?.credits || 0) / 20} videos remaining</span>
                        )}
                    </div>
                </div>
            </div>
        </aside>
    );
}
