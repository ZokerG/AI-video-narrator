"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { VideoUploader } from "@/components/video/VideoUploader";
import { VoiceConfiguration } from "@/components/video/VoiceConfiguration";
import { AudioSettings } from "@/components/video/AudioSettings";
import { ProcessingStatus } from "@/components/video/ProcessingStatus";
import { useState } from "react";
import { ArrowLeft, Check } from "lucide-react";
import Link from "next/link";
import axios from "axios";

type Step = "upload" | "voice" | "audio" | "processing" | "complete";

interface VoiceConfig {
    voiceId: string;
    stability: number;
    similarityBoost: number;
    speed: number;
}

interface AudioConfig {
    style: "viral" | "documentary" | "funny";
    pace: "fast" | "medium" | "slow";
    originalVolume: number;
}

interface ProcessingResult {
    status: string;
    output_video?: string;
    analysis?: any;
    message?: string;
}

export default function NewVideoPage() {
    const [currentStep, setCurrentStep] = useState<Step>("upload");
    const [videoFile, setVideoFile] = useState<File | null>(null);
    const [voiceConfig, setVoiceConfig] = useState<VoiceConfig>({
        voiceId: "JBFqnCBsd6RMkjVDRZzb",
        stability: 50,
        similarityBoost: 70,
        speed: 100,
    });
    const [audioConfig, setAudioConfig] = useState<AudioConfig>({
        style: "viral",
        pace: "fast",
        originalVolume: 30,
    });

    const [isProcessing, setIsProcessing] = useState(false);
    const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!videoFile) return;

        setIsProcessing(true);
        setCurrentStep("processing");
        setError(null);

        try {
            // Create FormData
            const formData = new FormData();
            formData.append("file", videoFile);
            formData.append("style", audioConfig.style);
            formData.append("pace", audioConfig.pace);
            formData.append("voice_id", voiceConfig.voiceId);
            formData.append("stability", voiceConfig.stability.toString());
            formData.append("similarity_boost", voiceConfig.similarityBoost.toString());
            formData.append("speed", voiceConfig.speed.toString());
            formData.append("original_volume", audioConfig.originalVolume.toString());

            // Call backend API
            const response = await axios.post<ProcessingResult>(
                "http://localhost:8000/analyze",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                    timeout: 600000, // 10 minutes
                }
            );

            if (response.data.status === "completed") {
                setProcessingResult(response.data);
                setCurrentStep("complete");
            } else {
                setError(response.data.message || "Unknown error occurred");
            }
        } catch (err: any) {
            console.error("Error processing video:", err);
            setError(err.response?.data?.message || err.message || "Failed to process video");
        } finally {
            setIsProcessing(false);
        }
    };

    const steps = [
        { id: "upload" as Step, label: "Upload Video", number: 1 },
        { id: "voice" as Step, label: "Voice Settings", number: 2 },
        { id: "audio" as Step, label: "Audio & Style", number: 3 },
    ];

    const currentStepIndex = steps.findIndex((s) => s.id === currentStep);

    return (
        <ProtectedRoute>
            <DashboardLayout>
                <div className="max-w-5xl mx-auto">
                    {/* Header */}
                    <div className="mb-8">
                        <Link
                            href="/"
                            className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4 font-medium hover:gap-3 transition-all"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            Back to Dashboard
                        </Link>
                        <h1 className="text-3xl font-bold text-gray-900">Create New Video</h1>
                        <p className="text-gray-600 mt-1">
                            Transform your video with AI-powered narration
                        </p>
                    </div>

                    {/* Progress Steps - Hide during processing */}
                    {currentStep !== "processing" && currentStep !== "complete" && (
                        <div className="mb-10">
                            <div className="flex items-center justify-between max-w-3xl mx-auto">
                                {steps.map((step, index) => {
                                    const isCurrent = currentStep === step.id;
                                    const isPast = currentStepIndex > index;
                                    const isLast = index === steps.length - 1;

                                    return (
                                        <div key={step.id} className="flex items-center flex-1">
                                            <div className="flex flex-col items-center flex-1">
                                                {/* Circle */}
                                                <div
                                                    className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all shadow-sm ${isCurrent
                                                        ? "bg-primary-600 text-white ring-4 ring-primary-100 scale-110"
                                                        : isPast
                                                            ? "bg-green-500 text-white"
                                                            : "bg-white border-2 border-gray-300 text-gray-400"
                                                        }`}
                                                >
                                                    {isPast ? <Check className="h-6 w-6" /> : step.number}
                                                </div>
                                                {/* Label */}
                                                <span
                                                    className={`text-sm mt-3 font-medium transition-all ${isCurrent
                                                        ? "text-gray-900 font-semibold"
                                                        : isPast
                                                            ? "text-green-600"
                                                            : "text-gray-500"
                                                        }`}
                                                >
                                                    {step.label}
                                                </span>
                                            </div>
                                            {/* Connector Line */}
                                            {!isLast && (
                                                <div className="flex-1 px-4 -mt-10">
                                                    <div
                                                        className={`h-1 rounded-full transition-all ${isPast ? "bg-green-500" : "bg-gray-200"
                                                            }`}
                                                    />
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* Content */}
                    <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-sm p-8">
                        {currentStep === "upload" && (
                            <VideoUploader
                                onUpload={(file) => {
                                    setVideoFile(file);
                                    setCurrentStep("voice");
                                }}
                            />
                        )}

                        {currentStep === "voice" && (
                            <VoiceConfiguration
                                config={voiceConfig}
                                onChange={setVoiceConfig}
                                onNext={() => setCurrentStep("audio")}
                                onBack={() => setCurrentStep("upload")}
                            />
                        )}

                        {currentStep === "audio" && (
                            <AudioSettings
                                config={audioConfig}
                                onChange={setAudioConfig}
                                onGenerate={handleGenerate}
                                onBack={() => setCurrentStep("voice")}
                                isProcessing={isProcessing}
                            />
                        )}

                        {currentStep === "processing" && (
                            <ProcessingStatus
                                isProcessing={isProcessing}
                                error={error}
                            />
                        )}

                        {currentStep === "complete" && processingResult && (
                            <div className="text-center py-12">
                                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                                    <Check className="h-10 w-10 text-green-600" />
                                </div>
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                                    Video Processing Complete!
                                </h2>
                                <p className="text-gray-600 mb-8">
                                    Your video has been successfully processed with AI narration
                                </p>

                                {processingResult.output_video && (
                                    <div className="space-y-4">
                                        <video
                                            src={`http://localhost:8000/${processingResult.output_video}`}
                                            controls
                                            className="w-full max-w-2xl mx-auto rounded-xl shadow-lg"
                                        />

                                        <div className="flex gap-4 justify-center">
                                            <a
                                                href={`http://localhost:8000/${processingResult.output_video}`}
                                                download
                                                className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition-colors"
                                            >
                                                Download Video
                                            </a>
                                            <Link
                                                href="/new"
                                                onClick={() => window.location.reload()}
                                                className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-900 rounded-lg font-semibold transition-colors"
                                            >
                                                Create Another
                                            </Link>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </DashboardLayout>
        </ProtectedRoute>
    );
}
