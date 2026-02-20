import { NextResponse } from "next/server"
import { auth } from "@clerk/nextjs/server"

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url)
        const resumeId = searchParams.get("resumeId")
        const jobId = searchParams.get("jobId")
        const jobCompany = searchParams.get("jobCompany") || "Company"

        const { getToken } = await auth()
        const token = await getToken()

        if (!token) {
            return new NextResponse("Unauthorized", { status: 401 })
        }

        if (!resumeId || !jobId) {
            return new NextResponse("Missing resumeId or jobId", { status: 400 })
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

        // Proxy the tailoring request to FastAPI backend
        const response = await fetch(`${apiUrl}/api/resumes/${resumeId}/tailor`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ job_id: jobId })
        })

        if (!response.ok) {
            const errorText = await response.text()
            console.error("Backend tailoring error:", errorText)
            return new NextResponse(errorText || "Failed to tailor resume on backend", { status: response.status })
        }

        const pdfBuffer = await response.arrayBuffer()

        // Clean company name for the download filename
        const safeCompany = jobCompany.replace(/[^a-zA-Z0-9_-]/g, '_')
        const filename = `Tailored_Resume_${safeCompany}.pdf`

        // Return the PDF bytes directly as a downloadable response
        // This is the absolute cleanest way to handle downloads in a production environment
        return new NextResponse(pdfBuffer, {
            headers: {
                "Content-Type": "application/pdf",
                "Content-Disposition": `attachment; filename="${filename}"`,
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        })

    } catch (error) {
        console.error("Error in Next.js Tailor Proxy:", error)
        return new NextResponse("Internal Server Error", { status: 500 })
    }
}
