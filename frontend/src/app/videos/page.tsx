"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/contexts/AuthContext";
import { useState, useEffect } from "react";
import { FileVideo, Download, Trash2, Play, Calendar, HardDrive, Loader2 } from "lucide-react";
import axios from "axios";
import { API_BASE_URL } from "@/lib/api";

interface Video {
    id: number;
    original_filename: string;
    storage_url: string;
    file_size: number;
    status: string;
    created_at: string;
    voice_config?: any;
    audio_config?: any;
}

export default function MyVideosPage() {
    const { token } = useAuth();
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deletingId, setDeletingId] = useState<number | null>(null);

    useEffect(() => {
        fetchVideos();
    }, []);

    const fetchVideos = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${API_BASE_URL}/videos/my-videos`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            setVideos(response.data.videos);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to load videos");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (videoId: number) => {
        if (!confirm("Are you sure you want to delete this video?")) {
            return;
        }

        setDeletingId(videoId);

        try {
            await axios.delete(`${API_BASE_URL}/videos/${videoId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            // Remove from list
            setVideos(videos.filter((v) => v.id !== videoId));
        } catch (err: any) {
            alert(err.response?.data?.detail || "Failed to delete video");
        } finally {
            setDeletingId(null);
        }
    };

    const formatFileSize = (bytes: number) => {
        if (!bytes) return "N/A";
        const mb = bytes / (1024 * 1024);
        return `${mb.toFixed(2)} MB`;
    };

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    };

    return (
        <ProtectedRoute>
            <DashboardLayout>
                <div className="space-y-8">
                    {/* Header */}
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">My Videos</h1>
                        <p className="text-gray-600 mt-1">
                            View and manage your AI-generated videos
                        </p>
                    </div>

                    {/* Loading State */}
                    {loading && (
                        <div className="flex items-center justify-center py-20">
                            <div className="text-center">
                                <Loader2 className="h-12 w-12 text-primary-600 animate-spin mx-auto mb-4" />
                                <p className="text-gray-600">Loading your videos...</p>
                            </div>
                        </div>
                    )}

                    {/* Error State */}
                    {error && (
                        <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
                            <p className="text-red-900 font-semibold">Error</p>
                            <p className="text-red-700">{error}</p>
                        </div>
                    )}

                    {/* Empty State */}
                    {!loading && !error && videos.length === 0 && (
                        <div className="text-center py-20">
                            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <FileVideo className="h-10 w-10 text-gray-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                No videos yet
                            </h3>
                            <p className="text-gray-600 mb-6">
                                Start creating your first AI-powered video!
                            </p>
                            <a
                                href="/new"
                                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold transition-colors"
                            >
                                Create Video
                            </a>
                        </div>
                    )}

                    {/* Videos Grid */}
                    {!loading && !error && videos.length > 0 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {videos.map((video) => (
                                <div
                                    key={video.id}
                                    className="bg-white rounded-2xl border-2 border-gray-200 overflow-hidden hover:border-primary-300 hover:shadow-lg transition-all"
                                >
                                    {/* Video Preview */}
                                    <div className="aspect-video bg-gray-900 flex items-center justify-center relative group">
                                        <FileVideo className="h-16 w-16 text-gray-600" />

                                        {/* Play Overlay */}
                                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all flex items-center justify-center">
                                            <a
                                                href={video.storage_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="opacity-0 group-hover:opacity-100 transition-opacity"
                                            >
                                                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
                                                    <Play className="h-8 w-8 text-primary-600 ml-1" fill="currentColor" />
                                                </div>
                                            </a>
                                        </div>
                                    </div>

                                    {/* Video Info */}
                                    <div className="p-4 space-y-3">
                                        <h3 className="font-semibold text-gray-900 truncate">
                                            {video.original_filename || `Video ${video.id}`}
                                        </h3>

                                        {/* Metadata */}
                                        <div className="space-y-2 text-sm text-gray-600">
                                            <div className="flex items-center gap-2">
                                                <Calendar className="h-4 w-4" />
                                                <span>{formatDate(video.created_at)}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <HardDrive className="h-4 w-4" />
                                                <span>{formatFileSize(video.file_size)}</span>
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="flex gap-2 pt-2 border-t border-gray-100">
                                            <a
                                                href={video.storage_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
                                            >
                                                <Download className="h-4 w-4" />
                                                Download
                                            </a>
                                            <button
                                                onClick={() => handleDelete(video.id)}
                                                disabled={deletingId === video.id}
                                                className="px-4 py-2 border-2 border-gray-200 hover:border-red-300 hover:bg-red-50 text-gray-700 hover:text-red-700 rounded-lg font-medium transition-colors disabled:opacity-50"
                                            >
                                                {deletingId === video.id ? (
                                                    <Loader2 className="h-4 w-4 animate-spin" />
                                                ) : (
                                                    <Trash2 className="h-4 w-4" />
                                                )}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </DashboardLayout>
        </ProtectedRoute>
    );
}
