"use client"

import { Search } from "lucide-react"
import { useState, useEffect } from "react"

interface SearchBarProps {
    onSearchChange: (search: string) => void
    placeholder?: string
}

export function SearchBar({ onSearchChange, placeholder = "Search jobs by title, company, or tech..." }: SearchBarProps) {
    const [searchTerm, setSearchTerm] = useState("")

    useEffect(() => {
        // Debounce search - wait 300ms after user stops typing
        const timer = setTimeout(() => {
            onSearchChange(searchTerm)
        }, 300)

        return () => clearTimeout(timer)
    }, [searchTerm, onSearchChange])

    return (
        <div className="relative w-full max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground h-5 w-5" />
            <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={placeholder}
                className="w-full pl-12 pr-4 py-3 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            />
        </div>
    )
}
