"use client";

import { Volume2, Sparkles, Gauge, Zap, BookOpen, Smile } from "lucide-react";

interface AudioConfig {
    style: "viral" | "documentary" | "funny";
    pace: "fast" | "medium" | "slow";
    originalVolume: number;
}

interface AudioSettingsProps {
    config: AudioConfig;
    onChange: (config: AudioConfig) => void;
    onGenerate: () => void;
    onBack: () => void;
    isProcessing: boolean;
}

export function AudioSettings({
    config,
    onChange,
    onGenerate,
    onBack,
    isProcessing,
}: AudioSettingsProps) {
    const updateConfig = (key: keyof AudioConfig, value: string | number) => {
        onChange({ ...config, [key]: value });
    };

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Audio & Narrative Style
                </h2>
                <p className="text-gray-600">
                    Configure how the narration will be delivered
                </p>
            </div>

            {/* Original Audio Volume Control */}
            <div className="bg-gradient-to-br from-gray-50 to-gray-100/50 rounded-xl p-6 border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-white shadow-sm flex items-center justify-center">
                            <Volume2 className="h-5 w-5 text-gray-700" />
                        </div>
                        <div>
                            <p className="font-semibold text-gray-900">Original Audio Volume</p>
                            <p className="text-xs text-gray-600">Background audio level</p>
                        </div>
                    </div>
                    <span className="text-lg font-bold text-primary-600 bg-white px-4 py-2 rounded-lg shadow-sm">
                        {config.originalVolume}%
                    </span>
                </div>

                <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.originalVolume}
                    onChange={(e) => updateConfig("originalVolume", parseInt(e.target.value))}
                    className="w-full h-3 bg-gray-300 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-600 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:border-4 [&::-webkit-slider-thumb]:border-white"
                    style={{
                        background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${config.originalVolume}%, #d1d5db ${config.originalVolume}%, #d1d5db 100%)`
                    }}
                />

                <div className="mt-4 p-3 bg-white rounded-lg border border-gray-200">
                    <p className="text-sm text-gray-700">
                        {config.originalVolume === 0
                            ? "🔇 Original audio muted (Voice only)"
                            : config.originalVolume < 30
                                ? "🔉 Quiet background (Voice focused)"
                                : config.originalVolume < 70
                                    ? "🔊 Balanced mix"
                                    : "📢 Prominent background audio"}
                    </p>
                </div>
            </div>

            {/* Narrative Style */}
            <div>
                <label className="block text-sm font-semibold text-gray-900 mb-4">
                    Narrative Style
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        {
                            value: "viral",
                            label: "Viral",
                            desc: "Energetic & immersive",
                            icon: Zap,
                            gradient: "from-orange-50 to-red-50",
                            border: "border-orange-200",
                            active: "border-orange-500 bg-orange-50"
                        },
                        {
                            value: "documentary",
                            label: "Documentary",
                            desc: "Professional & informative",
                            icon: BookOpen,
                            gradient: "from-blue-50 to-indigo-50",
                            border: "border-blue-200",
                            active: "border-blue-500 bg-blue-50"
                        },
                        {
                            value: "funny",
                            label: "Funny",
                            desc: "Humorous & playful",
                            icon: Smile,
                            gradient: "from-purple-50 to-pink-50",
                            border: "border-purple-200",
                            active: "border-purple-500 bg-purple-50"
                        },
                    ].map((style) => {
                        const Icon = style.icon;
                        const isActive = config.style === style.value;

                        return (
                            <button
                                key={style.value}
                                onClick={() => updateConfig("style", style.value)}
                                className={`p-5 rounded-xl border-2 transition-all ${isActive
                                        ? style.active
                                        : `${style.border} bg-white hover:${style.gradient}`
                                    }`}
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isActive ? "bg-white shadow-sm" : "bg-gray-50"
                                        }`}>
                                        <Icon className={`h-5 w-5 ${isActive ? "text-gray-900" : "text-gray-600"}`} />
                                    </div>
                                    {isActive && (
                                        <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                                    )}
                                </div>
                                <p className="font-semibold text-gray-900 text-left mb-1">{style.label}</p>
                                <p className="text-sm text-gray-600 text-left">{style.desc}</p>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Pace */}
            <div>
                <label className="block text-sm font-semibold text-gray-900 mb-4">
                    Narration Pace
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { value: "fast", label: "Fast", desc: "Quick cuts, 2-5s", emoji: "⚡" },
                        { value: "medium", label: "Medium", desc: "Balanced, 5-10s", emoji: "⏱️" },
                        { value: "slow", label: "Slow", desc: "Relaxed, 10-20s", emoji: "🌊" },
                    ].map((pace) => {
                        const isActive = config.pace === pace.value;

                        return (
                            <button
                                key={pace.value}
                                onClick={() => updateConfig("pace", pace.value)}
                                className={`p-5 rounded-xl border-2 transition-all ${isActive
                                        ? "border-primary-500 bg-primary-50 shadow-sm"
                                        : "border-gray-200 bg-white hover:border-gray-300"
                                    }`}
                            >
                                <div className="text-3xl mb-2">{pace.emoji}</div>
                                <p className="font-semibold text-gray-900 text-left mb-1">{pace.label}</p>
                                <p className="text-sm text-gray-600 text-left">{pace.desc}</p>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between pt-8 border-t border-gray-100">
                <button
                    onClick={onBack}
                    disabled={isProcessing}
                    className="px-6 py-3 text-gray-700 font-semibold hover:bg-gray-100 rounded-xl transition-colors disabled:opacity-50"
                >
                    ← Back
                </button>
                <button
                    onClick={onGenerate}
                    disabled={isProcessing}
                    className="px-8 py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-xl transition-all shadow-md hover:shadow-xl disabled:opacity-50 flex items-center gap-2"
                >
                    {isProcessing ? (
                        <>
                            <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                            <span className="text-white">Generating...</span>
                        </>
                    ) : (
                        <>
                            <Sparkles className="h-5 w-5 text-white" />
                            <span className="text-white">Generate Video</span>
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
