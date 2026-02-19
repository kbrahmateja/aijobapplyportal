"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

const NAV_LINKS = [
    { href: "/jobs", label: "Jobs" },
    { href: "/dashboard", label: "Dashboard" },
    { href: "/profile", label: "Profile" },
]

export function Navbar() {
    const pathname = usePathname()

    return (
        <div className="border-b bg-white/95 backdrop-blur-sm sticky top-0 z-40">
            <div className="flex h-16 items-center px-4 container mx-auto">
                <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                    AI Job Copilot
                </Link>
                <div className="ml-auto flex items-center space-x-1">
                    {NAV_LINKS.map(({ href, label }) => {
                        const isActive = pathname === href || pathname.startsWith(href + "/")
                        return (
                            <Link
                                key={href}
                                href={href}
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive
                                        ? "text-blue-600 bg-blue-50"
                                        : "text-muted-foreground hover:text-foreground hover:bg-gray-100"
                                    }`}
                            >
                                {label}
                            </Link>
                        )
                    })}
                    <div className="ml-2">
                        <SignedOut>
                            <SignInButton mode="modal">
                                <Button variant="outline" size="sm">Sign In</Button>
                            </SignInButton>
                        </SignedOut>
                        <SignedIn>
                            <UserButton afterSignOutUrl="/" />
                        </SignedIn>
                    </div>
                </div>
            </div>
        </div>
    )
}
