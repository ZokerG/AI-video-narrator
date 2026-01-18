"use client";

import { Loader2, AlertCircle, CheckCircle2 } from "lucide-react";

interface ProcessingStatusProps {
    isProcessing: boolean;
    error: string | null;
}

export function ProcessingStatus({ isProcessing, error }: ProcessingStatusProps) {
    if (error) {
        return (
            <div className="text-center py-12">
                <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <AlertCircle className="h-10 w-10 text-red-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Processing Failed
                </h2>
                <p className="text-gray-600 mb-4">
                    {error}
                </p>
                <button
                    onClick={() => window.location.reload()}
                    className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition-colors"
                >
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div className="text-center py-16">
            <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
                <Loader2 className="h-12 w-12 text-primary-600 animate-spin" />
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-3">
                Processing Your Video
            </h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
                This may take a few minutes depending on video length. Please don't close this window.
            </p>

            {/* Processing Steps */}
            <div className="max-w-md mx-auto space-y-4 text-left">
                <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                    <span className="text-sm text-gray-700">
                        Video uploaded successfully
                    </span>
                </div>

                <div className="flex items-center gap-3 p-4 bg-primary-50 border border-primary-200 rounded-lg">
                    <Loader2 className="h-5 w-5 text-primary-600 animate-spin flex-shrink-0" />
                    <span className="text-sm text-gray-700">
                        Analyzing video content with AI...
                    </span>
                </div>

                <div className="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg opacity-50">
                    <div className="h-5 w-5 border-2 border-gray-300 rounded-full flex-shrink-0" />
                    <span className="text-sm text-gray-500">
                        Generating AI narration
                    </span>
                </div>

                <div className="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg opacity-50">
                    <div className="h-5 w-5 border-2 border-gray-300 rounded-full flex-shrink-0" />
                    <span className="text-sm text-gray-500">
                        Mixing audio and video
                    </span>
                </div>
            </div>
        </div>
    );
}
