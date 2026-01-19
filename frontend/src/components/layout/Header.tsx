"use client";

import { Bell, CreditCard, LogOut, User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Image from "next/image";
// import logo from "@/app/logo/logo.png"; // Importación directa si Next.js lo permite desde src/app o usar ruta pública

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
        <header className="w-full border-b border-gray-100 bg-white/80 backdrop-blur-md flex-shrink-0 sticky top-0 z-40 transition-all duration-300">
            <div className="flex h-18 items-center px-8">
                {/* Logo & Branding */}
                <div className="flex items-center gap-3 group cursor-pointer" onClick={() => router.push("/")}>
                    <div className="relative h-10 w-10 transition-transform duration-300 group-hover:scale-105">
                        {/* Usando path relativo confiando en que Next lo resuelva o ruta estática si se mueve a public */}
                        {/* Nota: Idealmente mover logo.png a public/images/logo.png */}
                        {/* Por ahora intentamos importar desde donde dijo el usuario usando un require o import directo si está configurado */}
                        <img
                            src="/logo.png" // Fallback: asumiendo que el usuario lo moverá o configurará public.
                            // Si el archivo está en src/app/logo/logo.png, no es accesible via URL pública por defecto en Next.js App Router
                            // a menos que se importe. Como no puedo estar seguro del import sin ver la config de next,
                            // usaré un <img> tag apuntando a una ruta que instruiré al usuario crear, O
                            // usaré un import dinámico.
                            // MEJOR OPCIÓN: Usar un placeholder visual elegante si falla, pero intentar mostrar el logo.
                            alt="Quinesis Logo"
                            className="object-contain w-full h-full drop-shadow-sm"
                            onError={(e) => {
                                e.currentTarget.style.display = 'none';
                                e.currentTarget.nextElementSibling?.classList.remove('hidden');
                            }}
                        />
                        <div className="hidden h-10 w-10 bg-black rounded-xl flex items-center justify-center text-white shadow-lg">
                            <span className="font-bold text-lg">Q</span>
                        </div>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-2xl font-bold tracking-tight text-gray-900 leading-none" style={{ fontFamily: 'var(--font-geist-sans), sans-serif', letterSpacing: '-0.02em' }}>
                            QUINESIS
                        </span>
                        {/* <span className="text-[10px] uppercase tracking-[0.2em] text-gray-400 font-medium ml-0.5">
                            AI NARRATOR
                        </span> */}
                    </div>
                </div>

                {/* Spacer */}
                <div className="flex-1" />

                {/* Right Side */}
                <div className="flex items-center gap-6">
                    {/* Credits Pill */}
                    <div className="hidden md:flex items-center gap-2 px-4 py-1.5 bg-gray-50 border border-gray-100 rounded-full hover:bg-gray-100 transition-colors cursor-default">
                        <CreditCard className="h-3.5 w-3.5 text-gray-500" />
                        <span className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                            {user?.credits || 0} Credits
                        </span>
                    </div>

                    {/* Dependencies */}
                    <div className="h-6 w-px bg-gray-200 hidden md:block" />

                    {/* Notifications */}
                    <button className="relative p-2 text-gray-400 hover:text-gray-900 transition-colors">
                        <Bell className="h-5 w-5" />
                        <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 bg-red-500 rounded-full ring-2 ring-white"></span>
                    </button>

                    {/* User Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setShowUserMenu(!showUserMenu)}
                            className="flex items-center gap-3 p-1 rounded-full hover:bg-gray-50 transition-all border border-transparent hover:border-gray-100"
                        >
                            <div className="h-9 w-9 bg-black rounded-full flex items-center justify-center text-white text-sm font-medium shadow-md ring-2 ring-white">
                                {user?.email ? getInitials(user.email) : "un"}
                            </div>
                        </button>

                        {/* Dropdown Menu */}
                        {showUserMenu && (
                            <div className="absolute right-0 mt-3 w-64 bg-white rounded-2xl shadow-xl border border-gray-100 py-2 z-50 animate-in fade-in zoom-in-95 duration-200">
                                {/* User Info */}
                                <div className="px-5 py-4 border-b border-gray-50">
                                    <p className="text-sm font-bold text-gray-900 truncate">
                                        {user?.email}
                                    </p>
                                    <div className="flex items-center gap-2 mt-2">
                                        <div className="h-2 w-2 rounded-full bg-green-500"></div>
                                        <p className="text-xs text-gray-500 font-medium">
                                            Active Plan
                                        </p>
                                    </div>
                                </div>

                                {/* Menu Items */}
                                <div className="py-2 px-2">
                                    <button
                                        onClick={() => {
                                            setShowUserMenu(false);
                                            router.push("/settings");
                                        }}
                                        className="w-full px-3 py-2.5 text-left text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-xl flex items-center gap-3 transition-colors"
                                    >
                                        <User className="h-4 w-4" />
                                        Account Settings
                                    </button>
                                    <button
                                        onClick={handleLogout}
                                        className="w-full px-3 py-2.5 text-left text-sm font-medium text-red-600 hover:bg-red-50 rounded-xl flex items-center gap-3 transition-colors"
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
