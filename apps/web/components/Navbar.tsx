import Link from "next/link"
import { Button } from "@/components/ui/button"
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

export function Navbar() {
    return (
        <div className="border-b">
            <div className="flex h-16 items-center px-4 container mx-auto">
                <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                    AI Job Copilot
                </Link>
                <div className="ml-auto flex items-center space-x-4">
                    <Link href="/jobs" className="text-sm font-medium transition-colors hover:text-primary">
                        Jobs
                    </Link>
                    <Link href="/dashboard" className="text-sm font-medium transition-colors hover:text-primary">
                        Dashboard
                    </Link>
                    <Link href="/profile" className="text-sm font-medium transition-colors hover:text-primary">
                        Profile
                    </Link>
                    <SignedOut>
                        <SignInButton mode="modal">
                            <Button variant="outline">Sign In</Button>
                        </SignInButton>
                    </SignedOut>
                    <SignedIn>
                        <UserButton afterSignOutUrl="/" />
                    </SignedIn>
                    <Button>Get Standard</Button>
                </div>
            </div>
        </div>
    )
}
