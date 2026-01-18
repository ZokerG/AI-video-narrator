"use client";

import React, { useState, useRef } from "react";
import { Upload, FileVideo, X, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";

interface VideoUploaderProps {
    onUpload: (file: File, options: { style: string; pace: string; keepAudio: boolean }) => void;
    isProcessing: boolean;
}

export function VideoUploader({ onUpload, isProcessing }: VideoUploaderProps) {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Customization State
    const [style, setStyle] = useState("viral");
    const [pace, setPace] = useState("fast");
    const [keepAudio, setKeepAudio] = useState(true);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file: File) => {
        if (file.type.startsWith("video/")) {
            setSelectedFile(file);
        } else {
            alert("Please upload a video file");
        }
    };

    const handleSubmit = () => {
        if (selectedFile) {
            onUpload(selectedFile);
        }
    };

    return (
        <div className="w-full max-w-xl mx-auto">
            <AnimatePresence mode="wait">
                {!selectedFile ? (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className={cn(
                            "relative group cursor-pointer border border-dashed rounded-2xl p-16 transition-all duration-300 text-center bg-zinc-900/50 backdrop-blur-sm",
                            dragActive
                                ? "border-white/40 bg-zinc-800/80 scale-[1.01]"
                                : "border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800/30"
                        )}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={() => inputRef.current?.click()}
                    >
                        <input
                            ref={inputRef}
                            className="hidden"
                            type="file"
                            accept="video/*"
                            onChange={handleChange}
                        />
                        <div className="flex flex-col items-center gap-4">
                            <div className="h-12 w-12 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-xl">
                                <Upload className="h-5 w-5 text-zinc-400 group-hover:text-white transition-colors" />
                            </div>
                            <div className="space-y-1">
                                <p className="text-sm font-medium text-zinc-200">
                                    Click to upload or drag and drop
                                </p>
                                <p className="text-xs text-zinc-500">
                                    MP4, MOV up to 50MB
                                </p>
                            </div>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-black/40 border border-zinc-800 rounded-2xl p-6 backdrop-blur-md"
                    >
                        <div className="flex items-center gap-4 mb-6">
                            <div className="h-10 w-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                                <FileVideo className="h-5 w-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-zinc-200 truncate">
                                    {selectedFile.name}
                                </p>
                                <p className="text-xs text-zinc-500">
                                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                                </p>
                            </div>
                            <button
                                onClick={() => setSelectedFile(null)}
                                className="p-2 hover:bg-zinc-800 rounded-full text-zinc-500 hover:text-white transition-colors"
                                disabled={isProcessing}
                            >
                                <X className="h-4 w-4" />
                            </button>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="space-y-2">
                                <label className="text-xs font-medium text-zinc-400">Narration Style</label>
                                <select
                                    value={style}
                                    onChange={(e) => setStyle(e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-700 text-white text-sm rounded-lg p-2.5 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="viral">Viral (TikTok/Reels)</option>
                                    <option value="documentary">Documentary (Formal)</option>
                                    <option value="funny">Funny (Sarcastic)</option>
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-medium text-zinc-400">Pace / Duration</label>
                                <select
                                    value={pace}
                                    onChange={(e) => setPace(e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-700 text-white text-sm rounded-lg p-2.5 focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="fast">Fast (2-5s beats)</option>
                                    <option value="medium">Medium (5-10s beats)</option>
                                    <option value="slow">Slow (10-20s beats)</option>
                                </select>
                            </div>
                        </div>

                        <div className="flex items-center mb-6">
                            <input
                                id="keep-audio"
                                type="checkbox"
                                checked={keepAudio}
                                onChange={(e) => setKeepAudio(e.target.checked)}
                                className="w-4 h-4 text-blue-600 bg-zinc-700 border-zinc-600 rounded focus:ring-blue-600 ring-offset-zinc-800"
                            />
                            <label htmlFor="keep-audio" className="ml-2 text-sm font-medium text-zinc-300">Keep Original Audio</label>
                        </div>

                        <Button
                            className="w-full h-11 text-sm bg-white text-black hover:bg-zinc-200 hover:text-black border-0"
                            size="md"
                            onClick={() => {
                                if (selectedFile) onUpload(selectedFile, { style, pace, keepAudio });
                            }}
                            disabled={isProcessing}
                        >
                            {isProcessing ? (
                                <>
                                    <Loader2 className="animate-spin h-4 w-4 mr-2" />
                                    Analyzing Video...
                                </>
                            ) : (
                                "Generate Narration"
                            )}
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
