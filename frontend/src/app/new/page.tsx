"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { VideoUploader } from "@/components/video/VideoUploader";
import { VoiceConfiguration } from "@/components/video/VoiceConfiguration";
import { AudioSettings, type AudioConfig } from "@/components/video/AudioSettings";
import { ProcessingStatus } from "@/components/video/ProcessingStatus";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";
import { CheckCircle, Download, FileVideo } from "lucide-react";
import axios from "axios";
import { AnalysisViewer } from "@/components/AnalysisViewer";
import { API_BASE_URL } from "@/lib/api";

type Step = "upload" | "voice" | "audio" | "processing" | "complete";

interface VoiceConfig {
    voiceId: string;
    stability: number;
    similarityBoost: number;
    speed: number;
}

interface ProcessingResult {
    status: string;
    output_video?: string;
    storage_url?: string;
    video_id?: number;
    analysis?: {
        beats?: Array<{
            start_s: number;
            end_s: number;
            voiceover?: {
                script?: string;
            };
            visual_summary?: string;
        }>;
    };
    processing_time?: string;
    message?: string;
}

export default function NewVideoPage() {
    const { token, refreshUser } = useAuth();
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
        originalVolume: 10,
        backgroundTrack: undefined,
        backgroundVolume: 10
    });

    const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!videoFile) return;

        setIsProcessing(true);
        setCurrentStep("processing");
        setError(null);

        try {
            // Get auth token from localStorage
            const authToken = token || localStorage.getItem("auth_token");

            if (!authToken) {
                setError("Authentication required. Please login again.");
                setIsProcessing(false);
                return;
            }

            // Create FormData
            const formData = new FormData();
            formData.append("video", videoFile);
            formData.append("style", audioConfig.style);
            formData.append("pace", audioConfig.pace);
            formData.append("voice_id", voiceConfig.voiceId);
            formData.append("stability", voiceConfig.stability.toString());
            formData.append("similarity_boost", voiceConfig.similarityBoost.toString());
            formData.append("speed", voiceConfig.speed.toString());
            formData.append("original_volume", audioConfig.originalVolume.toString());

            if (audioConfig.backgroundTrack) {
                formData.append("background_track", audioConfig.backgroundTrack);
                formData.append("background_volume", audioConfig.backgroundVolume.toString());
            }

            // Call backend API
            const response = await axios.post<ProcessingResult>(
                `${API_BASE_URL}/analyze-v2`,  // ✅ Using new Clean Architecture endpoint
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                        "Authorization": `Bearer ${authToken}`
                    },
                    timeout: 600000, // 10 minutes
                }
            );

            if (response.data.status === "completed") {
                setProcessingResult(response.data);
                setCurrentStep("complete");
                // Refresh credits to reflect deduction
                if (refreshUser) refreshUser();
                console.log("✅ Processing complete:", response.data);
                console.log("📊 Analysis object:", response.data.analysis);
                console.log("📝 Beats array:", response.data.analysis?.beats);
                if (response.data.analysis?.beats?.[0]) {
                    console.log("🔍 First beat:", response.data.analysis.beats[0]);
                }
            } else {
                setError(response.data.message || "Unknown error occurred");
            }
        } catch (err: any) {
            console.error("❌ Processing error:", err);
            setError(err.response?.data?.message || err.message || "Processing failed");
            setCurrentStep("upload");
        } finally {
            setIsProcessing(false);
        }
    };

    const handleReset = () => {
        setVideoFile(null);
        setProcessingResult(null);
        setError(null);
        setCurrentStep("upload");
    };

    const steps = [
        { id: "upload" as Step, label: "Upload Video", number: 1 },
        { id: "voice" as Step, label: "Voice Settings", number: 2 },
        { id: "audio" as Step, label: "Audio Settings", number: 3 },
        { id: "processing" as Step, label: "Processing", number: 4 },
        { id: "complete" as Step, label: "Complete", number: 5 },
    ];

    const getStepStatus = (stepId: Step) => {
        const currentIndex = steps.findIndex((s) => s.id === currentStep);
        const stepIndex = steps.findIndex((s) => s.id === stepId);

        if (stepIndex < currentIndex) return "completed";
        if (stepIndex === currentIndex) return "current";
        return "upcoming";
    };

    return (
        <ProtectedRoute>
            <DashboardLayout>
                <div className="space-y-8">
                    {/* Header */}
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Create New Video</h1>
                        <p className="text-gray-600 mt-1">
                            Transform your video with AI-powered narration
                        </p>
                    </div>

                    {/* Step Indicator */}
                    {currentStep !== "complete" && (
                        <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                {steps.slice(0, -1).map((step, index) => {
                                    const status = getStepStatus(step.id);
                                    return (
                                        <div key={step.id} className="flex items-center flex-1">
                                            <div className="flex flex-col items-center">
                                                <div
                                                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm
                                                        ${status === "completed"
                                                            ? "bg-green-500 text-white"
                                                            : status === "current"
                                                                ? "bg-primary-600 text-white ring-4 ring-blue-100"
                                                                : "bg-gray-200 text-gray-600"
                                                        }`}
                                                >
                                                    {status === "completed" ? "✓" : step.number}
                                                </div>
                                                <span className="text-xs mt-2 font-medium text-gray-700">
                                                    {step.label}
                                                </span>
                                            </div>
                                            {index < steps.length - 2 && (
                                                <div className="flex-1 h-1 mx-4 bg-gray-200 rounded">
                                                    <div
                                                        className={`h-full rounded transition-all ${status === "completed" ? "bg-green-500 w-full" : "w-0"
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

                        {/* Complete Step with Script */}
                        {currentStep === "complete" && processingResult && (
                            <div className="space-y-6">
                                <div className="text-center mb-6">
                                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <CheckCircle className="h-8 w-8 text-green-600" />
                                    </div>
                                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                                        Video Generated Successfully!
                                    </h2>
                                    <p className="text-gray-600">
                                        Processing time: {processingResult.processing_time}
                                    </p>
                                </div>

                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    {/* Video Preview */}
                                    <div className="space-y-4">
                                        <h3 className="font-semibold text-lg text-gray-900">
                                            Generated Video
                                        </h3>
                                        <div className="bg-black rounded-xl overflow-hidden aspect-video">
                                            <video
                                                controls
                                                className="w-full h-full"
                                                src={processingResult.storage_url}
                                            >
                                                Your browser does not support video playback.
                                            </video>
                                        </div>

                                        <div className="flex gap-3">
                                            <a
                                                href={processingResult.storage_url}
                                                download
                                                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold transition-colors"
                                            >
                                                <Download className="h-5 w-5" />
                                                Download Video
                                            </a>
                                            <a
                                                href="/videos"
                                                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 border-2 border-gray-300 hover:border-primary-300 hover:bg-primary-50 text-gray-700 rounded-xl font-semibold transition-colors"
                                            >
                                                <FileVideo className="h-5 w-5" />
                                                My Videos
                                            </a>
                                        </div>
                                    </div>

                                    {/* Narration Script */}
                                    <div className="space-y-4">
                                        <h3 className="font-semibold text-lg text-gray-900">
                                            Narration Script
                                        </h3>
                                        <div className="bg-gray-50 rounded-xl p-4 max-h-96 overflow-y-auto space-y-3">
                                            {processingResult.analysis?.beats && processingResult.analysis.beats.length > 0 ? (
                                                processingResult.analysis.beats.map((beat, index) => (
                                                    <div
                                                        key={index}
                                                        className="bg-white rounded-lg p-4 border border-gray-200"
                                                    >
                                                        <div className="flex items-start gap-3">
                                                            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                                                                <span className="text-primary-600 font-semibold text-sm">
                                                                    {index + 1}
                                                                </span>
                                                            </div>
                                                            <div className="flex-1 min-w-0">
                                                                <div className="text-xs text-gray-500 mb-1">
                                                                    {beat.start_s?.toFixed(1)}s - {beat.end_s?.toFixed(1)}s
                                                                </div>
                                                                <p className="text-gray-900 leading-relaxed">
                                                                    {beat.voiceover?.script || beat.visual_summary || "No narration text"}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="text-center text-gray-500 py-8">
                                                    No narration script available
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <button
                                    onClick={handleReset}
                                    className="w-full px-6 py-3 border-2 border-gray-300 hover:border-primary-300 hover:bg-primary-50 text-gray-700 rounded-xl font-semibold transition-colors"
                                >
                                    Create Another Video
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </DashboardLayout>
        </ProtectedRoute>
    );
}
