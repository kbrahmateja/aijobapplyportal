"use client"

import { Calendar, MapPin, ExternalLink, Sparkles, Building2 } from "lucide-react"
import { useState } from "react"

interface Job {
    id: number
    title: string
    company: string
    location: string | null
    description: string | null
    url: string
    source: string
    posted_at: string
}

interface JobCardProps {
    job: Job
    defaultResumeId: number | null
    viewMode?: "grid" | "list"
}

export function JobCard({ job, defaultResumeId, viewMode = "grid" }: JobCardProps) {
    const [applying, setApplying] = useState(false)

    const handleAIApply = async () => {
        if (!defaultResumeId) {
            alert("Please upload a resume first")
            return
        }

        setApplying(true)
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/applications/apply`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    job_id: job.id,
                    resume_id: defaultResumeId
                })
            })

            if (response.ok) {
                alert("Application submitted successfully!")
            } else {
                alert("Failed to apply. Please try again.")
            }
        } catch (error) {
            console.error("Error applying:", error)
            alert("An error occurred. Please try again.")
        } finally {
            setApplying(false)
        }
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    }

    if (viewMode === "list") {
        return (
            <div className="bg-white rounded-lg border hover:shadow-md transition-shadow p-4 flex items-center gap-4">
                <div className="flex-1">
                    <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                            <h3 className="font-semibold text-lg hover:text-blue-600 transition-colors line-clamp-1">
                                {job.title}
                            </h3>
                            <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                    <Building2 className="h-4 w-4" />
                                    <span>{job.company}</span>
                                </div>
                                {job.location && (
                                    <div className="flex items-center gap-1">
                                        <MapPin className="h-4 w-4" />
                                        <span>{job.location}</span>
                                    </div>
                                )}
                                <div className="flex items-center gap-1">
                                    <Calendar className="h-4 w-4" />
                                    <span>{formatDate(job.posted_at)}</span>
                                </div>
                                <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                                    {job.source}
                                </span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                            <a
                                href={job.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1 text-sm font-medium"
                            >
                                View
                                <ExternalLink className="h-3 w-3" />
                            </a>
                            <button
                                onClick={handleAIApply}
                                disabled={applying || !defaultResumeId}
                                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 text-sm font-medium"
                            >
                                {applying ? "Applying..." : "Apply w/ AI"}
                                <Sparkles className="h-3 w-3" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    // Grid view (default)
    return (
        <div className="bg-white rounded-lg border hover:shadow-lg transition-shadow overflow-hidden">
            <div className="p-6">
                <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-lg hover:text-blue-600 transition-colors line-clamp-2">
                        {job.title}
                    </h3>
                    <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                        {job.source}
                    </span>
                </div>

                <div className="space-y-2 mb-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4" />
                        <span>{job.company}</span>
                    </div>
                    {job.location && (
                        <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            <span className="line-clamp-1">{job.location}</span>
                        </div>
                    )}
                    <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(job.posted_at)}</span>
                    </div>
                </div>

                {job.description && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                        {job.description}
                    </p>
                )}

                <div className="flex gap-2">
                    <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 font-medium text-sm"
                    >
                        View
                        <ExternalLink className="h-4 w-4" />
                    </a>
                    <button
                        onClick={handleAIApply}
                        disabled={applying || !defaultResumeId}
                        className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium text-sm"
                    >
                        {applying ? "Applying..." : "Apply w/ AI"}
                        <Sparkles className="h-4 w-4" />
                    </button>
                </div>
            </div>
        </div>
    )
}
