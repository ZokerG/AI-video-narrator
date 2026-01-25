
export interface AnalysisResponse {
    status: string;
    output_video?: string;
    storage_url?: string;
    analysis: {
        language?: string;
        overall?: {
            hook?: string;
            one_sentence_summary?: string;
            tone?: string;
        };
        beats: Array<{
            id: number;
            start_s: number;
            end_s: number;
            voiceover?: {
                script?: string;
            };
            visual_summary?: string;
            key_visuals?: string[];
        }>;
    };
}

// Use relative path to route through Next.js proxy
export const API_BASE_URL = "/api";

export const api = {
    getVideoUrl: (path?: string) => {
        if (!path) return "";
        if (path.startsWith("http")) return path;
        // Assume it's served statically or via API if relative
        return `${API_BASE_URL}/${path.replace(/^\//, "")}`;
    }
};
