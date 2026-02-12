import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle2, Bot, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="py-20 px-4 text-center space-y-8 bg-gradient-to-b from-background to-muted/20">
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
          Your AI <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">Job Application</span> Copilot
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Stop applying manually. Let our AI agents find, tailor, and apply to thousands of jobs for you.
          Human-like precision at machine speed.
        </p>
        <div className="flex justify-center gap-4">
          <Button size="lg" asChild>
            <Link href="/jobs">
              Find Jobs Now <ArrowRight className="ml-2 w-4 h-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline">
            View Demo
          </Button>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 container mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="p-6 rounded-2xl border bg-card text-card-foreground shadow-sm">
            <Bot className="w-12 h-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">Smart Discovery</h3>
            <p className="text-muted-foreground">
              Our agents scour hidden job boards and aggregators to find roles that perfectly match your profile.
            </p>
          </div>
          <div className="p-6 rounded-2xl border bg-card text-card-foreground shadow-sm">
            <Sparkles className="w-12 h-12 text-purple-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">Resume Tailoring</h3>
            <p className="text-muted-foreground">
              We rewrite your resume for every single application to pass ATS filters and impress recruiters.
            </p>
          </div>
          <div className="p-6 rounded-2xl border bg-card text-card-foreground shadow-sm">
            <CheckCircle2 className="w-12 h-12 text-green-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">Auto-Apply</h3>
            <p className="text-muted-foreground">
              From "Easy Apply" to complex forms, our browser agents handle the tedious work for you.
            </p>
          </div>
        </div>
      </section>

      <footer className="py-10 text-center text-sm text-muted-foreground border-t">
        © 2026 AI Job Copilot. All rights reserved.
      </footer>
    </div>
  );
}
