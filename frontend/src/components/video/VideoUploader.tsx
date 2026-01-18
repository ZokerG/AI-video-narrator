"use client";

import { Upload, FileVideo, Film } from "lucide-react";
import { useState } from "react";

interface VideoUploaderProps {
    onUpload: (file: File) => void;
}

export function VideoUploader({ onUpload }: VideoUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith("video/")) {
            onUpload(file);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            onUpload(file);
        }
    };

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Video</h2>
                <p className="text-gray-600">
                    Start by uploading the video you want to transform
                </p>
            </div>

            <div
                onDrop={handleDrop}
                onDragOver={(e) => {
                    e.preventDefault();
                    setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                className={`relative border-2 border-dashed rounded-2xl p-16 text-center transition-all ${isDragging
                        ? "border-primary-500 bg-primary-50 scale-[1.02]"
                        : "border-gray-300 hover:border-gray-400 bg-gray-50"
                    }`}
            >
                <input
                    type="file"
                    accept="video/*"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="video-upload"
                />

                <label htmlFor="video-upload" className="cursor-pointer">
                    <div className="flex flex-col items-center gap-6">
                        <div className={`w-20 h-20 rounded-2xl flex items-center justify-center transition-all ${isDragging
                                ? "bg-primary-500 scale-110"
                                : "bg-white shadow-lg"
                            }`}>
                            {isDragging ? (
                                <Upload className="h-10 w-10 text-white" />
                            ) : (
                                <Film className="h-10 w-10 text-primary-600" />
                            )}
                        </div>

                        <div className="space-y-2">
                            <p className="text-xl font-semibold text-gray-900">
                                {isDragging ? "Drop your video here" : "Drag and drop your video"}
                            </p>
                            <p className="text-gray-600">
                                or click the button below to browse
                            </p>
                        </div>

                        <button
                            type="button"
                            className="mt-4 px-8 py-3.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl"
                        >
                            Choose Video File
                        </button>
                    </div>
                </label>
            </div>

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-white rounded-xl border border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Supported formats</p>
                    <p className="text-sm font-semibold text-gray-900">MP4, MOV, AVI, WebM</p>
                </div>
                <div className="p-4 bg-white rounded-xl border border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Max duration</p>
                    <p className="text-sm font-semibold text-gray-900">5 minutes</p>
                </div>
                <div className="p-4 bg-white rounded-xl border border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Max file size</p>
                    <p className="text-sm font-semibold text-gray-900">500 MB</p>
                </div>
            </div>
        </div>
    );
}
