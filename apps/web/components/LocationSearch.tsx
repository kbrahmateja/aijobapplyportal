"use client"

import { MapPin, X, Loader2 } from "lucide-react"
import { useState, useEffect, useRef } from "react"

interface LocationSearchProps {
    onLocationChange: (location: string | null) => void
    selectedLocation?: string | null
    /** DB locations list — shown as primary suggestions */
    dbLocations?: string[]
}

interface NominatimResult {
    place_id: string
    display_name: string
    address: {
        city?: string
        town?: string
        village?: string
        state?: string
        country?: string
    }
}

function formatNominatim(r: NominatimResult): string {
    const { address } = r
    const city = address.city || address.town || address.village
    const country = address.country
    if (city && country) return `${city}, ${country}`
    if (address.state && country) return `${address.state}, ${country}`
    return r.display_name.split(",").slice(0, 2).join(",").trim()
}

export function LocationSearch({ onLocationChange, selectedLocation, dbLocations = [] }: LocationSearchProps) {
    const [query, setQuery] = useState(selectedLocation || "")
    const [dbMatches, setDbMatches] = useState<string[]>([])
    const [nominatimResults, setNominatimResults] = useState<NominatimResult[]>([])
    const [loading, setLoading] = useState(false)
    const [showDropdown, setShowDropdown] = useState(false)
    const containerRef = useRef<HTMLDivElement>(null)
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    // Sync clear from outside (e.g. "Clear all" in sidebar)
    useEffect(() => {
        if (!selectedLocation) {
            setQuery("")
            setDbMatches([])
            setNominatimResults([])
            setShowDropdown(false)
        }
    }, [selectedLocation])

    // Close on outside click
    useEffect(() => {
        function handleClick(e: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setShowDropdown(false)
            }
        }
        document.addEventListener("mousedown", handleClick)
        return () => document.removeEventListener("mousedown", handleClick)
    }, [])

    const handleInputChange = (value: string) => {
        setQuery(value)

        if (!value.trim()) {
            setDbMatches([])
            setNominatimResults([])
            setShowDropdown(false)
            onLocationChange(null)
            return
        }

        // Immediate DB match (client-side, instant)
        const lower = value.toLowerCase()
        const matches = dbLocations
            .filter(loc => loc.toLowerCase().includes(lower))
            .slice(0, 8)
        setDbMatches(matches)
        setShowDropdown(matches.length > 0)

        // Debounced Nominatim for city-level search (only if not well covered by DB)
        if (debounceRef.current) clearTimeout(debounceRef.current)
        debounceRef.current = setTimeout(async () => {
            setLoading(true)
            try {
                const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(value)}&format=json&addressdetails=1&limit=4`
                const res = await fetch(url, { headers: { "Accept-Language": "en" } })
                if (res.ok) {
                    const data: NominatimResult[] = await res.json()
                    // Deduplicate and exclude labels already covered by DB matches
                    const seen = new Set(matches.map(m => m.toLowerCase()))
                    const unique = data.filter(r => {
                        const label = formatNominatim(r).toLowerCase()
                        if (seen.has(label)) return false
                        seen.add(label)
                        return true
                    })
                    setNominatimResults(unique)
                    setShowDropdown(matches.length > 0 || unique.length > 0)
                }
            } catch {
                // network fail — DB results still shown
            } finally {
                setLoading(false)
            }
        }, 400)
    }

    const handleSelectDB = (loc: string) => {
        setQuery(loc)
        setShowDropdown(false)
        onLocationChange(loc)
    }

    const handleSelectNominatim = (r: NominatimResult) => {
        const label = formatNominatim(r)
        setQuery(label)
        setShowDropdown(false)
        onLocationChange(label)
    }

    const handleClear = () => {
        setQuery("")
        setDbMatches([])
        setNominatimResults([])
        setShowDropdown(false)
        onLocationChange(null)
    }

    const hasResults = dbMatches.length > 0 || nominatimResults.length > 0

    return (
        <div ref={containerRef} className="relative w-full">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <input
                type="text"
                value={query}
                onChange={(e) => handleInputChange(e.target.value)}
                onFocus={() => hasResults && setShowDropdown(true)}
                placeholder="Location..."
                className="w-full pl-9 pr-8 py-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all bg-white"
            />
            {loading && (
                <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground animate-spin" />
            )}
            {query && !loading && (
                <button
                    onClick={handleClear}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    aria-label="Clear"
                >
                    <X className="h-4 w-4" />
                </button>
            )}

            {/* Dropdown */}
            {showDropdown && hasResults && (
                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden max-h-72 overflow-y-auto">
                    {/* DB locations — these always work for filtering */}
                    {dbMatches.length > 0 && (
                        <>
                            <div className="px-3 py-1 text-xs text-muted-foreground bg-gray-50 border-b font-medium">
                                Available in database
                            </div>
                            {dbMatches.map((loc) => (
                                <button
                                    key={`db-${loc}`}
                                    onMouseDown={() => handleSelectDB(loc)}
                                    className="w-full text-left px-4 py-2 hover:bg-blue-50 hover:text-blue-700 transition-colors flex items-center gap-2 text-sm"
                                >
                                    <MapPin className="h-3.5 w-3.5 text-blue-500 flex-shrink-0" />
                                    {loc}
                                </button>
                            ))}
                        </>
                    )}

                    {/* Nominatim results — additional city/country search */}
                    {nominatimResults.length > 0 && (
                        <>
                            <div className="px-3 py-1 text-xs text-muted-foreground bg-gray-50 border-b font-medium">
                                Search globally
                            </div>
                            {nominatimResults.map((r) => {
                                const label = formatNominatim(r)
                                const subLabel = r.display_name.split(",").slice(1, 3).join(",").trim()
                                return (
                                    <button
                                        key={`osm-${r.place_id}`}
                                        onMouseDown={() => handleSelectNominatim(r)}
                                        className="w-full text-left px-4 py-2 hover:bg-blue-50 hover:text-blue-700 transition-colors flex items-start gap-2 text-sm"
                                    >
                                        <MapPin className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0 mt-0.5" />
                                        <div>
                                            <div className="font-medium">{label}</div>
                                            {subLabel && <div className="text-xs text-muted-foreground">{subLabel}</div>}
                                        </div>
                                    </button>
                                )
                            })}
                        </>
                    )}

                    <div className="px-3 py-1 bg-gray-50 border-t text-xs text-muted-foreground">
                        Powered by OpenStreetMap
                    </div>
                </div>
            )}
        </div>
    )
}
