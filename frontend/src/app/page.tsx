"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { VideoCard } from "@/components/video/VideoCard";
import { Plus } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  // Placeholder videos
  const videos = [
    {
      id: 1,
      title: "Welcome Video",
      thumbnail: "/placeholder-thumbnail.jpg",
      duration: "0:45",
      status: "completed",
      createdAt: "2024-01-15",
    },
  ];

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Manage your AI-powered videos
              </p>
            </div>
            <Link
              href="/new"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold transition-colors shadow-lg hover:shadow-xl"
            >
              <Plus className="h-5 w-5" />
              New Video
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 shadow-sm">
              <p className="text-sm font-medium text-gray-600">Total Videos</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{videos.length}</p>
            </div>
            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 shadow-sm">
              <p className="text-sm font-medium text-gray-600">Processing</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            </div>
            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 shadow-sm">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{videos.length}</p>
            </div>
          </div>

          {/* Recent Videos */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Recent Videos
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map((video) => (
                <VideoCard key={video.id} {...video} />
              ))}
            </div>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
