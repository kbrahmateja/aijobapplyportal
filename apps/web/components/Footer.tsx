import Link from "next/link"

export function Footer() {
    return (
        <footer className="bg-gray-950 text-gray-300 mt-auto">
            <div className="container mx-auto px-4 py-10">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Brand */}
                    <div>
                        <div className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                            AI Job Copilot
                        </div>
                        <p className="text-sm text-gray-400">
                            AI-powered job discovery and application automation. Updated daily from top remote job boards.
                        </p>
                    </div>

                    {/* Links */}
                    <div>
                        <h4 className="font-semibold text-sm text-white mb-3">Navigation</h4>
                        <div className="flex flex-col gap-2 text-sm">
                            <Link href="/jobs" className="hover:text-white transition-colors">Browse Jobs</Link>
                            <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
                            <Link href="/profile" className="hover:text-white transition-colors">Profile</Link>
                        </div>
                    </div>

                    {/* Job Sources */}
                    <div>
                        <h4 className="font-semibold text-sm text-white mb-3">Job Sources</h4>
                        <div className="flex flex-wrap gap-2">
                            {["RemoteOK", "WeWorkRemotely", "Remotive"].map((source) => (
                                <span
                                    key={source}
                                    className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs font-medium border border-blue-800"
                                >
                                    {source}
                                </span>
                            ))}
                        </div>
                        <p className="text-xs text-gray-500 mt-2">More sources added regularly</p>
                    </div>
                </div>

                <div className="border-t border-gray-800 mt-8 pt-4 text-center text-xs text-gray-500">
                    © 2026 AI Job Copilot. All rights reserved. Jobs updated daily at 2 AM UTC.
                </div>
            </div>
        </footer>
    )
}
