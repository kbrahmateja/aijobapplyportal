"use client"

import { useEffect, useState } from "react"
import { JobCard } from "@/components/JobCard"
import { SearchBar } from "@/components/SearchBar"
import { FilterSidebar } from "@/components/FilterSidebar"
import { ViewToggle } from "@/components/ViewToggle"
import { Loader2 } from "lucide-react"
import { useAuth } from "@clerk/nextjs"

interface Job {
    id: number
    title: string
    company: string
    location: string | null
    description: string | null
    url: string
    source: string
    posted_at: string
}

interface JobListResponse {
    jobs: Job[]
    total: number
    page: number
    limit: number
    total_pages: number
}

interface FiltersData {
    categories: string[]
    locations: string[]
    sources: string[]
    total_jobs: number
}

export default function JobsPage() {
    const { getToken, userId } = useAuth()
    const [jobs, setJobs] = useState<Job[]>([])
    const [defaultResumeId, setDefaultResumeId] = useState<number | null>(null)
    const [loading, setLoading] = useState(true)

    // View state
    const [viewMode, setViewMode] = useState<"grid" | "list">("grid")

    // Filter states
    const [searchTerm, setSearchTerm] = useState("")
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
    const [selectedLocation, setSelectedLocation] = useState<string | null>(null)
    const [selectedSource, setSelectedSource] = useState<string | null>(null)

    // Pagination states
    const [currentPage, setCurrentPage] = useState(1)
    const [totalPages, setTotalPages] = useState(1)
    const [totalJobs, setTotalJobs] = useState(0)

    // Filters metadata
    const [filtersData, setFiltersData] = useState<FiltersData>({
        categories: [],
        locations: [],
        sources: [],
        total_jobs: 0
    })

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

    // Fetch filters metadata on mount
    useEffect(() => {
        async function fetchFilters() {
            try {
                const res = await fetch(`${apiUrl}/api/jobs/filters`)
                if (res.ok) {
                    const data = await res.json()
                    setFiltersData(data)
                }
            } catch (error) {
                console.error("Error fetching filters:", error)
            }
        }
        fetchFilters()
    }, [apiUrl])

    // Fetch jobs when filters or page changes
    useEffect(() => {
        async function fetchJobs() {
            console.log('[Jobs] Fetching jobs for page:', currentPage)
            setLoading(true)

            // Scroll to top when filters change (but NOT on pagination change)
            // This ensures filtered results are visible, especially for single results
            if (currentPage === 1) {
                window.scrollTo({ top: 0, behavior: 'smooth' })
            }

            try {
                const params = new URLSearchParams()
                params.append("page", currentPage.toString())
                params.append("limit", "20")

                if (searchTerm) params.append("search", searchTerm)
                if (selectedLocation) params.append("location", selectedLocation)
                if (selectedSource) params.append("source", selectedSource)
                if (selectedCategory && selectedCategory !== "All") {
                    params.append("search", selectedCategory)
                }

                console.log('[Jobs] API call:', `${apiUrl}/api/jobs/?${params.toString()}`)
                const jobsRes = await fetch(`${apiUrl}/api/jobs/?${params.toString()}`)
                if (jobsRes.ok) {
                    const data: JobListResponse = await jobsRes.json()
                    console.log('[Jobs] Received data:', { page: data.page, total: data.total, jobs: data.jobs.length })
                    setJobs(data.jobs)
                    setTotalPages(data.total_pages)
                    setTotalJobs(data.total)
                } else {
                    console.error("Failed to fetch jobs:", jobsRes.status)
                }
            } catch (error) {
                console.error("Error fetching jobs:", error)
            } finally {
                setLoading(false)
            }
        }

        fetchJobs()
    }, [searchTerm, selectedLocation, selectedSource, selectedCategory, currentPage, apiUrl])

    // Fetch default resume
    useEffect(() => {
        async function fetchDefaultResume() {
            if (!userId) return

            try {
                const token = await getToken()
                const resumesRes = await fetch(`${apiUrl}/api/resumes`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
                if (resumesRes.ok) {
                    const resumesData = await resumesRes.json()
                    const defaultResume = resumesData.find((r: any) => r.is_default) || resumesData[0]
                    if (defaultResume) {
                        setDefaultResumeId(defaultResume.id)
                    }
                }
            } catch (error) {
                console.error("Error fetching default resume:", error)
            }
        }
        fetchDefaultResume()
    }, [userId, getToken, apiUrl])

    // Reset to page 1 when filters change
    const handleFilterChange = (callback: () => void) => {
        setCurrentPage(1)
        callback()
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Sticky Header with Search */}
            <div className="sticky top-0 z-20 bg-white shadow-sm border-b">
                <div className="container mx-auto py-6 px-4">
                    <h1 className="text-4xl font-bold mb-4 text-center bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                        Job Discovery
                    </h1>

                    {/* Search Bar */}
                    <div className="mb-4">
                        <SearchBar onSearchChange={(search) => {
                            console.log('[SearchBar] Search changed to:', search)
                            if (search !== searchTerm) {
                                setCurrentPage(1)
                                setSearchTerm(search)
                            }
                        }} />
                    </div>

                    {/* Stats and View Toggle */}
                    <div className="flex justify-between items-center">
                        <div className="text-muted-foreground">
                            {loading ? (
                                <p>Loading...</p>
                            ) : (
                                <p>
                                    Showing {jobs.length} of {totalJobs} jobs
                                    {searchTerm && ` for "${searchTerm}"`}
                                </p>
                            )}
                        </div>
                        <ViewToggle view={viewMode} onViewChange={setViewMode} />
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="container mx-auto py-6 px-4">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Sticky Filters Sidebar */}
                    <div className="lg:col-span-1">
                        <div className="sticky top-[280px]">
                            <FilterSidebar
                                categories={filtersData.categories}
                                locations={filtersData.locations}
                                sources={filtersData.sources}
                                selectedCategory={selectedCategory}
                                selectedLocation={selectedLocation}
                                selectedSource={selectedSource}
                                onCategoryChange={(cat) => handleFilterChange(() => setSelectedCategory(cat))}
                                onLocationChange={(loc) => handleFilterChange(() => setSelectedLocation(loc))}
                                onSourceChange={(src) => handleFilterChange(() => setSelectedSource(src))}
                            />
                        </div>
                    </div>

                    {/* Jobs Display Area */}
                    <div className="lg:col-span-3">
                        {loading ? (
                            <div className="flex justify-center items-center py-20">
                                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                            </div>
                        ) : jobs.length === 0 ? (
                            <div className="text-center py-20 text-muted-foreground bg-white rounded-lg">
                                <p className="text-xl mb-2">No jobs found</p>
                                <p>Try adjusting your filters or search terms</p>
                            </div>
                        ) : (
                            <>
                                {/* Jobs Grid or List View */}
                                <div className={
                                    viewMode === "grid"
                                        ? "grid grid-cols-1 md:grid-cols-2 gap-6"
                                        : "flex flex-col gap-4"
                                }>
                                    {jobs.map((job) => (
                                        <JobCard
                                            key={job.id}
                                            job={job}
                                            defaultResumeId={defaultResumeId}
                                            viewMode={viewMode}
                                        />
                                    ))}
                                </div>

                                {/* Pagination */}
                                {totalPages > 1 && (
                                    <div className="mt-8 flex justify-center items-center gap-4">
                                        <button
                                            onClick={() => {
                                                console.log('[Pagination] Previous clicked, current page:', currentPage)
                                                setCurrentPage(p => {
                                                    const newPage = Math.max(1, p - 1)
                                                    console.log('[Pagination] Setting page to:', newPage)
                                                    return newPage
                                                })
                                            }}
                                            disabled={currentPage === 1}
                                            className="px-6 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 transition-colors font-medium"
                                        >
                                            Previous
                                        </button>
                                        <div className="flex items-center gap-2">
                                            <span className="px-4 py-2 font-medium">
                                                Page {currentPage} of {totalPages}
                                            </span>
                                        </div>
                                        <button
                                            onClick={() => {
                                                console.log('[Pagination] Next clicked, current page:', currentPage, 'total pages:', totalPages)
                                                setCurrentPage(p => {
                                                    const newPage = Math.min(totalPages, p + 1)
                                                    console.log('[Pagination] Setting page to:', newPage)
                                                    return newPage
                                                })
                                            }}
                                            disabled={currentPage === totalPages}
                                            className="px-6 py2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 transition-colors font-medium"
                                        >
                                            Next
                                        </button>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
