"use client"

import { X } from "lucide-react"

interface FilterChipProps {
    label: string
    onRemove: () => void
}

export function FilterChip({ label, onRemove }: FilterChipProps) {
    return (
        <div className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
            {label}
            <button
                onClick={onRemove}
                className="hover:bg-blue-200 rounded-full p-0.5 transition-colors"
                aria-label={`Remove ${label} filter`}
            >
                <X className="h-2.5 w-2.5" />
            </button>
        </div>
    )
}

const SOURCE_COLORS: Record<string, string> = {
    WeWorkRemotely: "bg-green-50 text-green-700 border-green-200",
    RemoteOK: "bg-red-50 text-red-700 border-red-200",
    Remotive: "bg-purple-50 text-purple-700 border-purple-200",
}

interface FilterSidebarProps {
    sources: string[]
    categories: string[]
    selectedSource: string | null
    selectedCategory: string | null
    // kept for API compat — not displayed in sidebar (location is in header)
    locations?: string[]
    selectedLocation?: string | null
    onLocationChange?: (location: string | null) => void
    onSourceChange: (source: string | null) => void
    onCategoryChange: (category: string | null) => void
}

export function FilterSidebar({
    sources,
    categories,
    selectedSource,
    selectedCategory,
    onSourceChange,
    onCategoryChange,
}: FilterSidebarProps) {
    const hasActiveFilters = selectedSource || selectedCategory

    return (
        <div className="space-y-3 p-3 bg-white rounded-lg border text-sm">
            <div className="flex items-center justify-between">
                <h3 className="font-semibold">Filters</h3>
                {hasActiveFilters && (
                    <button
                        onClick={() => { onCategoryChange(null); onSourceChange(null) }}
                        className="text-xs text-blue-600 hover:underline"
                    >
                        Clear all
                    </button>
                )}
            </div>

            {/* Active Filters chips */}
            {hasActiveFilters && (
                <div className="flex flex-wrap gap-1.5">
                    {selectedCategory && (
                        <FilterChip label={selectedCategory} onRemove={() => onCategoryChange(null)} />
                    )}
                    {selectedSource && (
                        <FilterChip label={selectedSource} onRemove={() => onSourceChange(null)} />
                    )}
                </div>
            )}

            {/* Category — horizontal chips */}
            <div>
                <h4 className="font-medium text-xs text-muted-foreground uppercase tracking-wider mb-2">Category</h4>
                <div className="flex flex-wrap gap-1.5">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => onCategoryChange(cat === selectedCategory ? null : cat)}
                            className={`px-2.5 py-1 rounded-full text-xs border transition-colors ${selectedCategory === cat
                                    ? "bg-blue-600 text-white border-blue-600"
                                    : "bg-white border-gray-200 hover:border-blue-400 hover:text-blue-600"
                                }`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>
            </div>

            {/* Source — colored pills */}
            <div>
                <h4 className="font-medium text-xs text-muted-foreground uppercase tracking-wider mb-2">Job Board</h4>
                <div className="flex flex-col gap-1">
                    {sources.map((src) => {
                        const color = SOURCE_COLORS[src] || "bg-blue-50 text-blue-700 border-blue-200"
                        return (
                            <button
                                key={src}
                                onClick={() => onSourceChange(src === selectedSource ? null : src)}
                                className={`w-full text-left px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all ${selectedSource === src
                                        ? `${color} ring-1 ring-offset-1 ring-current`
                                        : "bg-white border-gray-200 hover:border-gray-300"
                                    }`}
                            >
                                {src}
                            </button>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}
