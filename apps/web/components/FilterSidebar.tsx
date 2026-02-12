"use client"

import { X } from "lucide-react"

interface FilterChipProps {
    label: string
    onRemove: () => void
}

export function FilterChip({ label, onRemove }: FilterChipProps) {
    return (
        <div className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            {label}
            <button
                onClick={onRemove}
                className="hover:bg-blue-200 rounded-full p-0.5 transition-colors"
                aria-label={`Remove ${label} filter`}
            >
                <X className="h-3 w-3" />
            </button>
        </div>
    )
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
    return (
        <div className="space-y-6 p-4 bg-white rounded-lg border">
            <div>
                <h3 className="font-semibold mb-3 text-lg">Filters</h3>

                {/* Active Filters */}
                {(selectedLocation || selectedSource || selectedCategory) && (
                    <div className="mb-4 flex flex-wrap gap-2">
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
            </div>

            {/* Category Filter */}
            <div>
                <h4 className="font-medium mb-2">Category</h4>
                <div className="space-y-1">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => onCategoryChange(cat === selectedCategory ? null : cat)}
                            className={`w-full text-left px-3 py-2 rounded-md transition-colors ${selectedCategory === cat
                                    ? "bg-blue-100 text-blue-900 font-medium"
                                    : "hover:bg-gray-100"
                                }`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>
            </div>

            {/* Location Filter */}
            <div>
                <h4 className="font-medium mb-2">Location</h4>
                <select
                    value={selectedLocation || ""}
                    onChange={(e) => onLocationChange(e.target.value || null)}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 outline-none"
                >
                    <option value="">All Locations</option>
                    {locations.map((loc) => (
                        <option key={loc} value={loc}>
                            {loc}
                        </option>
                    ))}
                </select>
            </div>

            {/* Source Filter */}
            <div>
                <h4 className="font-medium mb-2">Job Board</h4>
                <div className="space-y-1">
                    {sources.map((src) => (
                        <button
                            key={src}
                            onClick={() => onSourceChange(src === selectedSource ? null : src)}
                            className={`w-full text-left px-3 py-2 rounded-md transition-colors ${selectedSource === src
                                    ? "bg-blue-100 text-blue-900 font-medium"
                                    : "hover:bg-gray-100"
                                }`}
                        >
                            {src}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
}
