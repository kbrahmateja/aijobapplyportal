"use client"

import { X, ChevronDown, ChevronUp } from "lucide-react"
import { useState } from "react"

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
    locations: string[]
    sources: string[]
    categories: string[]
    selectedLocation: string | null
    selectedSource: string | null
    selectedCategory: string | null
    onLocationChange: (location: string | null) => void
    onSourceChange: (source: string | null) => void
    onCategoryChange: (category: string | null) => void
}

export function FilterSidebar({
    locations,
    sources,
    categories,
    selectedLocation,
    selectedSource,
    selectedCategory,
    onLocationChange,
    onSourceChange,
    onCategoryChange
}: FilterSidebarProps) {
    const [showAllLocations, setShowAllLocations] = useState(false)
    const visibleLocations = showAllLocations ? locations : locations.slice(0, 8)

    const hasActiveFilters = selectedLocation || selectedSource || selectedCategory

    return (
        <div className="space-y-4 p-3 bg-white rounded-lg border text-sm">
            <div className="flex items-center justify-between">
                <h3 className="font-semibold">Filters</h3>
                {hasActiveFilters && (
                    <button
                        onClick={() => { onCategoryChange(null); onLocationChange(null); onSourceChange(null) }}
                        className="text-xs text-blue-600 hover:underline"
                    >
                        Clear all
                    </button>
                )}
            </div>

            {/* Active Filters */}
            {hasActiveFilters && (
                <div className="flex flex-wrap gap-1.5">
                    {selectedCategory && (
                        <FilterChip label={selectedCategory} onRemove={() => onCategoryChange(null)} />
                    )}
                    {selectedLocation && (
                        <FilterChip label={selectedLocation} onRemove={() => onLocationChange(null)} />
                    )}
                    {selectedSource && (
                        <FilterChip label={selectedSource} onRemove={() => onSourceChange(null)} />
                    )}
                </div>
            )}

            {/* Category Filter — horizontal chips */}
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

            {/* Source Filter — colored pills */}
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

            {/* Location Filter */}
            <div>
                <h4 className="font-medium text-xs text-muted-foreground uppercase tracking-wider mb-2">Location</h4>
                <div className="flex flex-col gap-1">
                    <button
                        onClick={() => onLocationChange(null)}
                        className={`w-full text-left px-2.5 py-1 rounded text-xs transition-colors ${!selectedLocation ? "font-semibold text-blue-600" : "text-muted-foreground hover:text-foreground"
                            }`}
                    >
                        All Locations
                    </button>
                    {visibleLocations.map((loc) => (
                        <button
                            key={loc}
                            onClick={() => onLocationChange(loc === selectedLocation ? null : loc)}
                            className={`w-full text-left px-2.5 py-1 rounded text-xs transition-colors truncate ${selectedLocation === loc
                                    ? "font-semibold text-blue-600"
                                    : "text-muted-foreground hover:text-foreground"
                                }`}
                        >
                            {loc}
                        </button>
                    ))}
                    {locations.length > 8 && (
                        <button
                            onClick={() => setShowAllLocations(!showAllLocations)}
                            className="flex items-center gap-1 text-xs text-blue-600 hover:underline px-2.5 py-1"
                        >
                            {showAllLocations ? (
                                <><ChevronUp className="h-3 w-3" /> Show less</>
                            ) : (
                                <><ChevronDown className="h-3 w-3" /> +{locations.length - 8} more</>
                            )}
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}
