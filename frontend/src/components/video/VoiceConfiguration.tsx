"use client";

import { Mic, Volume2, Gauge, Play } from "lucide-react";

interface VoiceConfig {
    voiceId: string;
    stability: number;
    similarityBoost: number;
    speed: number;
}

interface VoiceConfigurationProps {
    config: VoiceConfig;
    onChange: (config: VoiceConfig) => void;
    onNext: () => void;
    onBack: () => void;
}

const voices = [
    { id: "JBFqnCBsd6RMkjVDRZzb", name: "George", desc: "Warm British", gender: "Male" },
    { id: "21m00Tcm4TlvDq8ikWAM", name: "Rachel", desc: "Young American", gender: "Female" },
    { id: "CYw3kZ02Hs0563khs1Fj", name: "James", desc: "Professional", gender: "Male" },
];

export function VoiceConfiguration({
    config,
    onChange,
    onNext,
    onBack,
}: VoiceConfigurationProps) {
    const updateConfig = (key: keyof VoiceConfig, value: number | string) => {
        onChange({ ...config, [key]: value });
    };

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Voice Configuration
                </h2>
                <p className="text-gray-600">
                    Customize the AI voice to match your content style
                </p>
            </div>

            {/* Voice Selector */}
            <div>
                <label className="block text-sm font-semibold text-gray-900 mb-4">
                    Select Voice
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {voices.map((voice) => {
                        const isSelected = config.voiceId === voice.id;

                        return (
                            <div
                                key={voice.id}
                                onClick={() => updateConfig("voiceId", voice.id)}
                                className={`relative p-6 rounded-xl border-2 transition-all text-left cursor-pointer ${isSelected
                                    ? "border-primary-600 bg-primary-50 shadow-lg ring-2 ring-primary-200"
                                    : "border-gray-200 hover:border-gray-300 bg-white hover:shadow-md"
                                    }`}
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isSelected ? "bg-primary-600 shadow-md" : "bg-gray-100"
                                        }`}>
                                        <Mic className={`h-6 w-6 ${isSelected ? "text-white" : "text-gray-600"
                                            }`} />
                                    </div>
                                    {isSelected && (
                                        <div className="w-3 h-3 bg-primary-600 rounded-full ring-2 ring-white"></div>
                                    )}
                                </div>

                                <p className="font-bold text-gray-900 mb-1 text-base">{voice.name}</p>
                                <p className="text-sm text-gray-600 mb-1">{voice.desc}</p>
                                <p className="text-xs text-gray-500">{voice.gender}</p>

                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        // TODO: Play preview
                                    }}
                                    className={`mt-4 text-xs font-semibold flex items-center gap-1.5 ${isSelected ? "text-primary-700" : "text-primary-600"
                                        } hover:underline`}
                                >
                                    <Play className="h-3.5 w-3.5" />
                                    Preview Voice
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Voice Settings Sliders */}
            <div className="space-y-8 pt-8 border-t border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900">Fine-tune Settings</h3>

                {/* Stability Slider */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center">
                                <Gauge className="h-5 w-5 text-gray-700" />
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-900">Stability</p>
                                <p className="text-xs text-gray-600">Voice consistency</p>
                            </div>
                        </div>
                        <span className="text-base font-bold text-gray-900 bg-gray-100 px-4 py-2 rounded-lg min-w-[60px] text-center">
                            {config.stability}%
                        </span>
                    </div>
                    <div className="relative pt-1">
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={config.stability}
                            onChange={(e) => updateConfig("stability", parseInt(e.target.value))}
                            className="w-full h-3 bg-gray-200 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-600 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:border-4 [&::-webkit-slider-thumb]:border-white"
                            style={{
                                background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${config.stability}%, #e5e7eb ${config.stability}%, #e5e7eb 100%)`
                            }}
                        />
                    </div>
                    <div className="flex justify-between text-xs font-medium text-gray-600">
                        <span>Expressive</span>
                        <span>Consistent</span>
                    </div>
                </div>

                {/* Clarity Slider */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center">
                                <Volume2 className="h-5 w-5 text-gray-700" />
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-900">Clarity</p>
                                <p className="text-xs text-gray-600">Voice definition</p>
                            </div>
                        </div>
                        <span className="text-base font-bold text-gray-900 bg-gray-100 px-4 py-2 rounded-lg min-w-[60px] text-center">
                            {config.similarityBoost}%
                        </span>
                    </div>
                    <div className="relative pt-1">
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={config.similarityBoost}
                            onChange={(e) => updateConfig("similarityBoost", parseInt(e.target.value))}
                            className="w-full h-3 bg-gray-200 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-600 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:border-4 [&::-webkit-slider-thumb]:border-white"
                            style={{
                                background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${config.similarityBoost}%, #e5e7eb ${config.similarityBoost}%, #e5e7eb 100%)`
                            }}
                        />
                    </div>
                    <div className="flex justify-between text-xs font-medium text-gray-600">
                        <span>Softer</span>
                        <span>Crisper</span>
                    </div>
                </div>

                {/* Speed Slider */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center">
                                <Mic className="h-5 w-5 text-gray-700" />
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-900">Speed</p>
                                <p className="text-xs text-gray-600">Speaking rate</p>
                            </div>
                        </div>
                        <span className="text-base font-bold text-gray-900 bg-gray-100 px-4 py-2 rounded-lg min-w-[60px] text-center">
                            {(config.speed / 100).toFixed(1)}x
                        </span>
                    </div>
                    <div className="relative pt-1">
                        <input
                            type="range"
                            min="70"
                            max="120"
                            value={config.speed}
                            onChange={(e) => updateConfig("speed", parseInt(e.target.value))}
                            className="w-full h-3 bg-gray-200 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-600 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:border-4 [&::-webkit-slider-thumb]:border-white"
                            style={{
                                background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(config.speed - 70) * 2}%, #e5e7eb ${(config.speed - 70) * 2}%, #e5e7eb 100%)`
                            }}
                        />
                    </div>
                    <div className="flex justify-between text-xs font-medium text-gray-600">
                        <span>0.7x Slower</span>
                        <span>1.2x Faster</span>
                    </div>
                </div>
            </div>

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between pt-8 border-t border-gray-100">
                <button
                    onClick={onBack}
                    className="px-6 py-3 text-gray-700 hover:bg-gray-100 rounded-xl font-semibold transition-colors"
                >
                    ← Back
                </button>
                <button
                    onClick={onNext}
                    className="px-8 py-3.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold transition-all shadow-md hover:shadow-lg"
                >
                    Continue →
                </button>
            </div>
        </div>
    );
}
