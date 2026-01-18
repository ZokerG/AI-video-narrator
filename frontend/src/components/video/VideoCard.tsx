import { Clock, FileVideo } from "lucide-react";

interface VideoCardProps {
    id: number;
    title: string;
    thumbnail?: string;
    duration: string;
    status: string;
    createdAt: string;
}

export function VideoCard({
    title,
    thumbnail,
    duration,
    status,
    createdAt,
}: VideoCardProps) {
    return (
        <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden hover:border-primary-300 hover:shadow-lg transition-all cursor-pointer">
            {/* Thumbnail */}
            <div className="aspect-video bg-gray-100 flex items-center justify-center">
                {thumbnail ? (
                    <img src={thumbnail} alt={title} className="w-full h-full object-cover" />
                ) : (
                    <FileVideo className="h-12 w-12 text-gray-400" />
                )}
            </div>

            {/* Content */}
            <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
                <div className="flex items-center justify-between text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{duration}</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${status === "completed"
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}>
                        {status}
                    </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">{createdAt}</p>
            </div>
        </div>
    );
}
