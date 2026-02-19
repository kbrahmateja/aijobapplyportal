"use client"

import { MapPin, X, Loader2 } from "lucide-react"
import { useState, useEffect, useRef } from "react"

interface NominatimResult {
    place_id: string
    display_name: string
    type: string
    address: {
        city?: string
        town?: string
        village?: string
        county?: string
        state?: string
        country?: string
    }
}

interface LocationSearchProps {
    onLocationChange: (location: string | null) => void
    selectedLocation?: string | null
}

function formatLocation(result: NominatimResult): string {
    const { address } = result
    const city = address.city || address.town || address.village
    const state = address.state
    const country = address.country

    if (city && country) return `${city}, ${country}`
    if (state && country) return `${state}, ${country}`
    if (country) return country
    return result.display_name.split(",").slice(0, 2).join(",").trim()
}

export function LocationSearch({ onLocationChange, selectedLocation }: LocationSearchProps) {
    const [query, setQuery] = useState(selectedLocation || "")
    const [suggestions, setSuggestions] = useState<NominatimResult[]>([])
    const [loading, setLoading] = useState(false)
    const [showDropdown, setShowDropdown] = useState(false)
    const [selectedLabel, setSelectedLabel] = useState(selectedLocation || "")
    const containerRef = useRef<HTMLDivElement>(null)
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    // Sync with external selectedLocation changes (e.g. "Clear all")
    useEffect(() => {
        if (!selectedLocation) {
            setQuery("")
            setSelectedLabel("")
        }
    }, [selectedLocation])

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setShowDropdown(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])

    const handleInputChange = (value: string) => {
        setQuery(value)
        setSelectedLabel("")

        if (debounceRef.current) clearTimeout(debounceRef.current)

        if (value.trim().length < 2) {
            setSuggestions([])
            setShowDropdown(false)
            if (value === "") onLocationChange(null)
            return
        }

        debounceRef.current = setTimeout(async () => {
            setLoading(true)
            try {
                const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(value)}&format=json&addressdetails=1&limit=6&featuretype=city`
                const res = await fetch(url, {
                    headers: { "Accept-Language": "en" }
                })
                if (res.ok) {
                    const data: NominatimResult[] = await res.json()
                    // Deduplicate by formatted label
                    const seen = new Set<string>()
                    const unique = data.filter(r => {
                        const label = formatLocation(r)
                        if (seen.has(label)) return false
                        seen.add(label)
                        return true
                    })
                    setSuggestions(unique)
                    setShowDropdown(unique.length > 0)
                }
            } catch {
                // Nominatim failed, show no suggestions
            } finally {
                setLoading(false)
            }
        }, 400)
    }

    const handleSelect = (result: NominatimResult) => {
        const label = formatLocation(result)
        setQuery(label)
        setSelectedLabel(label)
        setSuggestions([])
        setShowDropdown(false)
        onLocationChange(label)
    }

    const handleClear = () => {
        setQuery("")
        setSelectedLabel("")
        setSuggestions([])
        setShowDropdown(false)
        onLocationChange(null)
    }

    return (
        <div ref={containerRef} className="relative w-full">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <input
                type="text"
                value={query}
                onChange={(e) => handleInputChange(e.target.value)}
                onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
                placeholder="City or country..."
                className="w-full pl-9 pr-8 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all bg-white"
            />
            {loading && (
                <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground animate-spin" />
            )}
            {query && !loading && (
                <button
                    onClick={handleClear}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    aria-label="Clear location"
                >
                    <X className="h-4 w-4" />
                </button>
            )}

            {/* Dropdown */}
            {showDropdown && suggestions.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
                    {suggestions.map((result) => {
                        const label = formatLocation(result)
                        const subLabel = result.display_name.split(",").slice(1, 3).join(",").trim()
                        return (
                            <button
                                key={result.place_id}
                                onMouseDown={() => handleSelect(result)}
                                className="w-full text-left px-4 py-2.5 hover:bg-blue-50 hover:text-blue-700 transition-colors flex items-start gap-2.5"
                            >
                                <MapPin className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0 mt-0.5" />
                                <div>
                                    <div className="text-sm font-medium">{label}</div>
                                    {subLabel && (
                                        <div className="text-xs text-muted-foreground truncate max-w-[280px]">{subLabel}</div>
                                    )}
                                </div>
                            </button>
                        )
                    })}
                    <div className="px-4 py-1.5 bg-gray-50 border-t flex items-center gap-1.5">
                        <svg viewBox="0 0 256 256" className="h-3 w-3 text-muted-foreground" fill="currentColor">
                            <path d="M128,16a112,112,0,1,0,112,112A112.12,112.12,0,0,0,128,16Zm0,208a96,96,0,1,1,96-96A96.11,96.11,0,0,1,128,224Z" />
                        </svg>
                        <span className="text-xs text-muted-foreground">Powered by OpenStreetMap</span>
                    </div>
                </div>
            )}
        </div>
    )
}
