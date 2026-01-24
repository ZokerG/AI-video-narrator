"use client";

import { Sparkles, Type } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

interface StoryConceptInputProps {
    onGenerate: (topic: string, style: string) => void;
    isGenerating: boolean;
}

export function StoryConceptInput({ onGenerate, isGenerating }: StoryConceptInputProps) {
    const [topic, setTopic] = useState("");
    const [style, setStyle] = useState("curious");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (topic.trim()) {
            onGenerate(topic, style);
        }
    };

    return (
        <div className="w-full max-w-xl mx-auto">
            <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-sm p-8">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mx-auto flex items-center justify-center mb-4 shadow-lg transform -rotate-6">
                        <Sparkles className="h-8 w-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">What's your story?</h2>
                    <p className="text-gray-600 mt-2">
                        Enter a topic and let AI write a viral script for you.
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-semibold text-gray-900 mb-2">
                            Topic or Idea
                        </label>
                        <div className="relative">
                            <input
                                type="text"
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="e.g. Mind-blowing facts about space, History of coffee..."
                                className="w-full h-12 pl-12 pr-4 bg-gray-50 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-gray-900 font-medium placeholder:text-gray-400"
                                required
                            />
                            <Type className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-gray-900 mb-4">
                            Vibe / Style
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            {[
                                { id: "curious", label: "🤔 Curious", desc: "Did you know?" },
                                { id: "horror", label: "👻 Horror", desc: "Spooky facts" },
                                { id: "motivational", label: "💪 Motivational", desc: "Inspiring quotes" },
                                { id: "funny", label: "😂 Funny", desc: "Jokes & skits" },
                            ].map((s) => (
                                <button
                                    key={s.id}
                                    type="button"
                                    onClick={() => setStyle(s.id)}
                                    className={`p-4 rounded-xl border-2 text-left transition-all ${style === s.id
                                        ? "border-indigo-600 bg-indigo-50"
                                        : "border-gray-200 hover:border-indigo-200 hover:bg-gray-50"
                                        }`}
                                >
                                    <div className={`font-bold ${style === s.id ? "text-indigo-700" : "text-gray-900"}`}>
                                        {s.label}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">{s.desc}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    <Button
                        type="submit"
                        disabled={isGenerating || !topic.trim()}
                        className="w-full h-14 text-lg font-bold bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isGenerating ? (
                            <div className="flex items-center gap-2">
                                <div className="animate-spin h-5 w-5 border-3 border-white border-t-transparent rounded-full" />
                                Writing Script...
                            </div>
                        ) : (
                            "Generate Script"
                        )}
                    </Button>
                </form>
            </div>
        </div>
    );
}
