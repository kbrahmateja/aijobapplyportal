"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Loader2, Download, CheckCircle2, FileText, Sparkles } from "lucide-react"
import { useAuth } from "@clerk/nextjs"

interface TailorResumeModalProps {
    isOpen: boolean
    onOpenChange: (open: boolean) => void
    jobId: number
    jobTitle: string
    jobCompany: string
    resumeId: number
}

export function TailorResumeModal({
    isOpen,
    onOpenChange,
    jobId,
    jobTitle,
    jobCompany,
    resumeId
}: TailorResumeModalProps) {
    const { getToken } = useAuth()
    const [status, setStatus] = useState<"idle" | "tailoring" | "success" | "error">("idle")
    const [isDownloading, setIsDownloading] = useState(false)
    const [errorMessage, setErrorMessage] = useState("")
    const [downloadBlob, setDownloadBlob] = useState<Blob | null>(null)
    const [downloadFilename, setDownloadFilename] = useState("")

    const handleTailor = async () => {
        setStatus("tailoring")
        setErrorMessage("")

        try {
            const token = await getToken()
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

            const response = await fetch(`${apiUrl}/api/resumes/${resumeId}/tailor`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ job_id: jobId })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || "Failed to tailor resume")
            }

            // The response is now JSON pointing to a temporary download URL
            const data = await response.json()

            if (!data.download_url) {
                throw new Error("No download link returned from server.")
            }
            // We transform the backend URL into a proxy URL using our Next.js backend.
            // This bypasses cross-origin restrictions completely.
            const proxyUrl = `/api/download?url=${encodeURIComponent(apiUrl + data.download_url)}&filename=${encodeURIComponent(data.filename || "Tailored_Resume.pdf")}`

            // Fetch the proxy URL natively into a Blob
            const proxyResponse = await fetch(proxyUrl)
            if (!proxyResponse.ok) {
                throw new Error("Failed to download PDF from proxy")
            }

            const pdfBlob = await proxyResponse.blob()

            setDownloadBlob(pdfBlob)
            setDownloadFilename(data.filename || "Tailored_Resume.pdf")
            setStatus("success")
        } catch (error: any) {
            console.error("Tailoring error:", error)
            setStatus("error")
            setErrorMessage(error.message || "An unexpected error occurred.")
        }
    }

    // Reset status when modal closes
    const handleOpenChange = (open: boolean) => {
        if (!open) {
            setTimeout(() => {
                setStatus("idle")
                setDownloadBlob(null)
                setDownloadFilename("")
            }, 300)
        }
        onOpenChange(open)
    }

    return (
        <Dialog open={isOpen} onOpenChange={handleOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Tailor Resume with AI</DialogTitle>
                    <DialogDescription>
                        We will rewrite your existing resume to perfectly match the <span className="font-semibold">{jobTitle}</span> role at <span className="font-semibold">{jobCompany}</span>.
                    </DialogDescription>
                </DialogHeader>

                <div className="flex flex-col items-center justify-center py-6 min-h-[200px] text-center">
                    {status === "idle" && (
                        <div className="space-y-4">
                            <div className="bg-blue-50 text-blue-600 p-4 rounded-full inline-block mb-2">
                                <FileText className="w-8 h-8" />
                            </div>
                            <p className="text-sm text-muted-foreground max-w-[280px] mx-auto">
                                Our AI will analyze the job description and your experience to highlight the most relevant skills.
                            </p>
                        </div>
                    )}

                    {status === "tailoring" && (
                        <div className="space-y-4 flex flex-col items-center animate-in fade-in zoom-in duration-300">
                            <div className="relative">
                                <div className="absolute inset-0 bg-blue-100 rounded-full animate-ping opacity-75"></div>
                                <div className="relative bg-white border-2 border-blue-500 rounded-full p-3">
                                    <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                                </div>
                            </div>
                            <div className="space-y-1">
                                <p className="font-medium text-blue-900">Crafting your perfect resume...</p>
                                <p className="text-xs text-muted-foreground text-center">This usually takes 10-15 seconds.</p>
                            </div>
                        </div>
                    )}

                    {status === "success" && (
                        <div className="space-y-4 flex flex-col items-center animate-in fade-in slide-in-from-bottom-4 duration-300">
                            <div className="bg-green-100 text-green-600 p-3 rounded-full inline-block">
                                <CheckCircle2 className="w-8 h-8" />
                            </div>
                            <div className="space-y-1">
                                <p className="font-medium text-green-900">Success!</p>
                                <p className="text-sm text-green-700/80">Your tailored resume is ready!</p>
                            </div>
                            <div className="flex gap-3 mt-2">
                                <Button
                                    variant="outline"
                                    onClick={() => handleOpenChange(false)}
                                >
                                    Close
                                </Button>
                                <Button
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                    disabled={isDownloading}
                                    onClick={async () => {
                                        if (downloadBlob && downloadFilename) {
                                            setIsDownloading(true)
                                            try {
                                                const objectUrl = window.URL.createObjectURL(downloadBlob)
                                                const link = document.createElement('a')
                                                link.href = objectUrl
                                                link.download = downloadFilename
                                                document.body.appendChild(link)
                                                link.click()

                                                // Cleanup object URL immediately
                                                setTimeout(() => {
                                                    document.body.removeChild(link)
                                                    window.URL.revokeObjectURL(objectUrl)
                                                }, 100)
                                            } finally {
                                                setIsDownloading(false)
                                            }
                                        }
                                    }}
                                >
                                    {isDownloading ? (
                                        <>
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            Downloading...
                                        </>
                                    ) : (
                                        <>
                                            <Download className="w-4 h-4 mr-2" />
                                            Download PDF
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    )}

                    {status === "error" && (
                        <div className="space-y-4 flex flex-col items-center">
                            <div className="bg-red-50 text-red-600 p-3 rounded-full inline-block">
                                <FileText className="w-8 h-8 opacity-50" />
                            </div>
                            <div className="space-y-1">
                                <p className="font-medium text-red-900">Tailoring Failed</p>
                                <p className="text-sm text-red-600/80">{errorMessage}</p>
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setStatus("idle")}
                                className="mt-2"
                            >
                                Try Again
                            </Button>
                        </div>
                    )}
                </div>

                {status === "idle" && (
                    <div className="flex justify-end gap-3 mt-4">
                        <Button variant="ghost" onClick={() => handleOpenChange(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleTailor} className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white shadow-md">
                            <Sparkles className="w-4 h-4 mr-2" />
                            Generate & Download PDF
                        </Button>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    )
}
