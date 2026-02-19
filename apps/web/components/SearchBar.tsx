"use client"

import { Search, X } from "lucide-react"
import { useState, useEffect, useRef } from "react"

const SUGGESTIONS = [
    "Software Engineer",
    "Senior Software Engineer",
    "Frontend Engineer",
    "Backend Engineer",
    "Full Stack Engineer",
    "DevOps Engineer",
    "Site Reliability Engineer",
    "Cloud Engineer",
    "Data Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "Product Manager",
    "Product Designer",
    "UX Designer",
    "UI Designer",
    "React Developer",
    "Python Developer",
    "Node.js Developer",
    "TypeScript",
    "AWS",
    "Kubernetes",
    "Docker",
    "Go",
    "Rust",
    "Java",
    "iOS Developer",
    "Android Developer",
    "Mobile Engineer",
    "Security Engineer",
    "QA Engineer",
    "Blockchain",
    "Web3",
]

interface SearchBarProps {
    onSearchChange: (search: string) => void
    placeholder?: string
}

export function SearchBar({ onSearchChange, placeholder = "Search jobs by title, company, or tech..." }: SearchBarProps) {
    const [searchTerm, setSearchTerm] = useState("")
    const [showSuggestions, setShowSuggestions] = useState(false)
    const [filtered, setFiltered] = useState<string[]>([])
    const containerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const timer = setTimeout(() => {
            onSearchChange(searchTerm)
        }, 300)
        return () => clearTimeout(timer)
    }, [searchTerm, onSearchChange])

    useEffect(() => {
        if (searchTerm.trim().length > 0) {
            const matches = SUGGESTIONS.filter((s) =>
                s.toLowerCase().includes(searchTerm.toLowerCase())
            ).slice(0, 6)
            setFiltered(matches)
            setShowSuggestions(matches.length > 0)
        } else {
            setFiltered([])
            setShowSuggestions(false)
        }
    }, [searchTerm])

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setShowSuggestions(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])

    const handleSelect = (suggestion: string) => {
        setSearchTerm(suggestion)
        setShowSuggestions(false)
        onSearchChange(suggestion)
    }

    const handleClear = () => {
        setSearchTerm("")
        setShowSuggestions(false)
        onSearchChange("")
    }

    return (
        <div ref={containerRef} className="relative w-full max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4 pointer-events-none" />
            <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onFocus={() => filtered.length > 0 && setShowSuggestions(true)}
                placeholder={placeholder}
                className="w-full pl-11 pr-10 py-2.5 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            />
            {searchTerm && (
                <button
                    onClick={handleClear}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    aria-label="Clear search"
                >
                    <X className="h-4 w-4" />
                </button>
            )}

            {/* Autocomplete Dropdown */}
            {showSuggestions && (
                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
                    {filtered.map((suggestion) => (
                        <button
                            key={suggestion}
                            onMouseDown={() => handleSelect(suggestion)}
                            className="w-full text-left px-4 py-2.5 text-sm hover:bg-blue-50 hover:text-blue-700 transition-colors flex items-center gap-2"
                        >
                            <Search className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                            {suggestion}
                        </button>
                    ))}
                </div>
            )}
        </div>
    )
}
