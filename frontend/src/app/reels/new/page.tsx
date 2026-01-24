"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { StoryConceptInput } from "@/components/reels/StoryConceptInput";
import { ScriptReview } from "@/components/reels/ScriptReview";
import { VoiceConfiguration } from "@/components/video/VoiceConfiguration";
import { AudioSettings, type AudioConfig } from "@/components/video/AudioSettings";
import { ProcessingStatus } from "@/components/video/ProcessingStatus";
import { useAuth } from "@/contexts/AuthContext";
import axios from "axios";
import { CheckCircle, Check, Download, FileVideo } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

type Step = "concept" | "script" | "voice" | "audio" | "processing" | "complete";

export default function NewReelPage() {
    const { token, refreshUser } = useAuth();
    const [currentStep, setCurrentStep] = useState<Step>("concept");

    // State
    const [topic, setTopic] = useState("");
    const [style, setStyle] = useState("");
    const [script, setScript] = useState<any>(null);
    const [isGeneratingScript, setIsGeneratingScript] = useState(false);
    const [isProcessingVideo, setIsProcessingVideo] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<any>(null);

    // Configs
    const [voiceConfig, setVoiceConfig] = useState({
        voiceId: "JBFqnCBsd6RMkjVDRZzb",
        stability: 50,
        similarityBoost: 70,
        speed: 100,
    });

    const [audioConfig, setAudioConfig] = useState<AudioConfig>({
        style: "viral", // Default for Reels
        pace: "fast",
        originalVolume: 0, // Zero because we generate everything
        backgroundTrack: undefined,
        backgroundVolume: 10
    });

    // Step 1: Generate Script
    const handleGenerateScript = async (inputTopic: string, inputStyle: string) => {
        setTopic(inputTopic);
        setStyle(inputStyle);
        setIsGeneratingScript(true);
        setError(null);

        try {
            const res = await axios.post(`${API_BASE_URL}/reels/generate-script`, {
                topic: inputTopic,
                style: inputStyle
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            console.log("Script generated:", res.data);
            if (res.data.status === "success" && res.data.script) {
                setScript(res.data.script);
                setCurrentStep("script");
            } else {
                throw new Error("Invalid response format from server");
            }
        } catch (err: any) {
            console.error(err);
            setError("Failed to generate script. Please try again.");
        } finally {
            setIsGeneratingScript(false);
        }
    };

    // Step 4: Create Video
    const handleCreateVideo = async () => {
        setIsProcessingVideo(true);
        setCurrentStep("processing");
        setError(null);

        try {
            const payload = {
                script: script,
                voice_id: voiceConfig.voiceId,
                background_track: audioConfig.backgroundTrack,
                // We could pass other audio settings if the backend API supports them
            };

            const res = await axios.post(`${API_BASE_URL}/reels/create`, payload, {
                headers: { Authorization: `Bearer ${token}` },
                timeout: 300000 // 5 mins
            });

            setResult(res.data);
            setCurrentStep("complete");
            if (refreshUser) refreshUser(); // Credits deducted

        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.message || "Failed to create video.");
            // Allow retry?
            // setCurrentStep("audio"); 
        } finally {
            setIsProcessingVideo(false);
        }
    };

    const steps = [
        { id: "concept", label: "Topic", number: 1 },
        { id: "script", label: "Script", number: 2 },
        { id: "voice", label: "Voice", number: 3 },
        { id: "audio", label: "Music", number: 4 },
        { id: "processing", label: "Create", number: 5 },
    ];

    const getStepStatus = (stepId: string) => {
        const stepIds = steps.map(s => s.id);
        const currentIndex = stepIds.indexOf(currentStep);
        const stepIndex = stepIds.indexOf(stepId);

        if (stepIndex < currentIndex || currentStep === "complete") return "completed";
        if (stepIndex === currentIndex) return "current";
        return "upcoming";
    };

    return (
        <ProtectedRoute>
            <DashboardLayout>
                <div className="space-y-8 max-w-5xl mx-auto">
                    {/* Header */}
                    <div className="text-center md:text-left">
                        <h1 className="text-3xl font-bold text-gray-900">Create Viral Short</h1>
                        <p className="text-gray-600 mt-1">
                            Turn any topic into an engaging vertical video in seconds
                        </p>
                    </div>

                    {/* Simple Step Indicator */}
                    {currentStep !== "complete" && (
                        <div className="flex items-center justify-center space-x-2 md:space-x-4">
                            {steps.map((step) => {
                                const status = getStepStatus(step.id);
                                return (
                                    <div key={step.id} className="flex items-center">
                                        <div className={`
                                            w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors
                                            ${status === "completed" ? "bg-green-500 text-white" :
                                                status === "current" ? "bg-indigo-600 text-white" : "bg-gray-200 text-gray-500"}
                                        `}>
                                            {status === "completed" ? <Check className="h-4 w-4" /> : step.number}
                                        </div>
                                        <span className={`ml-2 text-sm font-medium hidden md:block ${status === "current" ? "text-indigo-900" : "text-gray-500"}`}>
                                            {step.label}
                                        </span>
                                        {step.id !== "processing" && (
                                            <div className="w-8 h-0.5 bg-gray-200 ml-2 hidden md:block" />
                                        )}
                                    </div>
                                )
                            })}
                        </div>
                    )}

                    {/* Main Content Area */}
                    <div className="min-h-[400px]">
                        {currentStep === "concept" && (
                            <StoryConceptInput
                                onGenerate={handleGenerateScript}
                                isGenerating={isGeneratingScript}
                            />
                        )}

                        {currentStep === "script" && script && (
                            <ScriptReview
                                script={script}
                                onConfirm={() => setCurrentStep("voice")}
                                onBack={() => setCurrentStep("concept")}
                            />
                        )}

                        {currentStep === "voice" && (
                            <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
                                <VoiceConfiguration
                                    config={voiceConfig}
                                    onChange={setVoiceConfig}
                                    onNext={() => setCurrentStep("audio")}
                                    onBack={() => setCurrentStep("script")}
                                />
                            </div>
                        )}

                        {currentStep === "audio" && (
                            <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
                                <AudioSettings
                                    config={audioConfig}
                                    onChange={setAudioConfig}
                                    onGenerate={handleCreateVideo}
                                    onBack={() => setCurrentStep("voice")}
                                    isProcessing={isProcessingVideo}
                                />
                            </div>
                        )}

                        {currentStep === "processing" && (
                            <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
                                <ProcessingStatus
                                    isProcessing={isProcessingVideo}
                                    error={error}
                                />
                                {error && (
                                    <button
                                        onClick={() => setCurrentStep("audio")}
                                        className="mt-6 mx-auto block px-6 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 font-medium"
                                    >
                                        Go Back & Retry
                                    </button>
                                )}
                            </div>
                        )}

                        {currentStep === "complete" && result && (
                            <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm text-center space-y-6">
                                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                                    <CheckCircle className="h-10 w-10 text-green-600" />
                                </div>
                                <h2 className="text-3xl font-bold text-gray-900">Your Reel is Ready!</h2>

                                <div className="max-w-xs mx-auto bg-black rounded-xl overflow-hidden shadow-2xl aspect-[9/16]">
                                    <video
                                        src={result.video_url}
                                        controls
                                        className="w-full h-full object-cover"
                                    />
                                </div>

                                <div className="flex justify-center gap-4 pt-4">
                                    <a
                                        href={result.video_url}
                                        download
                                        className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold transition-colors"
                                    >
                                        <Download className="h-5 w-5" />
                                        Download Reel
                                    </a>
                                    <a
                                        href="/videos"
                                        className="flex items-center gap-2 px-6 py-3 border-2 border-gray-200 hover:bg-gray-50 text-gray-700 rounded-xl font-bold transition-colors"
                                    >
                                        <FileVideo className="h-5 w-5" />
                                        My Gallery
                                    </a>
                                </div>

                                <button
                                    onClick={() => {
                                        setScript(null);
                                        setResult(null);
                                        setTopic("");
                                        setCurrentStep("concept");
                                    }}
                                    className="block mx-auto text-indigo-600 font-medium hover:underline mt-8"
                                >
                                    Create Another One
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </DashboardLayout>
        </ProtectedRoute>
    );
}
