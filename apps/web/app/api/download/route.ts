import { NextResponse } from "next/server"

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url)
    const downloadUrl = searchParams.get("url")
    const filename = searchParams.get("filename") || "Tailored_Resume.pdf"

    if (!downloadUrl) {
        return new NextResponse("Missing download URL", { status: 400 })
    }

    try {
        const response = await fetch(downloadUrl)

        if (!response.ok) {
            return new NextResponse("Failed to fetch file from backend", { status: response.status })
        }

        const blob = await response.blob()

        // By explicitly returning a NextResponse with the attachment header, Next.js will
        // physically force the browser to trigger a download dialog instead of navigating
        // to the URL, ensuring the filename is absolutely respected natively.
        return new NextResponse(blob, {
            headers: {
                "Content-Disposition": `attachment; filename="${filename}"`,
                "Content-Type": "application/pdf"
            }
        })
    } catch (error) {
        console.error("Error proxying download:", error)
        return new NextResponse("Internal Server Error", { status: 500 })
    }
}
