import { NextResponse } from "next/server"
import { auth } from "@clerk/nextjs/server"
import { writeFile, mkdir } from "fs/promises"
import path from "path"
import { v4 as uuidv4 } from "uuid"
import fs from "fs"

export async function POST(request: Request) {
    try {
        const { getToken } = await auth()
        const token = await getToken()

        if (!token) {
            return new NextResponse("Unauthorized", { status: 401 })
        }

        const body = await request.json()
        const { resumeId, jobId, jobCompany } = body

        if (!resumeId || !jobId) {
            return new NextResponse("Missing resumeId or jobId", { status: 400 })
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

        // Fetch the perfectly crafted PDF bytes from our FastAPI backend
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
            return new NextResponse("Failed to tailor resume on backend", { status: response.status })
        }

        const pdfBuffer = await response.arrayBuffer()

        // Clean company name gracefully
        const safeCompany = (jobCompany || "Company").replace(/[^a-zA-Z0-9_-]/g, '_')
        const filename = `Tailored_Resume_${safeCompany}.pdf`

        // Construct public physical save path
        // We omit any UUIDs so the user sees a perfectly clean URL.
        const uniqueFilename = filename
        const downloadsDir = path.join(process.cwd(), "public", "downloads")

        // Ensure directory exists
        if (!fs.existsSync(downloadsDir)) {
            await mkdir(downloadsDir, { recursive: true })
        }

        const filePath = path.join(downloadsDir, uniqueFilename)

        // Give Next.js a moment to physically write the bytes to the hard drive public folder
        await writeFile(filePath, Buffer.from(pdfBuffer))

        // Return the clean identifier and filename
        return NextResponse.json({
            fileId: uniqueFilename,
            filename: filename
        })

    } catch (error) {
        console.error("Error in Next.js Tailor Proxy:", error)
        return new NextResponse("Internal Server Error", { status: 500 })
    }
}
