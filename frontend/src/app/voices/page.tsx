"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/contexts/AuthContext";
import { useState, useEffect } from "react";
import { Mic, Play, Loader2, Search, Filter } from "lucide-react";
import axios from "axios";
import { API_BASE_URL } from "@/lib/api";

interface Voice {
    id: string;
    name: string;
    description: string;
    labels: {
        accent?: string;
        description?: string;
        age?: string;
        gender?: string;
        use_case?: string;
    };
}

export default function VoicesPage() {
    const { token } = useAuth();
    const [voices, setVoices] = useState<Voice[]>([]);
    const [filteredVoices, setFilteredVoices] = useState<Voice[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedLanguage, setSelectedLanguage] = useState<string>("all");
    const [playingVoice, setPlayingVoice] = useState<string | null>(null);
    const [generatingPreview, setGeneratingPreview] = useState<string | null>(null);

    useEffect(() => {
        fetchVoices();
    }, []);

    useEffect(() => {
        filterVoices();
    }, [searchQuery, selectedLanguage, voices]);

    const fetchVoices = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await axios.get(`${API_BASE_URL}/voices`);
            if (response.data.voices) {
                setVoices(response.data.voices);
                setFilteredVoices(response.data.voices);
            } else {
                setVoices([]);
                setFilteredVoices([]);
                if (response.data.error) throw new Error(response.data.error);
            }
        } catch (err: any) {
            setError(err.response?.data?.error || err.message || "Failed to load voices");
            setVoices([]); // Ensure we don't have undefined state
            setFilteredVoices([]);
        } finally {
            setLoading(false);
        }
    };

    const filterVoices = () => {
        if (!voices) return;
        let filtered = [...voices];

        // Search filter
        if (searchQuery) {
            filtered = filtered.filter((voice) =>
                voice.name.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        // Language filter
        if (selectedLanguage !== "all") {
            filtered = filtered.filter((voice) =>
                voice.labels.accent?.toLowerCase().includes(selectedLanguage.toLowerCase())
            );
        }

        setFilteredVoices(filtered);
    };

    const handlePreview = async (voiceId: string, voiceName: string) => {
        setGeneratingPreview(voiceId);

        try {
            const formData = new FormData();
            formData.append("voice_id", voiceId);
            formData.append("text", `Hello, I'm ${voiceName}. This is how I sound.`);

            const response = await axios.post(
                `${API_BASE_URL}/voices/preview`,
                formData,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            if (response.data.audio_url) {
                const audio = new Audio(response.data.audio_url);
                audio.play();
                setPlayingVoice(voiceId);

                audio.onended = () => {
                    setPlayingVoice(null);
                };
            }
        } catch (err: any) {
            alert(err.response?.data?.detail || "Failed to generate preview");
        } finally {
            setGeneratingPreview(null);
        }
    };

    const getLanguages = () => {
        const languages = new Set<string>();
        if (!voices || voices.length === 0) {
            return [];
        }
        voices.forEach((voice) => {
            if (voice.labels.accent) {
                languages.add(voice.labels.accent);
            }
        });
        return Array.from(languages).sort();
    };

    return (
        <ProtectedRoute>
            <DashboardLayout>
                <div className="space-y-8">
                    {/* Header */}
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Voice Library</h1>
                        <p className="text-gray-600 mt-1">
                            Explore and preview all available AI voices
                        </p>
                    </div>

                    {/* Filters & Search */}
                    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
                        <div className="flex flex-col md:flex-row gap-4">
                            {/* Search */}
                            <div className="flex-1 relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search voices..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none"
                                />
                            </div>

                            {/* Language Filter */}
                            <div className="relative">
                                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                                <select
                                    value={selectedLanguage}
                                    onChange={(e) => setSelectedLanguage(e.target.value)}
                                    className="pl-10 pr-8 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none appearance-none bg-white min-w-[200px]"
                                >
                                    <option value="all">All Languages</option>
                                    {getLanguages().map((lang) => (
                                        <option key={lang} value={lang}>
                                            {lang.charAt(0).toUpperCase() + lang.slice(1)}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="mt-4 text-sm text-gray-600">
                            Showing {filteredVoices?.length || 0} of {voices?.length || 0} voices
                        </div>
                    </div>

                    {/* Loading State */}
                    {loading && (
                        <div className="flex items-center justify-center py-20">
                            <Loader2 className="h-12 w-12 text-primary-600 animate-spin" />
                        </div>
                    )}

                    {/* Error State */}
                    {error && (
                        <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
                            <p className="text-red-900 font-semibold">Error</p>
                            <p className="text-red-700">{error}</p>
                        </div>
                    )}

                    {/* Voices Grid */}
                    {!loading && !error && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {filteredVoices?.map((voice) => (
                                <div
                                    key={voice.id}
                                    className="bg-white rounded-2xl border-2 border-gray-200 p-6 hover:border-primary-300 hover:shadow-lg transition-all"
                                >
                                    {/* Voice Icon */}
                                    <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <Mic className="h-8 w-8 text-white" />
                                    </div>

                                    {/* Voice Name */}
                                    <h3 className="text-lg font-bold text-gray-900 text-center mb-2">
                                        {voice.name}
                                    </h3>

                                    {/* Labels */}
                                    <div className="flex flex-wrap gap-2 justify-center mb-4">
                                        {voice.labels.gender && (
                                            <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-lg">
                                                {voice.labels.gender}
                                            </span>
                                        )}
                                        {voice.labels.accent && (
                                            <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-lg">
                                                {voice.labels.accent}
                                            </span>
                                        )}
                                        {voice.labels.age && (
                                            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-lg">
                                                {voice.labels.age}
                                            </span>
                                        )}
                                    </div>

                                    {/* Description */}
                                    {voice.description && (
                                        <p className="text-sm text-gray-600 text-center mb-4 line-clamp-2">
                                            {voice.description}
                                        </p>
                                    )}

                                    {/* Preview Button */}
                                    <button
                                        onClick={() => handlePreview(voice.id, voice.name)}
                                        disabled={generatingPreview === voice.id}
                                        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold transition-colors disabled:opacity-50"
                                    >
                                        {generatingPreview === voice.id ? (
                                            <>
                                                <Loader2 className="h-5 w-5 animate-spin" />
                                                Generating...
                                            </>
                                        ) : playingVoice === voice.id ? (
                                            <>
                                                <Play className="h-5 w-5" fill="currentColor" />
                                                Playing...
                                            </>
                                        ) : (
                                            <>
                                                <Play className="h-5 w-5" />
                                                Preview
                                            </>
                                        )}
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Empty State */}
                    {!loading && !error && filteredVoices && filteredVoices.length === 0 && (
                        <div className="text-center py-20">
                            <Mic className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                No voices found
                            </h3>
                            <p className="text-gray-600">
                                Try adjusting your search or filter criteria
                            </p>
                        </div>
                    )}
                </div>
            </DashboardLayout>
        </ProtectedRoute>
    );
}
