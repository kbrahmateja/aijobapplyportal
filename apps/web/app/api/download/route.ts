import { NextResponse } from "next/server"

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url)
    const downloadUrl = searchParams.get("url")
    const filename = searchParams.get("filename") || "Tailored_Resume.pdf"

    if (!downloadUrl) {
        return new NextResponse("Missing download URL", { status: 400 })
    }

    try {
        // Fetch the perfectly constructed PDF from the FastAPI backend
        const response = await fetch(downloadUrl)

        if (!response.ok) {
            return new NextResponse("Failed to fetch file from backend", { status: response.status })
        }

        const blob = await response.blob()

        // Return the exactly identical file but from localhost:3000 (same-origin).
        // This physically forces browsers (especially Chrome/Safari) to 100% respect the
        // HTML5 <a download> attribute instead of opening it as a URL navigation.
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
