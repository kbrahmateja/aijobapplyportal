"use client"

import { LayoutGrid, List } from "lucide-react"

interface ViewToggleProps {
    view: "grid" | "list"
    onViewChange: (view: "grid" | "list") => void
}

export function ViewToggle({ view, onViewChange }: ViewToggleProps) {
    return (
        <div className="flex items-center gap-2 border rounded-lg p-1">
            <button
                onClick={() => onViewChange("grid")}
                className={`p-2 rounded transition-colors ${view === "grid"
                        ? "bg-blue-100 text-blue-900"
                        : "hover:bg-gray-100"
                    }`}
                aria-label="Grid view"
            >
                <LayoutGrid className="h-5 w-5" />
            </button>
            <button
                onClick={() => onViewChange("list")}
                className={`p-2 rounded transition-colors ${view === "list"
                        ? "bg-blue-100 text-blue-900"
                        : "hover:bg-gray-100"
                    }`}
                aria-label="List view"
            >
                <List className="h-5 w-5" />
            </button>
        </div>
    )
}
