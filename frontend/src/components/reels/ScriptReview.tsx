"use client";

import { Check, Edit2, Clock, Image as ImageIcon } from "lucide-react";

interface Scene {
    id: number;
    narration: string;
    visual_query: string;
    duration_estimate: number;
}

interface ScriptReviewProps {
    script: {
        title: string;
        estimated_duration: number;
        scenes: Scene[];
    };
    onConfirm: () => void;
    onBack: () => void;
}

export function ScriptReview({ script, onConfirm, onBack }: ScriptReviewProps) {
    return (
        <div className="w-full max-w-2xl mx-auto space-y-6">
            <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-sm overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 border-b border-gray-200">
                    <h3 className="text-xl font-bold text-gray-900 flex items-center justify-between">
                        {script.title || "Generated Script"}
                        <span className="text-sm font-medium px-3 py-1 bg-white rounded-full border border-gray-200 text-gray-600 flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            ~{script.estimated_duration}s
                        </span>
                    </h3>
                </div>

                <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
                    {script.scenes.map((scene, index) => (
                        <div key={index} className="flex gap-4 p-4 rounded-xl bg-gray-50 border border-gray-200 group hover:border-indigo-200 transition-colors">
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                                {index + 1}
                            </div>
                            <div className="flex-1 space-y-3">
                                <div>
                                    <div className="text-xs font-semibold uppercase tracking-wider text-indigo-600 mb-1">Narration</div>
                                    <p className="text-gray-800 font-medium leading-relaxed">
                                        "{scene.narration}"
                                    </p>
                                </div>
                                <div>
                                    <div className="text-xs font-semibold uppercase tracking-wider text-purple-600 mb-1 flex items-center gap-1">
                                        <ImageIcon className="h-3 w-3" /> Visual Idea
                                    </div>
                                    <p className="text-sm text-gray-600 italic">
                                        {scene.visual_query}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="p-6 bg-gray-50 border-t border-gray-200 flex gap-4">
                    <button
                        onClick={onBack}
                        className="flex-1 px-6 py-3 text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-xl font-bold transition-colors"
                    >
                        Try Again
                    </button>
                    <button
                        onClick={onConfirm}
                        className="flex-2 w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold transition-colors shadow-md hover:shadow-lg flex items-center justify-center gap-2"
                    >
                        <Check className="h-5 w-5" />
                        Looks Good, Let's Make It!
                    </button>
                </div>
            </div>
        </div>
    );
}
