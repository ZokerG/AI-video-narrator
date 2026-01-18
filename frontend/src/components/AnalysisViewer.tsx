"use client";

import React, { useState, useRef, useEffect } from "react";
import { type AnalysisResponse, api } from "@/lib/api";
import { Play, Pause, RefreshCw, Volume2, Film } from "lucide-react";
import { Button } from "./ui/button";
import { motion } from "framer-motion";

interface AnalysisViewerProps {
    data: AnalysisResponse;
    onReset: () => void;
}

export function AnalysisViewer({ data, onReset }: AnalysisViewerProps) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [currentBeatId, setCurrentBeatId] = useState<number | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const videoUrl = api.getVideoUrl(data.output_video);

    // Update current time and active beat as video plays
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const handleTimeUpdate = () => {
            const time = video.currentTime;
            setCurrentTime(time);

            // Find which beat is currently active
            const activeBeat = data.analysis.beats.find(
                (beat) => time >= beat.start_s && time <= beat.end_s
            );
            setCurrentBeatId(activeBeat?.id ?? null);
        };

        video.addEventListener("timeupdate", handleTimeUpdate);
        return () => video.removeEventListener("timeupdate", handleTimeUpdate);
    }, [data.analysis.beats]);

    const togglePlay = () => {
        if (videoRef.current) {
            if (isPlaying) {
                videoRef.current.pause();
            } else {
                videoRef.current.play();
            }
            setIsPlaying(!isPlaying);
        }
    };

    const jumpToBeat = (beat: any) => {
        if (videoRef.current) {
            videoRef.current.currentTime = beat.start_s;
            videoRef.current.play();
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-8 w-full max-w-6xl mx-auto"
        >
            {/* Video Player Column */}
            <div className="lg:col-span-2 space-y-6">
                <div className="relative aspect-[9/16] bg-black rounded-3xl overflow-hidden shadow-2xl border border-zinc-800 mx-auto max-w-sm lg:max-w-md">
                    <video
                        ref={videoRef}
                        src={videoUrl}
                        className="w-full h-full object-cover"
                        onPlay={() => setIsPlaying(true)}
                        onPause={() => setIsPlaying(false)}
                        controls
                    />
                    {/* Custom overlay controls could go here for a more premium feel, but native controls are safer for MVP */}
                </div>

                <div className="flex justify-center gap-4">
                    <Button onClick={togglePlay} variant="outline" className="rounded-full w-12 h-12 p-0">
                        {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
                    </Button>
                    <Button onClick={onReset} variant="ghost" className="rounded-full w-12 h-12 p-0">
                        <RefreshCw className="h-5 w-5" />
                    </Button>
                </div>
            </div>

            {/* Analysis/Beats Column */}
            <div className="space-y-6 max-h-[80vh] overflow-y-auto pr-2 custom-scrollbar">
                <div className="bg-zinc-900/50 backdrop-blur border border-zinc-800 rounded-3xl p-6">
                    <h2 className="text-xl font-bold text-white mb-2">{data.analysis.overall?.hook || "Generando gancho..."}</h2>
                    <p className="text-zinc-400 text-sm mb-4">{data.analysis.overall?.one_sentence_summary || "Analizando el contenido del video..."}</p>
                    <div className="flex gap-2 mb-4">
                        <span className="px-3 py-1 bg-blue-500/10 text-blue-400 text-xs rounded-full border border-blue-500/20 font-medium uppercase tracking-wider">
                            {data.analysis.overall?.tone || "Neutro"}
                        </span>
                        <span className="px-3 py-1 bg-zinc-800 text-zinc-400 text-xs rounded-full border border-zinc-700 font-medium uppercase tracking-wider">
                            {data.analysis.language}
                        </span>
                        <span className="px-3 py-1 bg-zinc-800 text-zinc-400 text-xs rounded-full border border-zinc-700 font-medium">
                            {data.analysis.beats.length} beats
                        </span>
                    </div>
                </div>

                <h3 className="text-lg font-semibold text-white px-2">Narrative Beats</h3>
                <div className="space-y-4">
                    {data.analysis.beats.map((beat) => {
                        const isActive = beat.id === currentBeatId;
                        return (
                            <motion.div
                                key={beat.id}
                                animate={isActive ? { scale: 1.02 } : { scale: 1 }}
                                transition={{ duration: 0.2 }}
                                className={`bg-zinc-900 border rounded-2xl p-4 transition-all cursor-pointer ${isActive
                                        ? "border-blue-500 shadow-lg shadow-blue-500/20"
                                        : "border-zinc-800 hover:border-zinc-700"
                                    }`}
                                onClick={() => jumpToBeat(beat)}
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <span className={`text-xs font-mono px-2 py-1 rounded ${isActive
                                            ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                                            : "bg-zinc-950 text-zinc-500"
                                        }`}>
                                        {beat.start_s.toFixed(1)}s - {beat.end_s.toFixed(1)}s
                                    </span>
                                    {isActive && (
                                        <span className="flex items-center gap-1 text-xs text-blue-400 animate-pulse">
                                            <span className="h-2 w-2 bg-blue-400 rounded-full"></span>
                                            Playing
                                        </span>
                                    )}
                                </div>

                                {/* Voiceover Script - Main Narration */}
                                {beat.voiceover?.script && (
                                    <div className="mb-3">
                                        <p className={`font-medium text-base leading-relaxed ${isActive ? "text-white" : "text-zinc-300"
                                            }`}>
                                            🎙️ "{beat.voiceover.script}"
                                        </p>
                                    </div>
                                )}

                                {/* Visual Summary */}
                                {beat.visual_summary && (
                                    <p className="text-zinc-500 text-sm italic border-l-2 border-zinc-800 pl-3 mb-2">
                                        👁️ {beat.visual_summary}
                                    </p>
                                )}

                                {/* Key Visuals Tags */}
                                {beat.key_visuals && beat.key_visuals.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mt-3">
                                        {beat.key_visuals.map((tag, i) => (
                                            <span key={i} className="text-xs text-zinc-400 bg-zinc-800/50 px-2 py-1 rounded-md">
                                                #{tag}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </motion.div>
    );
}

