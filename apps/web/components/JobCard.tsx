"use client"

import { Calendar, MapPin, ExternalLink, Sparkles, Building2 } from "lucide-react"
import { useState } from "react"
import { TailorResumeModal } from "./TailorResumeModal"

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

const SOURCE_COLORS: Record<string, string> = {
    WeWorkRemotely: "bg-green-50 text-green-700",
    RemoteOK: "bg-red-50 text-red-700",
    Remotive: "bg-purple-50 text-purple-700",
}

function SourceBadge({ source }: { source: string }) {
    const color = SOURCE_COLORS[source] || "bg-blue-50 text-blue-700"
    return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium flex-shrink-0 ${color}`}>
            {source}
        </span>
    )
}

export function JobCard({ job, defaultResumeId, viewMode = "grid" }: JobCardProps) {
    const [isTailoring, setIsTailoring] = useState(false)

    const handleAIApply = () => {
        if (!defaultResumeId) {
            alert("Please upload a resume first via your Profile page.")
            return
        }
        setIsTailoring(true)
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
        if (diffDays === 0) return "Today"
        if (diffDays === 1) return "Yesterday"
        if (diffDays < 7) return `${diffDays}d ago`
        return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
    }

    if (viewMode === "list") {
        return (
            <div className="bg-white rounded-lg border hover:shadow-md transition-shadow p-3 flex items-center gap-4">
                <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-sm hover:text-blue-600 transition-colors line-clamp-1">
                                {job.title}
                            </h3>
                            <div className="flex items-center flex-wrap gap-x-3 gap-y-0.5 mt-1 text-xs text-muted-foreground">
                                <div className="flex items-center gap-1">
                                    <Building2 className="h-3 w-3 flex-shrink-0" />
                                    <span className="truncate">{job.company}</span>
                                </div>
                                {job.location && (
                                    <div className="flex items-center gap-1">
                                        <MapPin className="h-3 w-3 flex-shrink-0" />
                                        <span className="truncate">{job.location}</span>
                                    </div>
                                )}
                                <div className="flex items-center gap-1">
                                    <Calendar className="h-3 w-3 flex-shrink-0" />
                                    <span>{formatDate(job.posted_at)}</span>
                                </div>
                                <SourceBadge source={job.source} />
                            </div>
                        </div>
                        <div className="flex items-center gap-1.5 flex-shrink-0">
                            <a
                                href={job.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-3 py-1.5 border rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1 text-xs font-medium"
                            >
                                View <ExternalLink className="h-3 w-3" />
                            </a>
                            <button
                                onClick={handleAIApply}
                                disabled={isTailoring}
                                className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 text-xs font-medium"
                            >
                                Apply w/ AI <Sparkles className="h-3 w-3" />
                            </button>
                        </div>
                    </div>
                </div>

                {defaultResumeId && (
                    <TailorResumeModal
                        isOpen={isTailoring}
                        onOpenChange={setIsTailoring}
                        jobId={job.id}
                        jobTitle={job.title}
                        jobCompany={job.company}
                        resumeId={defaultResumeId}
                    />
                )}
            </div>
        )
    }

    // Grid view
    return (
        <div className="bg-white rounded-lg border hover:shadow-md transition-shadow overflow-hidden">
            <div className="p-4">
                <div className="flex justify-between items-start gap-2 mb-2">
                    <h3 className="font-semibold text-sm hover:text-blue-600 transition-colors line-clamp-2 leading-snug">
                        {job.title}
                    </h3>
                    <SourceBadge source={job.source} />
                </div>

                <div className="space-y-1 mb-3 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                        <Building2 className="h-3.5 w-3.5 flex-shrink-0" />
                        <span className="truncate">{job.company}</span>
                    </div>
                    {job.location && (
                        <div className="flex items-center gap-1.5">
                            <MapPin className="h-3.5 w-3.5 flex-shrink-0" />
                            <span className="line-clamp-1">{job.location}</span>
                        </div>
                    )}
                    <div className="flex items-center gap-1.5">
                        <Calendar className="h-3.5 w-3.5 flex-shrink-0" />
                        <span>{formatDate(job.posted_at)}</span>
                    </div>
                </div>

                <div className="flex gap-2">
                    <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 px-3 py-1.5 border rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-1.5 font-medium text-xs"
                    >
                        View <ExternalLink className="h-3 w-3" />
                    </a>
                    <button
                        onClick={handleAIApply}
                        disabled={isTailoring}
                        className="flex-1 px-3 py-1.5 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1.5 font-medium text-xs"
                    >
                        Apply w/ AI <Sparkles className="h-3.5 w-3.5" />
                    </button>
                </div>

                {defaultResumeId && (
                    <TailorResumeModal
                        isOpen={isTailoring}
                        onOpenChange={setIsTailoring}
                        jobId={job.id}
                        jobTitle={job.title}
                        jobCompany={job.company}
                        resumeId={defaultResumeId}
                    />
                )}
            </div>
        </div>
    )
}
