import { NextResponse } from "next/server"
import { readFile } from "fs/promises"
import path from "path"
import fs from "fs"

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url)
        const fileId = searchParams.get("fileId")

        if (!fileId) {
            return new NextResponse("Missing fileId", { status: 400 })
        }

        // Use the same directory as the tailor-resume route
        const filePath = path.join(process.cwd(), "public", "downloads", fileId)

        if (!fs.existsSync(filePath)) {
            return new NextResponse("File not found", { status: 404 })
        }

        const fileBuffer = await readFile(filePath)

        // Force a specific, clean filename in the header
        // We use the fileId itself which we already cleaned in the previous step
        const response = new NextResponse(fileBuffer)

        response.headers.set("Content-Type", "application/pdf")
        response.headers.set("Content-Disposition", `attachment; filename="${fileId}"`)
        response.headers.set("Cache-Control", "no-cache, no-store, must-revalidate")

        return response

    } catch (error) {
        console.error("Error in Next.js Download Proxy:", error)
        return new NextResponse("Internal Server Error", { status: 500 })
    }
}
