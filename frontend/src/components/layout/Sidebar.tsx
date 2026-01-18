"use client";

import { Home, Plus, FolderOpen, Settings, Mic, CreditCard, HelpCircle } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navigation = [
    { name: "Dashboard", href: "/", icon: Home },
    { name: "New Video", href: "/new", icon: Plus },
    { name: "My Videos", href: "/videos", icon: FolderOpen },
    { name: "Voices", href: "/voices", icon: Mic },
    { name: "Settings", href: "/settings", icon: Settings },
    { name: "Billing", href: "/billing", icon: CreditCard },
    { name: "Help", href: "/help", icon: HelpCircle },
];

export function Sidebar() {
    const pathname = usePathname();

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
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600 font-medium">Usage</span>
                        <span className="text-gray-900 font-semibold">45% of plan</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div
                            className="bg-primary-600 h-2.5 rounded-full transition-all"
                            style={{ width: "45%" }}
                        ></div>
                    </div>
                </div>
            </div>
        </aside>
    );
}
