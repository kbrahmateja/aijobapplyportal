"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";

interface Application {
    id: number;
    status: string;
    decision_reason: string | null;
    scheduled_at: string | null;
    job_id: number; // We might want job title too, but let's start simple
    created_at: string;
}

export function ApplicationList() {
    const { getToken } = useAuth();
    const [applications, setApplications] = useState<Application[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchApplications = async () => {
            try {
                const token = await getToken();
                // Use env var or default to localhost
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                const res = await fetch(`${apiUrl}/api/applications/`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error(`Failed to fetch applications: ${res.status} ${errorText}`);
                }

                const data = await res.json();
                setApplications(data);
            } catch (err: any) {
                console.error("Fetch error:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchApplications();
    }, [getToken]);

    if (loading) return <div className="p-4 text-gray-500">Loading applications...</div>;
    if (error) return <div className="p-4 text-red-500 border border-red-200 rounded bg-red-50">Error: {error}</div>;

    return (
        <div className="space-y-4">
            <h2 className="text-xl font-bold">Your Applications</h2>
            {applications.length === 0 ? (
                <div className="p-8 text-center border-2 border-dashed rounded-lg text-gray-400">
                    No applications found. Start applying!
                </div>
            ) : (
                <div className="grid gap-4">
                    {applications.map((app) => (
                        <div key={app.id} className="p-4 border rounded-lg shadow-sm bg-white dark:bg-gray-800 hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start">
                                <div className="space-y-1">
                                    <h3 className="font-semibold text-lg">Application #{app.id}</h3>
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm text-gray-500">Status:</span>
                                        <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase tracking-wide ${getStatusBadge(app.status)}`}>
                                            {app.status}
                                        </span>
                                    </div>
                                    {app.decision_reason && (
                                        <p className="text-sm text-gray-600 dark:text-gray-300 mt-2 bg-gray-50 dark:bg-gray-700/50 p-2 rounded">
                                            {app.decision_reason}
                                        </p>
                                    )}
                                </div>
                                <div className="text-right text-xs text-gray-400 space-y-1">
                                    <p>Created: {new Date(app.created_at).toLocaleDateString()}</p>
                                    {app.scheduled_at && <p>Scheduled: {new Date(app.scheduled_at).toLocaleString()}</p>}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

function getStatusBadge(status: string) {
    switch (status) {
        case 'applied': return 'bg-green-100 text-green-800 border border-green-200';
        case 'queued': return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
        case 'rejected': return 'bg-red-100 text-red-800 border border-red-200';
        default: return 'bg-gray-100 text-gray-800 border border-gray-200';
    }
}
