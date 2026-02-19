"use client"

import { useEffect, useState, useRef } from "react"
import Link from "next/link"
import { ArrowRight, Bot, Sparkles, CheckCircle2, TrendingUp, Globe, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

const JOB_SOURCES = [
  { name: "RemoteOK", color: "bg-red-50 text-red-700 border-red-200" },
  { name: "WeWorkRemotely", color: "bg-green-50 text-green-700 border-green-200" },
  { name: "Remotive", color: "bg-purple-50 text-purple-700 border-purple-200" },
]

const HOW_IT_WORKS = [
  {
    icon: <Globe className="w-8 h-8 text-blue-500" />,
    step: "01",
    title: "We Scrape Daily",
    desc: "Our bots pull fresh jobs every night from 3+ job boards — RemoteOK, WeWorkRemotely, Remotive and more."
  },
  {
    icon: <Sparkles className="w-8 h-8 text-purple-500" />,
    step: "02",
    title: "AI Tailors Your Resume",
    desc: "Upload your base resume once. Our AI rewrites it for every job to pass ATS filters."
  },
  {
    icon: <CheckCircle2 className="w-8 h-8 text-emerald-500" />,
    step: "03",
    title: "Auto-Apply",
    desc: "Our browser agent fills forms and submits applications — while you sleep."
  },
]

/** Animates a number from 0 to `target` over `duration` ms */
function useCountUp(target: number | null, duration = 1200) {
  const [count, setCount] = useState(0)
  const rafRef = useRef<number | null>(null)

  useEffect(() => {
    if (target === null || target === 0) return
    const start = performance.now()
    const animate = (now: number) => {
      const elapsed = now - start
      const progress = Math.min(elapsed / duration, 1)
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.round(eased * target))
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate)
      }
    }
    rafRef.current = requestAnimationFrame(animate)
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [target, duration])

  return count
}

export default function Home() {
  const [totalJobs, setTotalJobs] = useState<number | null>(null)
  const [topCompanies, setTopCompanies] = useState<string[]>([])
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  const animatedCount = useCountUp(totalJobs)

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch(`${apiUrl}/api/jobs/filters`)
        if (res.ok) {
          const data = await res.json()
          setTotalJobs(data.total_jobs)
        }
      } catch (e) {
        // silently fail
      }
    }
    async function fetchTopCompanies() {
      try {
        const res = await fetch(`${apiUrl}/api/jobs/?limit=100&page=1`)
        if (res.ok) {
          const data = await res.json()
          const countMap: Record<string, number> = {}
          for (const job of data.jobs) {
            if (job.company && job.company !== "Unknown") {
              countMap[job.company] = (countMap[job.company] || 0) + 1
            }
          }
          const sorted = Object.entries(countMap)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 12)
            .map(([name]) => name)
          setTopCompanies(sorted)
        }
      } catch (e) {
        // silently fail
      }
    }
    fetchStats()
    fetchTopCompanies()
  }, [apiUrl])

  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="py-24 px-4 text-center relative overflow-hidden bg-gradient-to-br from-blue-600/10 via-cyan-50/40 to-background">
        {/* Decorative blobs */}
        <div className="pointer-events-none absolute -top-32 -left-32 w-96 h-96 rounded-full bg-blue-400/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 -right-24 w-80 h-80 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="max-w-3xl mx-auto space-y-6 relative">
          {/* Live stats badge with count-up */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium shadow-sm">
            <RefreshCw className="w-3.5 h-3.5 animate-spin [animation-duration:3s]" />
            {totalJobs !== null
              ? <><span className="font-bold">{animatedCount.toLocaleString()}+</span> live jobs</>
              : "Loading jobs..."
            } · Updated daily
          </div>

          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight leading-tight">
            Your AI{" "}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Job Application
            </span>{" "}
            Copilot
          </h1>

          <p className="text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed">
            Stop applying manually. Our AI agents find, tailor, and apply to thousands of remote jobs for you — every day.
          </p>

          <div className="flex justify-center gap-3 pt-2">
            <Button size="lg" asChild className="shadow-lg shadow-blue-500/20">
              <Link href="/jobs">
                Browse Jobs <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </Button>
          </div>

          {/* Job Sources strip */}
          <div className="pt-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider mb-3">Sourced from</p>
            <div className="flex justify-center flex-wrap gap-2">
              {JOB_SOURCES.map((s) => (
                <span
                  key={s.name}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border ${s.color}`}
                >
                  {s.name}
                </span>
              ))}
              <span className="px-3 py-1.5 rounded-full text-sm font-medium border bg-gray-50 text-gray-500 border-gray-200">
                + more soon
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="border-y bg-white py-6 px-4">
        <div className="container mx-auto grid grid-cols-3 gap-4 text-center max-w-2xl">
          <div>
            <div className="text-2xl font-bold text-blue-600">{totalJobs ? `${animatedCount.toLocaleString()}+` : "—"}</div>
            <div className="text-sm text-muted-foreground">Live Jobs</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">3</div>
            <div className="text-sm text-muted-foreground">Job Boards</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">Daily</div>
            <div className="text-sm text-muted-foreground">Auto-Refresh</div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16 container mx-auto px-4">
        <h2 className="text-2xl font-bold text-center mb-10">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {HOW_IT_WORKS.map((item) => (
            <div key={item.step} className="p-6 rounded-2xl border bg-card shadow-sm relative hover:shadow-md transition-shadow">
              <div className="text-xs font-bold text-muted-foreground/30 absolute top-4 right-5 text-5xl select-none">{item.step}</div>
              <div className="mb-3">{item.icon}</div>
              <h3 className="text-lg font-bold mb-1">{item.title}</h3>
              <p className="text-sm text-muted-foreground">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Top Companies (dynamic) */}
      {topCompanies.length > 0 && (
        <section className="py-10 bg-gray-50 px-4">
          <div className="container mx-auto">
            <div className="flex items-center gap-2 mb-5">
              <TrendingUp className="w-4 h-4 text-blue-600" />
              <h2 className="text-base font-semibold">Top Hiring Companies Right Now</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {topCompanies.map((company) => (
                <Link
                  key={company}
                  href={`/jobs?search=${encodeURIComponent(company)}`}
                  className="px-3 py-1.5 bg-white border rounded-full text-sm hover:border-blue-400 hover:text-blue-600 transition-colors"
                >
                  {company}
                </Link>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-3">* Based on current jobs in database. Updated daily.</p>
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="py-16 text-center px-4">
        <h2 className="text-2xl font-bold mb-3">Ready to automate your job search?</h2>
        <p className="text-muted-foreground mb-6">Browse {totalJobs ? `${totalJobs.toLocaleString()}+` : "hundreds of"} remote jobs or sign in to start AI-applying.</p>
        <div className="flex justify-center gap-3">
          <Button size="lg" asChild>
            <Link href="/jobs">Find Jobs Now <ArrowRight className="ml-2 w-4 h-4" /></Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
