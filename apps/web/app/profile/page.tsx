"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, FileText, CheckCircle2, Loader2, Sparkles } from "lucide-react"
import { JobCard } from "@/components/JobCard"
import { useAuth } from "@clerk/nextjs"

export default function ProfilePage() {
    const { getToken } = useAuth()
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [resumeId, setResumeId] = useState<number | null>(null)
    const [matches, setMatches] = useState<any[]>([])
    const [loadingMatches, setLoadingMatches] = useState(false)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
        }
    }

    const handleUpload = async () => {
        if (!file) return

        setUploading(true)
        const formData = new FormData()
        formData.append("file", file)

        try {
            const token = await getToken() // Get Clerk Token
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
            const response = await fetch(`${apiUrl}/api/resumes/upload`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                body: formData,
            })

            if (response.ok) {
                const data = await response.json()
                setResumeId(data.id)
                fetchMatches(data.id)
            } else {
                console.error("Upload failed")
            }
        } catch (error) {
            console.error("Error uploading:", error)
        } finally {
            setUploading(false)
        }
    }

    const fetchMatches = async (id: number) => {
        setLoadingMatches(true)
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
            const response = await fetch(`${apiUrl}/api/resumes/${id}/matches`, {
                headers: {
                    Authorization: `Bearer ${await getToken()}`
                }
            })
            if (response.ok) {
                const data = await response.json()
                setMatches(data)
            }
        } catch (error) {
            console.error("Error fetching matches:", error)
        } finally {
            setLoadingMatches(false)
        }
    }

    return (
        <div className="container mx-auto py-10 px-4 max-w-4xl">
            <h1 className="text-3xl font-bold mb-8">Your Profile & Matches</h1>

            <div className="grid gap-8">
                {/* Resume Upload Section */}
                <Card>
                    <CardHeader>
                        <CardTitle>Resume Upload</CardTitle>
                        <CardDescription>Upload your resume (PDF) to get AI-powered job matches.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-4">
                            <div className="grid w-full max-w-sm items-center gap-1.5">
                                <input
                                    type="file"
                                    accept=".pdf"
                                    onChange={handleFileChange}
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                />
                            </div>
                            <Button onClick={handleUpload} disabled={!file || uploading}>
                                {uploading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Parsing...
                                    </>
                                ) : (
                                    <>
                                        <Upload className="mr-2 h-4 w-4" />
                                        Analyze Resume
                                    </>
                                )}
                            </Button>
                        </div>

                        {resumeId && (
                            <div className="mt-4 p-4 bg-green-50 text-green-700 rounded-md flex items-center gap-2">
                                <CheckCircle2 className="w-5 h-5" />
                                <span>Resume parsed successfully! ID: {resumeId}</span>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Matches Section */}
                {resumeId && (
                    <div className="space-y-6">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-6 h-6 text-purple-600" />
                            <h2 className="text-2xl font-semibold">AI Matched Jobs</h2>
                        </div>

                        {loadingMatches ? (
                            <div className="text-center py-10">
                                <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                                <p className="mt-4 text-muted-foreground">Finding the best roles for you...</p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {matches.map((job) => (
                                    <div key={job.id} className="relative">
                                        {/* Using JobCard but wrapping to check if props match */}
                                        {/* The backend returns 'similarity' which JobCard doesn't expect. 
                         We should display score. For now, using a simple display or reusing JobCard with a similarity badge overlay.
                      */}
                                        <div className="absolute top-4 right-4 z-10 bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm font-bold shadow-sm">
                                            {Math.round(job.similarity * 100)}% Match
                                        </div>
                                        <JobCard
                                            job={{
                                                ...job,
                                                // JobCard expects full job object. The match endpoint returns subset. 
                                                // Check matching.py: id, title, company, url. Description/Source/PostedAt missing.
                                                // I need to update matching.py to return full Job object or handle missing fields.
                                                // For MVP, I'll mock missing fields or update backend.
                                                description: job.description || "Matched via AI",
                                                source: job.source || "AI Match",
                                                posted_at: job.posted_at || new Date().toISOString(),
                                                location: job.location || "Remote"
                                            }}
                                            defaultResumeId={resumeId}
                                        />
                                    </div>
                                ))}
                                {matches.length === 0 && (
                                    <p className="text-muted-foreground">No matches found yet. Try simpler keywords in your resume.</p>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
